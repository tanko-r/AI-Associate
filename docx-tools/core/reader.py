"""
Read and parse .docx files into structured dicts.

Adapted from Ambrose's document_service.py. Extracts paragraphs with IDs,
section hierarchy, defined terms, and metadata.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def get_paragraph_style_info(paragraph) -> Dict[str, Any]:
    """Extract style information from a paragraph."""
    style_name = paragraph.style.name if paragraph.style else "Normal"
    numbering_info = None
    if paragraph._p.pPr is not None:
        numPr = paragraph._p.pPr.find(qn('w:numPr'))
        if numPr is not None:
            ilvl = numPr.find(qn('w:ilvl'))
            numId = numPr.find(qn('w:numId'))
            if ilvl is not None and numId is not None:
                numbering_info = {
                    "level": int(ilvl.get(qn('w:val'))),
                    "numId": numId.get(qn('w:val'))
                }
    return {
        "style": style_name,
        "numbering": numbering_info,
        "is_heading": style_name.lower().startswith("heading")
    }


def extract_section_number(text: str) -> Tuple[Optional[str], str, Optional[str]]:
    """Extract section number from paragraph text. Returns (number, remaining_text, type)."""
    text = text.strip()
    patterns = [
        (r'^(ARTICLE\s+[IVXLCDM]+)[.\s:]+(.*)$', 'article'),
        (r'^(Article\s+[IVXLCDM]+)[.\s:]+(.*)$', 'article'),
        (r'^(ARTICLE\s+\d+)[.\s:]+(.*)$', 'article'),
        (r'^(Article\s+\d+)[.\s:]+(.*)$', 'article'),
        (r'^(Section\s+[\d]+\.[\d\.A-Za-z\(\)]+)[.\s:]+(.*)$', 'section'),
        (r'^(Section\s+[\d]+)[.\s:]+(.*)$', 'section'),
        (r'^(SECTION\s+[\d]+\.[\d\.A-Za-z\(\)]+)[.\s:]+(.*)$', 'section'),
        (r'^(SECTION\s+[\d]+)[.\s:]+(.*)$', 'section'),
        (r'^(\d+\.\d+\.\d+\.?\s*)(.*)$', 'subsub'),
        (r'^(\d+\.\d+\.?\s*)(.*)$', 'sub'),
        (r'^(\d+\.)\s+(.*)$', 'top'),
        (r'^([A-Z]\.)\s+(.*)$', 'letter_upper'),
        (r'^([a-z]\.)\s+(.*)$', 'letter_lower'),
        (r'^\(([A-Z])\)\s*(.*)$', 'paren_upper'),
        (r'^\(([a-z])\)\s*(.*)$', 'paren_lower'),
        (r'^\((\d+)\)\s*(.*)$', 'paren_num'),
        (r'^\(([ivxlcdm]+)\)\s*(.*)$', 'roman_lower'),
        (r'^\(([IVXLCDM]+)\)\s*(.*)$', 'roman_upper'),
    ]
    for pattern, num_type in patterns:
        flags = re.IGNORECASE if num_type.startswith('article') or num_type.startswith('section') else 0
        match = re.match(pattern, text, flags)
        if match:
            section_num = match.group(1).strip()
            remaining = match.group(2).strip() if match.lastindex >= 2 else ""
            if num_type.startswith('paren') or num_type.startswith('roman'):
                if not section_num.startswith('('):
                    section_num = f"({section_num})"
            return (section_num, remaining, num_type)
    return (None, text, None)


def extract_caption(text: str, max_length: int = 60) -> str:
    """Extract a caption from paragraph text."""
    _, remaining, _ = extract_section_number(text)
    text_to_use = remaining if remaining else text
    caption_match = re.match(r'^([^.]+\.)\s{2,}', text_to_use)
    if caption_match:
        return caption_match.group(1).strip()
    first_sentence = re.match(r'^([^.]+\.)', text_to_use)
    if first_sentence and len(first_sentence.group(1)) <= max_length:
        return first_sentence.group(1).strip()
    if len(text_to_use) > max_length:
        return text_to_use[:max_length].strip() + "..."
    return text_to_use.strip() if text_to_use.strip() else "(untitled)"


def extract_defined_terms(text: str) -> List[str]:
    """Identify potential defined terms in quoted text."""
    quoted_terms = re.findall(r'"([A-Z][^"]+)"', text)
    paren_terms = re.findall(r'\((?:the\s+)?"([A-Z][^"]+)"\)', text)
    return list(set(quoted_terms + paren_terms))


class SectionTracker:
    """Tracks the current section hierarchy as we parse the document."""

    def __init__(self):
        self.hierarchy = []
        self.counters = {}
        self.last_level = -1
        self.last_numId = None

    def update(self, numbering_level, section_num, caption, numId=None, resolved_ordinal=None):
        if numbering_level is not None and section_num is None:
            if resolved_ordinal:
                section_num = resolved_ordinal
                level = numbering_level
            else:
                if numId != self.last_numId:
                    self.counters = {}
                    self.last_numId = numId
                levels_to_remove = [l for l in self.counters if l > numbering_level]
                for l in levels_to_remove:
                    del self.counters[l]
                self.counters[numbering_level] = self.counters.get(numbering_level, 0) + 1
                section_num = self._generate_section_number(numbering_level)
                level = numbering_level
        elif section_num is not None:
            if numbering_level is not None:
                level = numbering_level
            else:
                if re.match(r'^(Article|ARTICLE|Section|SECTION)', section_num):
                    level = 0
                elif re.match(r'^\d+\.\d+\.\d+', section_num):
                    level = 2
                elif re.match(r'^\d+\.\d+', section_num):
                    level = 1
                elif re.match(r'^\d+\.', section_num):
                    level = 0
                elif re.match(r'^\([ivx]+\)', section_num, re.IGNORECASE):
                    level = 2
                elif re.match(r'^\([a-z]\)', section_num, re.IGNORECASE):
                    level = 2
                else:
                    level = self.last_level + 1 if self.last_level >= 0 else 0
        else:
            return
        self.hierarchy = self.hierarchy[:level]
        self.hierarchy.append({"level": level, "number": section_num, "caption": caption})
        self.last_level = level

    def _generate_section_number(self, level):
        if level == 0:
            return f"{self.counters.get(0, 1)}."
        elif level == 1:
            count = self.counters.get(1, 1)
            letter = chr(ord('A') + count - 1) if count <= 26 else f"A{count-26}"
            return f"{letter}."
        elif level == 2:
            count = self.counters.get(2, 1)
            roman = self._to_roman(count).lower()
            return f"({roman})"
        else:
            count = self.counters.get(level, 1)
            return f"({count})"

    @staticmethod
    def _to_roman(num):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        for i in range(len(val)):
            while num >= val[i]:
                num -= val[i]
                roman_num += syms[i]
        return roman_num

    def get_current_hierarchy(self):
        return list(self.hierarchy)

    def get_section_ref(self):
        if not self.hierarchy:
            return None
        return self.hierarchy[-1]["number"].rstrip('.')


class NumberingResolver:
    """Reads Word's numbering.xml to resolve actual rendered ordinals."""

    def __init__(self, doc):
        self.abstract_nums = {}
        self.num_to_abstract = {}
        self.counters = {}
        try:
            numbering_part = doc.part.numbering_part
        except Exception:
            return
        if numbering_part is None:
            return
        numbering_xml = numbering_part._element
        for abstract in numbering_xml.findall(qn('w:abstractNum')):
            abstract_id = abstract.get(qn('w:abstractNumId'))
            levels = {}
            for lvl in abstract.findall(qn('w:lvl')):
                ilvl = int(lvl.get(qn('w:ilvl')))
                num_fmt_el = lvl.find(qn('w:numFmt'))
                lvl_text_el = lvl.find(qn('w:lvlText'))
                start_el = lvl.find(qn('w:start'))
                levels[ilvl] = {
                    'fmt': num_fmt_el.get(qn('w:val')) if num_fmt_el is not None else 'decimal',
                    'text': lvl_text_el.get(qn('w:val')) if lvl_text_el is not None else f'%{ilvl + 1}.',
                    'start': int(start_el.get(qn('w:val'))) if start_el is not None else 1,
                }
            self.abstract_nums[abstract_id] = levels
        for num in numbering_xml.findall(qn('w:num')):
            num_id = num.get(qn('w:numId'))
            abstract_ref = num.find(qn('w:abstractNumId'))
            if abstract_ref is not None:
                self.num_to_abstract[num_id] = abstract_ref.get(qn('w:val'))

    def resolve(self, num_id, ilvl):
        abstract_id = self.num_to_abstract.get(num_id)
        if abstract_id is None:
            return None, ilvl
        levels_def = self.abstract_nums.get(abstract_id)
        if levels_def is None:
            return None, ilvl
        level_def = levels_def.get(ilvl)
        if level_def is None:
            return None, ilvl
        if level_def['fmt'] == 'bullet':
            return None, ilvl
        if num_id not in self.counters:
            self.counters[num_id] = {}
        counters = self.counters[num_id]
        levels_to_reset = [l for l in counters if l > ilvl]
        for l in levels_to_reset:
            del counters[l]
        if ilvl not in counters:
            counters[ilvl] = level_def['start']
        else:
            counters[ilvl] += 1
        text_pattern = level_def['text']
        result = text_pattern
        for lvl_num in range(10):
            placeholder = f'%{lvl_num + 1}'
            if placeholder in result:
                count = counters.get(lvl_num, levels_def.get(lvl_num, {}).get('start', 1))
                fmt = levels_def.get(lvl_num, {}).get('fmt', 'decimal')
                result = result.replace(placeholder, self._format_number(count, fmt))
        return result, ilvl

    @staticmethod
    def _format_number(num, fmt):
        if fmt == 'decimal':
            return str(num)
        elif fmt == 'lowerLetter':
            return chr(ord('a') + num - 1) if 1 <= num <= 26 else str(num)
        elif fmt == 'upperLetter':
            return chr(ord('A') + num - 1) if 1 <= num <= 26 else str(num)
        elif fmt == 'lowerRoman':
            return NumberingResolver._to_roman(num).lower()
        elif fmt == 'upperRoman':
            return NumberingResolver._to_roman(num)
        else:
            return str(num)

    @staticmethod
    def _to_roman(num):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        for i in range(len(val)):
            while num >= val[i]:
                num -= val[i]
                roman_num += syms[i]
        return roman_num


def _iter_block_items(document):
    """Iterate through document body items in order."""
    parent = document.element.body
    for child in parent.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, document)
        elif child.tag == qn('w:tbl'):
            yield Table(child, document)


def _process_table(table, start_id, section_tracker):
    """Process a table and return structured data."""
    table_data = {
        "type": "table",
        "id": f"tbl_{start_id}",
        "rows": [],
        "section_hierarchy": section_tracker.get_current_hierarchy()
    }
    para_id = start_id
    for row_idx, row in enumerate(table.rows):
        row_data = []
        for cell_idx, cell in enumerate(row.cells):
            cell_paragraphs = []
            for para in cell.paragraphs:
                para_id += 1
                text = para.text.strip()
                section_num, remaining, num_type = extract_section_number(text)
                caption = extract_caption(text)
                cell_paragraphs.append({
                    "id": f"p_{para_id}",
                    "text": text,
                    "section_number": section_num,
                    "caption": caption,
                    "style_info": get_paragraph_style_info(para),
                    "section_hierarchy": section_tracker.get_current_hierarchy()
                })
            row_data.append({"cell_id": f"cell_{row_idx}_{cell_idx}", "paragraphs": cell_paragraphs})
        table_data["rows"].append(row_data)
    return table_data, para_id


def read_docx(docx_path: str) -> Dict[str, Any]:
    """
    Parse a .docx file and extract structured content.

    Args:
        docx_path: Path to the .docx file.

    Returns:
        Dict with keys: source_file, metadata, content, defined_terms, sections, exhibits.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(f"File not found: {docx_path}")

    doc = Document(str(docx_path))
    section_tracker = SectionTracker()

    try:
        numbering_resolver = NumberingResolver(doc)
    except Exception:
        numbering_resolver = None

    result = {
        "source_file": str(docx_path),
        "metadata": {"core_properties": {}},
        "content": [],
        "defined_terms": [],
        "sections": [],
        "exhibits": []
    }

    try:
        props = doc.core_properties
        result["metadata"]["core_properties"] = {
            "title": props.title or "",
            "author": props.author or "",
            "created": str(props.created) if props.created else "",
            "modified": str(props.modified) if props.modified else ""
        }
    except Exception:
        pass

    para_id = 0
    all_defined_terms = set()

    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            para_id += 1
            para_text = block.text.strip()
            style_info = get_paragraph_style_info(block)
            section_num, remaining, num_type = extract_section_number(para_text)
            caption = extract_caption(para_text)
            numbering_level = style_info["numbering"]["level"] if style_info["numbering"] else None
            numId = style_info["numbering"]["numId"] if style_info["numbering"] else None

            resolved_ordinal = None
            if numbering_level is not None and numId is not None and numbering_resolver:
                resolved_ordinal, _ = numbering_resolver.resolve(numId, numbering_level)

            if numbering_level is not None or section_num or style_info["is_heading"]:
                section_tracker.update(numbering_level, section_num, caption, numId, resolved_ordinal)

            para_data = {
                "type": "paragraph",
                "id": f"p_{para_id}",
                "text": para_text,
                "section_number": resolved_ordinal or section_num,
                "section_ref": section_tracker.get_section_ref(),
                "caption": caption,
                "style_info": style_info,
                "indent_level": numbering_level if numbering_level is not None else 0,
                "section_hierarchy": section_tracker.get_current_hierarchy(),
                "is_numbered": bool(style_info["numbering"]) or bool(section_num) or style_info["is_heading"]
            }

            if style_info["is_heading"] or (section_num and num_type in ['article', 'section', 'top']):
                result["sections"].append({
                    "id": f"sec_{para_id}",
                    "number": section_num,
                    "title": caption or para_text[:50],
                    "para_id": f"p_{para_id}",
                    "hierarchy": section_tracker.get_current_hierarchy()
                })

            if re.match(r'^EXHIBIT\s+[A-Z0-9]', para_text, re.IGNORECASE):
                result["exhibits"].append({
                    "id": f"ex_{para_id}",
                    "title": para_text,
                    "start_para_id": f"p_{para_id}"
                })

            terms = extract_defined_terms(para_text)
            all_defined_terms.update(terms)
            result["content"].append(para_data)

        elif isinstance(block, Table):
            table_data, para_id = _process_table(block, para_id, section_tracker)
            result["content"].append(table_data)

    result["defined_terms"] = sorted(list(all_defined_terms))
    return result


def format_for_display(parsed: Dict[str, Any]) -> str:
    """
    Format parsed document output as readable text for Sara.

    Returns a clean text representation with section hierarchy and paragraph IDs.
    """
    lines = []
    source = parsed.get("source_file", "unknown")
    lines.append(f"Document: {source}")

    props = parsed.get("metadata", {}).get("core_properties", {})
    if props.get("title"):
        lines.append(f"Title: {props['title']}")
    if props.get("author"):
        lines.append(f"Author: {props['author']}")

    lines.append("")

    if parsed.get("defined_terms"):
        lines.append(f"Defined Terms ({len(parsed['defined_terms'])}): {', '.join(parsed['defined_terms'][:20])}")
        if len(parsed['defined_terms']) > 20:
            lines.append(f"  ... and {len(parsed['defined_terms']) - 20} more")
        lines.append("")

    lines.append("--- Content ---")
    lines.append("")

    for item in parsed.get("content", []):
        if item["type"] == "paragraph":
            pid = item["id"]
            text = item["text"]
            sec_num = item.get("section_number", "")
            prefix = f"[{pid}]"
            if sec_num:
                prefix += f" {sec_num}"
            if text:
                lines.append(f"{prefix} {text}")
            else:
                lines.append(f"{prefix} (blank)")
        elif item["type"] == "table":
            lines.append(f"[{item['id']}] (table)")

    return "\n".join(lines)
