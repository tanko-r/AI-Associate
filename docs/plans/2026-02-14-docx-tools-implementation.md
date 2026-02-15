# Docx Tools Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add docx read/write/redline/compare capabilities to Sara's plugin via a shared Python core, exposed through both an MCP server and CLI scripts with an in-session toggle.

**Architecture:** Shared `docx-tools/core/` library with 6 modules (reader, writer, redliner, comparer, extractor, analyzer). Two thin interface layers: an MCP server using the `mcp` Python SDK with stdio transport, and CLI scripts using argparse. A `/docx-mode` command toggles between them. Core parsing code adapted from Ambrose's `document_service.py`.

**Tech Stack:** Python 3.10+, python-docx, redlines, diff-match-patch, mcp SDK, uv for running

---

### Task 1: Project Scaffolding and Dependencies

**Files:**
- Create: `docx-tools/core/__init__.py`
- Create: `docx-tools/requirements.txt`
- Create: `docx-tools/pyproject.toml`
- Create: `docx-tools/tests/__init__.py`

**Step 1: Create directory structure**

```bash
mkdir -p /home/david/projects/AI-Associate/docx-tools/core
mkdir -p /home/david/projects/AI-Associate/docx-tools/cli
mkdir -p /home/david/projects/AI-Associate/docx-tools/tests
```

**Step 2: Create pyproject.toml**

Create `docx-tools/pyproject.toml`:

```toml
[project]
name = "docx-tools"
version = "0.1.0"
description = "Docx reading, writing, redlining, and comparison tools for Sara"
requires-python = ">=3.10"
dependencies = [
    "python-docx>=0.8.11",
    "redlines>=0.4.0",
    "diff-match-patch>=20200713",
    "mcp>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
```

**Step 3: Create requirements.txt**

Create `docx-tools/requirements.txt`:

```
python-docx>=0.8.11
redlines>=0.4.0
diff-match-patch>=20200713
mcp>=1.0.0
```

**Step 4: Create core/__init__.py**

Create `docx-tools/core/__init__.py`:

```python
"""Docx tools core library — read, write, redline, compare, extract, analyze."""
```

**Step 5: Create tests/__init__.py**

Create `docx-tools/tests/__init__.py` (empty file).

**Step 6: Install dependencies**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv pip install -e ".[dev]"`

If uv venv doesn't exist yet: `cd /home/david/projects/AI-Associate/docx-tools && uv venv && uv pip install -e ".[dev]"`

**Step 7: Commit**

```bash
git add docx-tools/
git commit -m "feat: scaffold docx-tools project structure and dependencies"
```

---

### Task 2: Core Reader — `reader.py`

Adapted from Ambrose's `document_service.py`. This is the largest core module. It parses a .docx file into a structured dict with paragraph IDs, section hierarchy, defined terms, and metadata.

**Files:**
- Create: `docx-tools/core/reader.py`
- Create: `docx-tools/tests/test_reader.py`
- Reference: Ambrose's `/mnt/c/Users/david/Documents/claude-redlining/app/services/document_service.py` — adapt `parse_document()`, `NumberingResolver`, `SectionTracker`, `extract_section_number()`, `extract_defined_terms()`, `iter_block_items()`, `get_paragraph_style_info()`, `extract_caption()`, `process_table()`

**Step 1: Create a minimal test .docx file for testing**

Create `docx-tools/tests/test_reader.py`:

```python
"""Tests for docx reader."""
import pytest
from pathlib import Path
from docx import Document


@pytest.fixture
def sample_docx(tmp_path):
    """Create a minimal test .docx file."""
    doc = Document()
    doc.add_heading("PURCHASE AND SALE AGREEMENT", level=1)
    doc.add_paragraph("This Purchase and Sale Agreement (this \"Agreement\") is entered into as of January 1, 2026, by and between Acme Corp (\"Seller\") and Widget Inc (\"Buyer\").")
    doc.add_heading("Article I: Definitions", level=2)
    doc.add_paragraph("1.1 \"Property\" means the real property located at 123 Main Street.")
    doc.add_paragraph("1.2 \"Purchase Price\" means the sum of One Million Dollars ($1,000,000).")
    doc.add_heading("Article II: Sale and Purchase", level=2)
    doc.add_paragraph("2.1 Agreement to Sell.  Seller shall sell the Property to Buyer, and Buyer shall purchase the Property from Seller, for the Purchase Price, subject to the terms and conditions of this Agreement.")
    doc.add_paragraph("2.2 Closing Date.  The closing shall occur on or before March 1, 2026 (the \"Closing Date\").")
    path = tmp_path / "test_contract.docx"
    doc.save(str(path))
    return path


def test_read_docx_returns_dict(sample_docx):
    from core.reader import read_docx
    result = read_docx(str(sample_docx))
    assert isinstance(result, dict)
    assert "content" in result
    assert "metadata" in result
    assert "defined_terms" in result
    assert "sections" in result


def test_read_docx_extracts_paragraphs(sample_docx):
    from core.reader import read_docx
    result = read_docx(str(sample_docx))
    paragraphs = [item for item in result["content"] if item["type"] == "paragraph"]
    assert len(paragraphs) >= 5
    # Each paragraph has an ID
    for p in paragraphs:
        assert p["id"].startswith("p_")
        assert "text" in p


def test_read_docx_extracts_defined_terms(sample_docx):
    from core.reader import read_docx
    result = read_docx(str(sample_docx))
    terms = result["defined_terms"]
    assert "Agreement" in terms
    assert "Property" in terms
    assert "Purchase Price" in terms


def test_read_docx_extracts_sections(sample_docx):
    from core.reader import read_docx
    result = read_docx(str(sample_docx))
    assert len(result["sections"]) > 0


def test_read_docx_extracts_metadata(sample_docx):
    from core.reader import read_docx
    result = read_docx(str(sample_docx))
    assert "core_properties" in result["metadata"]


def test_read_docx_nonexistent_file():
    from core.reader import read_docx
    with pytest.raises(FileNotFoundError):
        read_docx("/nonexistent/file.docx")
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_reader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.reader'`

**Step 3: Implement reader.py**

Create `docx-tools/core/reader.py`. This is adapted from Ambrose's `document_service.py`, stripping Flask/session handling:

```python
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_reader.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/reader.py docx-tools/tests/test_reader.py
git commit -m "feat: add core docx reader with section tracking and defined term extraction"
```

---

### Task 3: Core Writer — `writer.py`

Converts markdown or structured text content into a properly formatted .docx file.

**Files:**
- Create: `docx-tools/core/writer.py`
- Create: `docx-tools/tests/test_writer.py`

**Step 1: Write the tests**

Create `docx-tools/tests/test_writer.py`:

```python
"""Tests for docx writer."""
import pytest
from pathlib import Path
from docx import Document


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path


def test_write_docx_from_markdown(output_dir):
    from core.writer import write_docx
    content = """# Memorandum

**To:** Partner
**From:** Sara
**Date:** February 14, 2026
**Re:** Lease Termination Rights

## Question Presented

Whether the tenant may terminate the lease early under Section 5.2.

## Short Answer

Yes. The lease grants the tenant an early termination right upon 90 days' written notice after the third lease year.
"""
    output_path = output_dir / "memo.docx"
    write_docx(content, str(output_path))
    assert output_path.exists()
    doc = Document(str(output_path))
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "Memorandum" in full_text
    assert "Question Presented" in full_text


def test_write_docx_with_template(output_dir, tmp_path):
    from core.writer import write_docx
    # Create a template with custom font
    template = Document()
    style = template.styles['Normal']
    style.font.name = 'Times New Roman'
    template_path = tmp_path / "template.docx"
    template.save(str(template_path))

    content = "This is a test paragraph."
    output_path = output_dir / "from_template.docx"
    write_docx(content, str(output_path), template_path=str(template_path))
    assert output_path.exists()


def test_write_docx_creates_parent_dirs(output_dir):
    from core.writer import write_docx
    output_path = output_dir / "subdir" / "deep" / "memo.docx"
    write_docx("Test content", str(output_path))
    assert output_path.exists()


def test_write_docx_returns_path(output_dir):
    from core.writer import write_docx
    output_path = output_dir / "test.docx"
    result = write_docx("Content", str(output_path))
    assert result == str(output_path)
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_writer.py -v`
Expected: FAIL

**Step 3: Implement writer.py**

Create `docx-tools/core/writer.py`:

```python
"""
Write content to .docx files.

Converts markdown-formatted text or plain text into a properly formatted
Word document with headings, bold, italic, and list support.
"""

import re
from pathlib import Path
from typing import Optional

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def write_docx(
    content: str,
    output_path: str,
    template_path: Optional[str] = None,
) -> str:
    """
    Write content to a .docx file.

    Args:
        content: Markdown-formatted text or plain text to write.
        output_path: Path for the output .docx file.
        template_path: Optional path to a .docx template for style inheritance.

    Returns:
        The output file path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if template_path and Path(template_path).exists():
        doc = Document(str(template_path))
        # Clear template content but keep styles
        for para in list(doc.paragraphs):
            p_element = para._element
            p_element.getparent().remove(p_element)
    else:
        doc = Document()
        _apply_default_styles(doc)

    _render_markdown_to_docx(doc, content)
    doc.save(str(output_path))
    return str(output_path)


def _apply_default_styles(doc: Document):
    """Apply clean professional defaults to a new document."""
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    for level in range(1, 4):
        heading_style = doc.styles[f'Heading {level}']
        heading_style.font.name = 'Times New Roman'
        heading_style.font.bold = True
        if level == 1:
            heading_style.font.size = Pt(16)
            heading_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif level == 2:
            heading_style.font.size = Pt(14)
        elif level == 3:
            heading_style.font.size = Pt(12)


def _render_markdown_to_docx(doc: Document, content: str):
    """Parse markdown content and add it to the document."""
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = min(len(heading_match.group(1)), 3)
            text = heading_match.group(2).strip()
            doc.add_heading(text, level=level)
            i += 1
            continue

        # Blank lines
        if not line.strip():
            i += 1
            continue

        # Regular paragraph (may contain inline markdown)
        para = doc.add_paragraph()
        _add_inline_markdown(para, line.strip())
        i += 1


def _add_inline_markdown(paragraph, text: str):
    """Add text with inline markdown formatting (bold, italic) to a paragraph."""
    # Pattern to match **bold**, *italic*, or plain text segments
    pattern = r'(\*\*(.+?)\*\*|\*(.+?)\*|([^*]+))'
    for match in re.finditer(pattern, text):
        full = match.group(0)
        if full.startswith('**') and full.endswith('**'):
            run = paragraph.add_run(match.group(2))
            run.bold = True
        elif full.startswith('*') and full.endswith('*'):
            run = paragraph.add_run(match.group(3))
            run.italic = True
        else:
            paragraph.add_run(match.group(4))
```

**Step 4: Run tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_writer.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/writer.py docx-tools/tests/test_writer.py
git commit -m "feat: add core docx writer with markdown-to-docx conversion"
```

---

### Task 4: Core Redliner — `redliner.py`

Generates a .docx with native Word track changes showing insertions and deletions.

**Files:**
- Create: `docx-tools/core/redliner.py`
- Create: `docx-tools/tests/test_redliner.py`
- Reference: Ambrose's `_apply_track_changes_to_paragraph()` and `_apply_run_formatting()` from `document_service.py`

**Step 1: Write the tests**

Create `docx-tools/tests/test_redliner.py`:

```python
"""Tests for docx redliner."""
import pytest
from pathlib import Path
from docx import Document


@pytest.fixture
def original_docx(tmp_path):
    """Create a test .docx with known content."""
    doc = Document()
    doc.add_paragraph("The Seller shall deliver the Property on the Closing Date.")
    doc.add_paragraph("The Purchase Price shall be One Million Dollars ($1,000,000).")
    doc.add_paragraph("This Agreement may be terminated by either party upon thirty (30) days written notice.")
    path = tmp_path / "original.docx"
    doc.save(str(path))
    return path


def test_redline_docx_creates_output(original_docx, tmp_path):
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "original": "The Seller shall deliver the Property on the Closing Date.",
            "revised": "The Seller shall deliver the Property on or before the Closing Date."
        }
    }
    output_path = tmp_path / "redlined.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()


def test_redline_docx_with_no_changes(original_docx, tmp_path):
    from core.redliner import redline_docx
    output_path = tmp_path / "redlined.docx"
    result = redline_docx(str(original_docx), {}, str(output_path))
    assert Path(result).exists()


def test_redline_docx_preserves_unchanged(original_docx, tmp_path):
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "original": "The Seller shall deliver the Property on the Closing Date.",
            "revised": "The Seller shall deliver the Property on or before the Closing Date."
        }
    }
    output_path = tmp_path / "redlined.docx"
    redline_docx(str(original_docx), revisions, str(output_path))
    doc = Document(str(output_path))
    # Paragraph 2 (index 1) should be unchanged
    assert "Purchase Price" in doc.paragraphs[1].text
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_redliner.py -v`
Expected: FAIL

**Step 3: Implement redliner.py**

Create `docx-tools/core/redliner.py`:

```python
"""
Generate .docx files with native Word track changes.

Applies revisions to a document using Word's revision markup (w:ins, w:del)
so changes display correctly in Microsoft Word's track changes view.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

import diff_match_patch as dmp_module
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def redline_docx(
    original_path: str,
    revisions: Dict[str, Dict[str, str]],
    output_path: str,
    author: str = "Sara",
) -> str:
    """
    Generate a Word document with track changes.

    Args:
        original_path: Path to the original .docx file.
        revisions: Dict mapping paragraph ID (e.g., "p_1") to
                   {"original": "...", "revised": "..."}.
        output_path: Path for the output .docx file.
        author: Author name for track changes attribution.

    Returns:
        The output file path.
    """
    original_path = Path(original_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(original_path, output_path)
    doc = Document(str(output_path))

    para_id = 0
    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            para_id += 1
            para_key = f"p_{para_id}"
            if para_key in revisions:
                rev = revisions[para_key]
                original_text = rev.get("original", "")
                revised_text = rev.get("revised", "")
                if original_text != revised_text:
                    _apply_track_changes(block, original_text, revised_text, author)
        elif isinstance(block, Table):
            for row in block.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        para_id += 1
                        para_key = f"p_{para_id}"
                        if para_key in revisions:
                            rev = revisions[para_key]
                            original_text = rev.get("original", "")
                            revised_text = rev.get("revised", "")
                            if original_text != revised_text:
                                _apply_track_changes(para, original_text, revised_text, author)

    doc.save(str(output_path))
    return str(output_path)


def _iter_block_items(document):
    """Iterate through document body items in order."""
    parent = document.element.body
    for child in parent.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, document)
        elif child.tag == qn('w:tbl'):
            yield Table(child, document)


def _apply_track_changes(paragraph, original_text: str, revised_text: str, author: str):
    """Apply track changes to a single paragraph using Word revision markup."""
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(original_text, revised_text)
    dmp.diff_cleanupSemantic(diffs)

    # Capture first run's formatting
    first_run_format = None
    if paragraph.runs:
        first_run = paragraph.runs[0]
        first_run_format = {
            'bold': first_run.bold,
            'italic': first_run.italic,
            'underline': first_run.underline,
            'font_name': first_run.font.name,
            'font_size': first_run.font.size,
        }

    # Clear existing runs
    p = paragraph._p
    for child in list(p):
        if child.tag == qn('w:r'):
            p.remove(child)

    rev_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    for op, text in diffs:
        if op == 0:  # Unchanged
            run = _make_run(text, first_run_format)
            p.append(run)
        elif op == -1:  # Deletion
            del_elem = OxmlElement('w:del')
            del_elem.set(qn('w:id'), str(abs(hash(text)) % 100000))
            del_elem.set(qn('w:author'), author)
            del_elem.set(qn('w:date'), rev_date)
            run = _make_run(text, first_run_format, is_delete=True)
            del_elem.append(run)
            p.append(del_elem)
        elif op == 1:  # Insertion
            ins_elem = OxmlElement('w:ins')
            ins_elem.set(qn('w:id'), str(abs(hash(text)) % 100000))
            ins_elem.set(qn('w:author'), author)
            ins_elem.set(qn('w:date'), rev_date)
            run = _make_run(text, first_run_format)
            ins_elem.append(run)
            p.append(ins_elem)


def _make_run(text: str, format_dict: dict = None, is_delete: bool = False):
    """Create a w:r element with optional formatting."""
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    if format_dict:
        if format_dict.get('bold'):
            rPr.append(OxmlElement('w:b'))
        if format_dict.get('italic'):
            rPr.append(OxmlElement('w:i'))
        if format_dict.get('underline'):
            u = OxmlElement('w:u')
            u.set(qn('w:val'), 'single')
            rPr.append(u)
        if format_dict.get('font_name'):
            rFonts = OxmlElement('w:rFonts')
            rFonts.set(qn('w:ascii'), format_dict['font_name'])
            rFonts.set(qn('w:hAnsi'), format_dict['font_name'])
            rPr.append(rFonts)
        if format_dict.get('font_size'):
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), str(int(format_dict['font_size'].pt * 2)))
            rPr.append(sz)
    run.append(rPr)

    if is_delete:
        t = OxmlElement('w:delText')
    else:
        t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    run.append(t)
    return run
```

**Step 4: Run tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_redliner.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/redliner.py docx-tools/tests/test_redliner.py
git commit -m "feat: add core docx redliner with Word track changes markup"
```

---

### Task 5: Core Comparer — `comparer.py`

Compares two .docx files and returns a structured diff report.

**Files:**
- Create: `docx-tools/core/comparer.py`
- Create: `docx-tools/tests/test_comparer.py`

**Step 1: Write the tests**

Create `docx-tools/tests/test_comparer.py`:

```python
"""Tests for docx comparer."""
import pytest
from docx import Document


@pytest.fixture
def two_versions(tmp_path):
    """Create two versions of a document."""
    doc1 = Document()
    doc1.add_paragraph("The Seller shall deliver the Property on the Closing Date.")
    doc1.add_paragraph("The Purchase Price shall be One Million Dollars ($1,000,000).")
    doc1.add_paragraph("This Agreement may be terminated by either party.")
    path1 = tmp_path / "v1.docx"
    doc1.save(str(path1))

    doc2 = Document()
    doc2.add_paragraph("The Seller shall deliver the Property on or before the Closing Date.")
    doc2.add_paragraph("The Purchase Price shall be One Million Dollars ($1,000,000).")
    doc2.add_paragraph("This Agreement may be terminated by Buyer only upon thirty (30) days written notice.")
    path2 = tmp_path / "v2.docx"
    doc2.save(str(path2))
    return path1, path2


def test_compare_returns_diff_report(two_versions):
    from core.comparer import compare_docx
    path1, path2 = two_versions
    result = compare_docx(str(path1), str(path2))
    assert isinstance(result, dict)
    assert "summary" in result
    assert "changes" in result


def test_compare_detects_modifications(two_versions):
    from core.comparer import compare_docx
    path1, path2 = two_versions
    result = compare_docx(str(path1), str(path2))
    changes = result["changes"]
    modified = [c for c in changes if c["type"] == "modified"]
    assert len(modified) == 2  # paragraphs 1 and 3 changed


def test_compare_detects_no_changes(tmp_path):
    from core.comparer import compare_docx
    doc = Document()
    doc.add_paragraph("Identical content.")
    path1 = tmp_path / "a.docx"
    path2 = tmp_path / "b.docx"
    doc.save(str(path1))
    doc.save(str(path2))
    result = compare_docx(str(path1), str(path2))
    assert result["summary"]["total_changes"] == 0


def test_compare_with_redline_output(two_versions, tmp_path):
    from core.comparer import compare_docx
    path1, path2 = two_versions
    redline_path = tmp_path / "comparison.docx"
    result = compare_docx(str(path1), str(path2), redline_output=str(redline_path))
    assert redline_path.exists()
    assert "redline_path" in result
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_comparer.py -v`
Expected: FAIL

**Step 3: Implement comparer.py**

Create `docx-tools/core/comparer.py`:

```python
"""
Compare two .docx files and produce a structured diff report.

Optionally generates a redlined .docx showing the differences.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

import diff_match_patch as dmp_module

from core.reader import read_docx
from core.redliner import redline_docx


def compare_docx(
    path_a: str,
    path_b: str,
    redline_output: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compare two .docx files and return a structured diff report.

    Args:
        path_a: Path to the first (original) .docx file.
        path_b: Path to the second (revised) .docx file.
        redline_output: Optional path to write a redlined .docx showing changes.

    Returns:
        Dict with keys: summary, changes, and optionally redline_path.
    """
    parsed_a = read_docx(path_a)
    parsed_b = read_docx(path_b)

    paras_a = [p for p in parsed_a["content"] if p["type"] == "paragraph"]
    paras_b = [p for p in parsed_b["content"] if p["type"] == "paragraph"]

    dmp = dmp_module.diff_match_patch()
    changes: List[Dict[str, Any]] = []
    revisions_for_redline: Dict[str, Dict[str, str]] = {}

    max_len = max(len(paras_a), len(paras_b))
    for i in range(max_len):
        if i < len(paras_a) and i < len(paras_b):
            text_a = paras_a[i]["text"]
            text_b = paras_b[i]["text"]
            para_id = paras_a[i]["id"]
            section_ref = paras_a[i].get("section_ref")

            if text_a != text_b:
                diffs = dmp.diff_main(text_a, text_b)
                dmp.diff_cleanupSemantic(diffs)
                changes.append({
                    "type": "modified",
                    "para_id": para_id,
                    "section_ref": section_ref,
                    "original": text_a,
                    "revised": text_b,
                    "diff": _format_diff(diffs),
                })
                revisions_for_redline[para_id] = {
                    "original": text_a,
                    "revised": text_b,
                }
        elif i < len(paras_a):
            changes.append({
                "type": "deleted",
                "para_id": paras_a[i]["id"],
                "section_ref": paras_a[i].get("section_ref"),
                "text": paras_a[i]["text"],
            })
        else:
            changes.append({
                "type": "added",
                "para_id": f"new_{i}",
                "text": paras_b[i]["text"],
            })

    result: Dict[str, Any] = {
        "summary": {
            "total_changes": len(changes),
            "modified": len([c for c in changes if c["type"] == "modified"]),
            "added": len([c for c in changes if c["type"] == "added"]),
            "deleted": len([c for c in changes if c["type"] == "deleted"]),
            "paragraphs_a": len(paras_a),
            "paragraphs_b": len(paras_b),
        },
        "changes": changes,
    }

    if redline_output and revisions_for_redline:
        redline_docx(path_a, revisions_for_redline, redline_output)
        result["redline_path"] = redline_output

    return result


def _format_diff(diffs) -> str:
    """Format diff operations as a readable string."""
    parts = []
    for op, text in diffs:
        if op == 0:
            parts.append(text)
        elif op == -1:
            parts.append(f"[-{text}-]")
        elif op == 1:
            parts.append(f"[+{text}+]")
    return "".join(parts)


def format_for_display(result: Dict[str, Any]) -> str:
    """Format comparison result as readable text for Sara."""
    lines = []
    s = result["summary"]
    lines.append(f"Comparison: {s['total_changes']} changes ({s['modified']} modified, {s['added']} added, {s['deleted']} deleted)")
    lines.append(f"Document A: {s['paragraphs_a']} paragraphs | Document B: {s['paragraphs_b']} paragraphs")
    lines.append("")

    for change in result["changes"]:
        ctype = change["type"].upper()
        pid = change.get("para_id", "")
        sec = change.get("section_ref", "")
        header = f"[{ctype}] {pid}"
        if sec:
            header += f" (Section {sec})"
        lines.append(header)

        if ctype == "MODIFIED":
            lines.append(f"  {change['diff']}")
        elif ctype == "DELETED":
            lines.append(f"  Removed: {change['text'][:200]}")
        elif ctype == "ADDED":
            lines.append(f"  Added: {change['text'][:200]}")
        lines.append("")

    if result.get("redline_path"):
        lines.append(f"Redlined document saved to: {result['redline_path']}")

    return "\n".join(lines)
```

**Step 4: Run tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_comparer.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/comparer.py docx-tools/tests/test_comparer.py
git commit -m "feat: add core docx comparer with diff reporting and optional redline output"
```

---

### Task 6: Core Extractor — `extractor.py`

Extracts document structure: sections, defined terms with definitions, provision types, exhibits.

**Files:**
- Create: `docx-tools/core/extractor.py`
- Create: `docx-tools/tests/test_extractor.py`

**Step 1: Write the tests**

Create `docx-tools/tests/test_extractor.py`:

```python
"""Tests for docx structure extractor."""
import pytest
from docx import Document


@pytest.fixture
def contract_docx(tmp_path):
    """Create a contract-like .docx for structure extraction."""
    doc = Document()
    doc.add_heading("COMMERCIAL LEASE AGREEMENT", level=1)
    doc.add_paragraph("This Lease Agreement (this \"Lease\") is entered into by and between Big Landlord LLC (\"Landlord\") and Small Tenant Inc (\"Tenant\").")
    doc.add_heading("Article I: Premises", level=2)
    doc.add_paragraph("1.1 Landlord hereby leases to Tenant the premises located at 456 Commerce Drive (the \"Premises\").")
    doc.add_heading("Article II: Term", level=2)
    doc.add_paragraph("2.1 The term of this Lease shall commence on April 1, 2026 (the \"Commencement Date\") and shall expire on March 31, 2031.")
    doc.add_paragraph("2.2 Tenant shall have the option to renew this Lease for one additional five-year term upon written notice to Landlord not less than 180 days prior to expiration.")
    doc.add_heading("Article III: Rent", level=2)
    doc.add_paragraph("3.1 Tenant shall pay base rent of $5,000 per month (the \"Base Rent\"), due on the first day of each calendar month.")
    doc.add_paragraph("3.2 Base Rent shall increase by three percent (3%) on each anniversary of the Commencement Date.")
    path = tmp_path / "lease.docx"
    doc.save(str(path))
    return path


def test_extract_returns_structure(contract_docx):
    from core.extractor import extract_structure
    result = extract_structure(str(contract_docx))
    assert "sections" in result
    assert "defined_terms" in result
    assert "provisions" in result
    assert "exhibits" in result


def test_extract_finds_sections(contract_docx):
    from core.extractor import extract_structure
    result = extract_structure(str(contract_docx))
    section_titles = [s["title"] for s in result["sections"]]
    assert any("Premises" in t for t in section_titles)
    assert any("Term" in t for t in section_titles)
    assert any("Rent" in t for t in section_titles)


def test_extract_finds_defined_terms(contract_docx):
    from core.extractor import extract_structure
    result = extract_structure(str(contract_docx))
    term_names = [t["term"] for t in result["defined_terms"]]
    assert "Lease" in term_names
    assert "Premises" in term_names
    assert "Base Rent" in term_names


def test_extract_classifies_provisions(contract_docx):
    from core.extractor import extract_structure
    result = extract_structure(str(contract_docx))
    provision_types = set(p["type"] for p in result["provisions"])
    assert len(provision_types) > 0
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_extractor.py -v`
Expected: FAIL

**Step 3: Implement extractor.py**

Create `docx-tools/core/extractor.py`:

```python
"""
Extract document structure from .docx files.

Returns sections, defined terms with definitions, provision classifications,
and exhibits without requiring LLM analysis.
"""

import re
from typing import Dict, Any, List

from core.reader import read_docx


# Patterns for classifying provisions
PROVISION_PATTERNS = {
    "obligation": [
        r'\bshall\b(?!\s+not)',
        r'\bmust\b',
        r'\bagrees?\s+to\b',
        r'\bcovenants?\s+to\b',
    ],
    "right": [
        r'\bmay\b(?!\s+not)',
        r'\bis\s+entitled\b',
        r'\bhas\s+the\s+(?:right|option)\b',
        r'\bshall\s+have\s+the\s+(?:right|option)\b',
    ],
    "condition": [
        r'\bsubject\s+to\b',
        r'\bprovided\s+that\b',
        r'\bconditioned?\s+upon\b',
        r'\bif\s+and\s+only\s+if\b',
    ],
    "termination": [
        r'\bterminate\b',
        r'\bcancell?(?:ation|ed)\b',
        r'\bexpir(?:e|ation)\b',
    ],
    "indemnification": [
        r'\bindemnif(?:y|ication)\b',
        r'\bhold\s+harmless\b',
        r'\bdefend\b.*\bclaims?\b',
    ],
    "representation": [
        r'\brepresents?\s+(?:and\s+warrants?|that)\b',
        r'\bwarrants?\s+(?:and\s+represents?|that)\b',
    ],
}

# Patterns for extracting defined terms with their definitions
DEFINITION_PATTERN = re.compile(
    r'["\u201c]([A-Z][^"\u201d]+)["\u201d]\s+(?:means?|shall\s+mean|refers?\s+to|is\s+defined\s+as)\s+(.+?)(?:\.(?:\s|$)|\.$)',
    re.IGNORECASE
)

# Parenthetical definitions: (the "Term")
PAREN_DEFINITION_PATTERN = re.compile(
    r'(.{10,120}?)\s+\((?:the\s+|each,?\s+a\s+)?["\u201c]([A-Z][^"\u201d]+)["\u201d]\)',
)


def extract_structure(docx_path: str) -> Dict[str, Any]:
    """
    Extract document structure from a .docx file.

    Args:
        docx_path: Path to the .docx file.

    Returns:
        Dict with keys: sections, defined_terms, provisions, exhibits, summary.
    """
    parsed = read_docx(docx_path)
    paragraphs = [p for p in parsed["content"] if p["type"] == "paragraph"]

    sections = parsed["sections"]
    exhibits = parsed["exhibits"]

    defined_terms = _extract_defined_terms_with_definitions(paragraphs)
    provisions = _classify_provisions(paragraphs)

    return {
        "sections": sections,
        "defined_terms": defined_terms,
        "provisions": provisions,
        "exhibits": exhibits,
        "summary": {
            "total_paragraphs": len(paragraphs),
            "total_sections": len(sections),
            "total_defined_terms": len(defined_terms),
            "total_provisions": len(provisions),
            "total_exhibits": len(exhibits),
        }
    }


def _extract_defined_terms_with_definitions(paragraphs: List[Dict]) -> List[Dict]:
    """Extract defined terms and their definitions from paragraph text."""
    terms = {}

    for para in paragraphs:
        text = para["text"]
        if not text:
            continue

        # Explicit definitions: "Term" means ...
        for match in DEFINITION_PATTERN.finditer(text):
            term_name = match.group(1).strip()
            definition = match.group(2).strip()
            terms[term_name] = {
                "term": term_name,
                "definition": definition,
                "para_id": para["id"],
                "section_ref": para.get("section_ref"),
            }

        # Parenthetical definitions: ... (the "Term")
        for match in PAREN_DEFINITION_PATTERN.finditer(text):
            context = match.group(1).strip()
            term_name = match.group(2).strip()
            if term_name not in terms:
                terms[term_name] = {
                    "term": term_name,
                    "definition": context,
                    "para_id": para["id"],
                    "section_ref": para.get("section_ref"),
                }

    return sorted(terms.values(), key=lambda t: t["term"])


def _classify_provisions(paragraphs: List[Dict]) -> List[Dict]:
    """Classify paragraphs by provision type based on language patterns."""
    provisions = []

    for para in paragraphs:
        text = para["text"]
        if not text or len(text) < 30:
            continue

        matched_types = []
        for ptype, patterns in PROVISION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matched_types.append(ptype)
                    break

        if matched_types:
            provisions.append({
                "para_id": para["id"],
                "section_ref": para.get("section_ref"),
                "type": matched_types[0],  # Primary classification
                "all_types": matched_types,
                "caption": para.get("caption", ""),
                "text_preview": text[:150],
            })

    return provisions


def format_for_display(result: Dict[str, Any]) -> str:
    """Format extraction result as readable text for Sara."""
    lines = []
    s = result["summary"]
    lines.append(f"Document Structure: {s['total_paragraphs']} paragraphs, {s['total_sections']} sections")
    lines.append("")

    lines.append("--- Sections ---")
    for sec in result["sections"]:
        num = sec.get("number", "")
        title = sec.get("title", "")
        lines.append(f"  {num} {title}".strip())
    lines.append("")

    lines.append(f"--- Defined Terms ({s['total_defined_terms']}) ---")
    for term in result["defined_terms"]:
        defn = term["definition"][:100]
        lines.append(f"  \"{term['term']}\" — {defn}")
    lines.append("")

    lines.append(f"--- Provisions ({s['total_provisions']}) ---")
    type_counts = {}
    for p in result["provisions"]:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {ptype}: {count}")
    lines.append("")

    if result["exhibits"]:
        lines.append("--- Exhibits ---")
        for ex in result["exhibits"]:
            lines.append(f"  {ex['title']}")

    return "\n".join(lines)
```

**Step 4: Run tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_extractor.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/extractor.py docx-tools/tests/test_extractor.py
git commit -m "feat: add core docx structure extractor with provision classification"
```

---

### Task 7: Core Analyzer — `analyzer.py`

Prepares a structured, prompt-ready analysis of a contract for Sara to process with her own judgment. No external AI calls.

**Files:**
- Create: `docx-tools/core/analyzer.py`
- Create: `docx-tools/tests/test_analyzer.py`

**Step 1: Write the tests**

Create `docx-tools/tests/test_analyzer.py`:

```python
"""Tests for contract analyzer."""
import pytest
from docx import Document


@pytest.fixture
def contract_docx(tmp_path):
    doc = Document()
    doc.add_heading("PURCHASE AND SALE AGREEMENT", level=1)
    doc.add_paragraph("This Purchase and Sale Agreement (this \"Agreement\") is entered into by Acme Corp (\"Seller\") and Widget Inc (\"Buyer\").")
    doc.add_paragraph("1.1 Seller represents and warrants that Seller has good and marketable title to the Property.")
    doc.add_paragraph("2.1 Buyer shall pay the Purchase Price of $1,000,000 at closing.")
    doc.add_paragraph("3.1 Seller shall indemnify and hold harmless Buyer from any claims arising from a breach of Seller's representations.")
    doc.add_paragraph("4.1 Either party may terminate this Agreement upon thirty (30) days written notice if the other party is in material default.")
    path = tmp_path / "psa.docx"
    doc.save(str(path))
    return path


def test_analyze_returns_structured_output(contract_docx):
    from core.analyzer import analyze_contract
    result = analyze_contract(str(contract_docx), representation="buyer")
    assert "risk_categories" in result
    assert "provisions_by_concept" in result
    assert "representation" in result


def test_analyze_identifies_risk_categories(contract_docx):
    from core.analyzer import analyze_contract
    result = analyze_contract(str(contract_docx), representation="buyer")
    categories = [c["category"] for c in result["risk_categories"]]
    assert len(categories) > 0


def test_analyze_includes_representation(contract_docx):
    from core.analyzer import analyze_contract
    result = analyze_contract(str(contract_docx), representation="seller")
    assert result["representation"] == "seller"
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_analyzer.py -v`
Expected: FAIL

**Step 3: Implement analyzer.py**

Create `docx-tools/core/analyzer.py`:

```python
"""
Lightweight contract analysis that prepares structured output for Sara.

No external AI calls — this tool parses the document, identifies risk
categories, and organizes provisions into a prompt-ready format that
Sara processes with her own judgment.
"""

import re
from typing import Dict, Any, List, Optional

from core.reader import read_docx
from core.extractor import extract_structure, PROVISION_PATTERNS


# Risk categories by contract type (adapted from Ambrose)
RISK_CATEGORIES = {
    "purchase and sale agreement": [
        "Buyer Closing Escapes",
        "Deposit at Risk",
        "Title/Survey Cure Obligations",
        "Representation Exposure",
        "Indemnification Scope",
        "Closing Timeline Risk",
        "Financing Contingency",
        "Due Diligence Termination Rights",
        "Casualty/Condemnation Risk",
        "Default Remedies",
    ],
    "lease": [
        "Rent Escalation Exposure",
        "Landlord Control of Property",
        "Tenant Default Remedies",
        "Assignment/Subletting Restrictions",
        "Operating Expense Passthrough",
        "Renewal/Extension Options",
        "Early Termination Rights",
        "Maintenance and Repair Obligations",
        "Insurance Requirements",
        "Casualty/Condemnation",
        "Holdover Provisions",
        "Security Deposit",
    ],
    "development agreement": [
        "Performance Timeline Risk",
        "Cost Overrun Allocation",
        "Change Order Approval",
        "Completion Standards",
        "Warranty Scope",
        "Indemnification Obligations",
        "Default and Cure Rights",
        "Termination Triggers",
    ],
    "loan agreement": [
        "Default Triggers",
        "Cross-Default Provisions",
        "Prepayment Restrictions",
        "Financial Covenant Compliance",
        "Collateral Requirements",
        "Representation Exposure",
        "Acceleration Rights",
    ],
}

# Keywords that signal specific risk categories
CATEGORY_SIGNALS = {
    "Deposit at Risk": [r'\bdeposit\b', r'\bearnest\s+money\b'],
    "Title/Survey Cure Obligations": [r'\btitle\b', r'\bsurvey\b', r'\bencumbrance\b'],
    "Representation Exposure": [r'\brepresents?\b', r'\bwarrants?\b'],
    "Indemnification Scope": [r'\bindemnif\b', r'\bhold\s+harmless\b'],
    "Closing Timeline Risk": [r'\bclosing\s+date\b', r'\bextension\b', r'\btime\s+is\s+of\s+the\s+essence\b'],
    "Financing Contingency": [r'\bfinancing\b', r'\bloan\b', r'\bmortgage\b'],
    "Due Diligence Termination Rights": [r'\bdue\s+diligence\b', r'\binspection\b', r'\bfeasibility\b'],
    "Casualty/Condemnation Risk": [r'\bcasualty\b', r'\bcondemnation\b', r'\beminent\s+domain\b'],
    "Default Remedies": [r'\bdefault\b', r'\bbreach\b', r'\bliquidated\s+damages\b', r'\bspecific\s+performance\b'],
    "Buyer Closing Escapes": [r'\bcondition\s+(?:precedent|to\s+closing)\b', r'\btermination\s+right\b'],
    "Rent Escalation Exposure": [r'\brent\b.*\bincrease\b', r'\bescalat\b', r'\bCPI\b'],
    "Assignment/Subletting Restrictions": [r'\bassign\b', r'\bsublet\b', r'\btransfer\b'],
    "Operating Expense Passthrough": [r'\boperating\s+expense\b', r'\bCAM\b', r'\bcommon\s+area\b'],
    "Renewal/Extension Options": [r'\brenewal?\b', r'\bextension\b', r'\boption\s+to\s+renew\b'],
    "Early Termination Rights": [r'\bearly\s+termination\b', r'\bterminate\b.*\bprior\b'],
    "Holdover Provisions": [r'\bholdover\b'],
    "Security Deposit": [r'\bsecurity\s+deposit\b'],
    "Default Triggers": [r'\bevent\s+of\s+default\b', r'\bdefault\b'],
    "Cross-Default Provisions": [r'\bcross.?default\b'],
    "Prepayment Restrictions": [r'\bprepay\b', r'\bearly\s+repayment\b'],
    "Acceleration Rights": [r'\baccelerat\b'],
}


def analyze_contract(
    docx_path: str,
    representation: str,
    focus_areas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze a contract and return structured, prompt-ready output.

    Args:
        docx_path: Path to the .docx file.
        representation: Who the client is (e.g., "buyer", "seller", "tenant").
        focus_areas: Optional list of specific areas to focus on.

    Returns:
        Dict with risk_categories, provisions_by_concept, representation, and structure.
    """
    structure = extract_structure(docx_path)
    parsed = read_docx(docx_path)
    paragraphs = [p for p in parsed["content"] if p["type"] == "paragraph"]

    contract_type = _detect_contract_type(paragraphs)
    categories = RISK_CATEGORIES.get(contract_type, RISK_CATEGORIES["purchase and sale agreement"])

    if focus_areas:
        categories = [c for c in categories if any(f.lower() in c.lower() for f in focus_areas)] or categories

    risk_analysis = _map_risk_categories(paragraphs, categories)

    provisions_by_concept = {}
    for prov in structure["provisions"]:
        ptype = prov["type"]
        if ptype not in provisions_by_concept:
            provisions_by_concept[ptype] = []
        provisions_by_concept[ptype].append(prov)

    return {
        "contract_type": contract_type,
        "representation": representation,
        "risk_categories": risk_analysis,
        "provisions_by_concept": provisions_by_concept,
        "defined_terms": structure["defined_terms"],
        "sections": structure["sections"],
        "summary": {
            "total_paragraphs": len(paragraphs),
            "categories_identified": len([r for r in risk_analysis if r["paragraphs"]]),
            "total_provisions_classified": len(structure["provisions"]),
        },
    }


def _detect_contract_type(paragraphs: List[Dict]) -> str:
    """Detect contract type from document content."""
    full_text = " ".join(p["text"] for p in paragraphs[:10]).lower()
    type_signals = {
        "purchase and sale agreement": [r'purchase\s+and\s+sale', r'purchase\s+agreement'],
        "lease": [r'\blease\b', r'\blandlord\b', r'\btenant\b', r'\brent\b'],
        "development agreement": [r'development\s+agreement', r'\bdeveloper\b'],
        "loan agreement": [r'loan\s+agreement', r'\blender\b', r'\bborrower\b', r'\bpromissory\b'],
    }
    for ctype, patterns in type_signals.items():
        for pattern in patterns:
            if re.search(pattern, full_text):
                return ctype
    return "purchase and sale agreement"


def _map_risk_categories(paragraphs: List[Dict], categories: List[str]) -> List[Dict]:
    """Map risk categories to paragraphs where they appear."""
    results = []
    for category in categories:
        signals = CATEGORY_SIGNALS.get(category, [])
        matching_paras = []
        for para in paragraphs:
            text = para["text"]
            if not text or len(text) < 20:
                continue
            for signal in signals:
                if re.search(signal, text, re.IGNORECASE):
                    matching_paras.append({
                        "para_id": para["id"],
                        "section_ref": para.get("section_ref"),
                        "text_preview": text[:150],
                    })
                    break
        results.append({
            "category": category,
            "paragraphs": matching_paras,
            "count": len(matching_paras),
        })
    return results


def format_for_display(result: Dict[str, Any]) -> str:
    """Format analysis result as readable text for Sara."""
    lines = []
    lines.append(f"Contract Analysis: {result['contract_type'].title()}")
    lines.append(f"Representation: {result['representation']}")
    s = result["summary"]
    lines.append(f"Paragraphs: {s['total_paragraphs']} | Categories found: {s['categories_identified']} | Provisions classified: {s['total_provisions_classified']}")
    lines.append("")

    lines.append("--- Risk Categories ---")
    for rc in result["risk_categories"]:
        if rc["paragraphs"]:
            lines.append(f"  {rc['category']} ({rc['count']} paragraphs)")
            for p in rc["paragraphs"][:3]:
                lines.append(f"    [{p['para_id']}] {p['text_preview'][:100]}...")
            if rc["count"] > 3:
                lines.append(f"    ... and {rc['count'] - 3} more")
    lines.append("")

    lines.append("--- Provisions by Concept ---")
    for concept, provisions in result["provisions_by_concept"].items():
        lines.append(f"  {concept}: {len(provisions)}")
    lines.append("")

    lines.append(f"--- Defined Terms ({len(result['defined_terms'])}) ---")
    for term in result["defined_terms"][:10]:
        lines.append(f"  \"{term['term']}\"")
    if len(result["defined_terms"]) > 10:
        lines.append(f"  ... and {len(result['defined_terms']) - 10} more")

    return "\n".join(lines)
```

**Step 4: Run tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/test_analyzer.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add docx-tools/core/analyzer.py docx-tools/tests/test_analyzer.py
git commit -m "feat: add core contract analyzer with risk category mapping"
```

---

### Task 8: MCP Server

**Files:**
- Create: `docx-tools/mcp_server.py`
- Modify: `.mcp.json`

**Step 1: Implement MCP server**

Create `docx-tools/mcp_server.py`:

```python
#!/usr/bin/env python3
"""
MCP server exposing docx tools for Sara.

Tools: read_docx, write_docx, redline_docx, compare_docx, extract_structure, analyze_contract
"""

import json
import sys
from pathlib import Path

# Ensure core is importable
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from core.reader import read_docx as _read_docx, format_for_display as _reader_display
from core.writer import write_docx as _write_docx
from core.redliner import redline_docx as _redline_docx
from core.comparer import compare_docx as _compare_docx, format_for_display as _comparer_display
from core.extractor import extract_structure as _extract_structure, format_for_display as _extractor_display
from core.analyzer import analyze_contract as _analyze_contract, format_for_display as _analyzer_display

mcp = FastMCP("docx-tools")


@mcp.tool()
def read_docx(docx_path: str) -> str:
    """Read and parse a .docx file. Returns structured text with paragraph IDs, section hierarchy, defined terms, and metadata."""
    result = _read_docx(docx_path)
    return _reader_display(result)


@mcp.tool()
def write_docx(content: str, output_path: str, template_path: str = "") -> str:
    """Write content to a .docx file. Content can be markdown-formatted. Optionally provide a template .docx for style inheritance."""
    tmpl = template_path if template_path else None
    path = _write_docx(content, output_path, template_path=tmpl)
    return f"Document written to: {path}"


@mcp.tool()
def redline_docx(original_path: str, revisions_json: str, output_path: str, author: str = "Sara") -> str:
    """Generate a .docx with native Word track changes. revisions_json is a JSON string mapping paragraph IDs to {\"original\": \"...\", \"revised\": \"...\"}."""
    revisions = json.loads(revisions_json)
    path = _redline_docx(original_path, revisions, output_path, author=author)
    return f"Redlined document saved to: {path}"


@mcp.tool()
def compare_docx(path_a: str, path_b: str, redline_output: str = "") -> str:
    """Compare two .docx files and return a diff report. Optionally generate a redlined .docx showing changes."""
    rl = redline_output if redline_output else None
    result = _compare_docx(path_a, path_b, redline_output=rl)
    return _comparer_display(result)


@mcp.tool()
def extract_structure(docx_path: str) -> str:
    """Extract document structure: sections, defined terms with definitions, provision types, and exhibits."""
    result = _extract_structure(docx_path)
    return _extractor_display(result)


@mcp.tool()
def analyze_contract(docx_path: str, representation: str, focus_areas: str = "") -> str:
    """Analyze a contract for risk categories and provision mapping. Returns structured output for Sara's review. focus_areas is a comma-separated list of areas to focus on (optional)."""
    areas = [a.strip() for a in focus_areas.split(",") if a.strip()] if focus_areas else None
    result = _analyze_contract(docx_path, representation, focus_areas=areas)
    return _analyzer_display(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Step 2: Update .mcp.json**

Read the existing `.mcp.json` at `/home/david/projects/AI-Associate/.mcp.json` and add the `docx-tools` server entry alongside the existing `court-listener` entry. The new entry:

```json
"docx-tools": {
  "command": "uv",
  "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}/docx-tools", "mcp_server.py"],
  "env": {}
}
```

**Step 3: Commit**

```bash
git add docx-tools/mcp_server.py .mcp.json
git commit -m "feat: add MCP server exposing all 6 docx tools"
```

---

### Task 9: CLI Scripts

**Files:**
- Create: `docx-tools/cli/read.py`
- Create: `docx-tools/cli/write.py`
- Create: `docx-tools/cli/redline.py`
- Create: `docx-tools/cli/compare.py`
- Create: `docx-tools/cli/extract.py`
- Create: `docx-tools/cli/analyze.py`

**Step 1: Create all 6 CLI scripts**

Each script uses argparse and prints results to stdout.

Create `docx-tools/cli/read.py`:

```python
#!/usr/bin/env python3
"""Read and parse a .docx file."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reader import read_docx, format_for_display

parser = argparse.ArgumentParser(description="Read and parse a .docx file")
parser.add_argument("docx_path", help="Path to the .docx file")
args = parser.parse_args()

result = read_docx(args.docx_path)
print(format_for_display(result))
```

Create `docx-tools/cli/write.py`:

```python
#!/usr/bin/env python3
"""Write content to a .docx file."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.writer import write_docx

parser = argparse.ArgumentParser(description="Write content to a .docx file")
parser.add_argument("--input", required=True, help="Path to input file (markdown/text)")
parser.add_argument("--output", required=True, help="Path for output .docx file")
parser.add_argument("--template", default=None, help="Optional template .docx for style inheritance")
args = parser.parse_args()

content = Path(args.input).read_text(encoding="utf-8")
path = write_docx(content, args.output, template_path=args.template)
print(f"Document written to: {path}")
```

Create `docx-tools/cli/redline.py`:

```python
#!/usr/bin/env python3
"""Generate a redlined .docx with track changes."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.redliner import redline_docx

parser = argparse.ArgumentParser(description="Generate a redlined .docx with track changes")
parser.add_argument("original", help="Path to the original .docx file")
parser.add_argument("--revised-text", required=True, help="Path to JSON file mapping para IDs to {original, revised}")
parser.add_argument("--output", required=True, help="Path for output .docx file")
parser.add_argument("--author", default="Sara", help="Author name for track changes")
args = parser.parse_args()

revisions = json.loads(Path(args.revised_text).read_text(encoding="utf-8"))
path = redline_docx(args.original, revisions, args.output, author=args.author)
print(f"Redlined document saved to: {path}")
```

Create `docx-tools/cli/compare.py`:

```python
#!/usr/bin/env python3
"""Compare two .docx files."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.comparer import compare_docx, format_for_display

parser = argparse.ArgumentParser(description="Compare two .docx files")
parser.add_argument("path_a", help="Path to the first .docx file")
parser.add_argument("path_b", help="Path to the second .docx file")
parser.add_argument("--redline-output", default=None, help="Optional path to write a redlined .docx")
args = parser.parse_args()

result = compare_docx(args.path_a, args.path_b, redline_output=args.redline_output)
print(format_for_display(result))
```

Create `docx-tools/cli/extract.py`:

```python
#!/usr/bin/env python3
"""Extract document structure from a .docx file."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.extractor import extract_structure, format_for_display

parser = argparse.ArgumentParser(description="Extract document structure from a .docx file")
parser.add_argument("docx_path", help="Path to the .docx file")
args = parser.parse_args()

result = extract_structure(args.docx_path)
print(format_for_display(result))
```

Create `docx-tools/cli/analyze.py`:

```python
#!/usr/bin/env python3
"""Analyze a contract for risk categories."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import analyze_contract, format_for_display

parser = argparse.ArgumentParser(description="Analyze a contract for risk categories")
parser.add_argument("docx_path", help="Path to the .docx file")
parser.add_argument("--representation", required=True, help="Who the client is (buyer, seller, tenant, etc.)")
parser.add_argument("--focus", default="", help="Comma-separated focus areas")
args = parser.parse_args()

areas = [a.strip() for a in args.focus.split(",") if a.strip()] if args.focus else None
result = analyze_contract(args.docx_path, args.representation, focus_areas=areas)
print(format_for_display(result))
```

**Step 2: Test one CLI script manually**

Run: `cd /home/david/projects/AI-Associate && uv run --directory docx-tools python docx-tools/cli/read.py --help`
Expected: Help text prints without errors

**Step 3: Commit**

```bash
git add docx-tools/cli/
git commit -m "feat: add CLI scripts for all 6 docx tools"
```

---

### Task 10: The `/docx-mode` Command

**Files:**
- Create: `commands/docx-mode.md`

**Step 1: Create the command**

Create `commands/docx-mode.md`:

```markdown
---
description: Toggle between MCP and CLI for docx tools
argument-hint: [mcp|cli]
---

Set the docx tools integration mode for this session.

Mode requested: $ARGUMENTS

If the argument is "mcp":
- Write the following to `.claude/ai-associate.local.md` (create if it doesn't exist), setting the YAML frontmatter `docx_mode` to `mcp`:
  ```yaml
  ---
  docx_mode: mcp
  ---
  ```
- Confirm: "Docx tools mode set to **MCP**. I'll use the docx-tools MCP server for all document operations."

If the argument is "cli":
- Write the following to `.claude/ai-associate.local.md` (create if it doesn't exist), setting the YAML frontmatter `docx_mode` to `cli`:
  ```yaml
  ---
  docx_mode: cli
  ---
  ```
- Confirm: "Docx tools mode set to **CLI**. I'll use Bash scripts in `docx-tools/cli/` for all document operations."

If no argument was provided (i.e., $ARGUMENTS is empty or blank):
- Read `.claude/ai-associate.local.md` if it exists and check the `docx_mode` value
- Report the current mode: "Current docx tools mode: **[mode]**" (default is `mcp` if no file exists)
```

**Step 2: Commit**

```bash
git add commands/docx-mode.md
git commit -m "feat: add /docx-mode command to toggle between MCP and CLI"
```

---

### Task 11: Update Sara's Skill and Agent Files

**Files:**
- Modify: `skills/sara-associate/SKILL.md`
- Modify: `agents/document-drafter.md`
- Modify: `agents/document-reviewer.md`

**Step 1: Add docx operations section to SKILL.md**

Add the following section to `skills/sara-associate/SKILL.md` after the "## Research Tools" section and before "## Quality Standards":

```markdown
## Document Tools — Docx Operations

Sara can read, write, redline, and compare Word documents (.docx files). Check the current docx mode by reading `.claude/ai-associate.local.md` — the `docx_mode` frontmatter value determines which interface to use. Default is `mcp`.

**Available operations:**

- **read_docx** — Parse a .docx file into structured text with paragraph IDs, section hierarchy, and defined terms
- **write_docx** — Write content (markdown) to a properly formatted .docx file. Use this for all work product that the partner needs in Word format. Accepts an optional template .docx for style matching.
- **redline_docx** — Generate a .docx with native Word track changes showing insertions and deletions. Takes the original .docx and a set of revisions keyed by paragraph ID.
- **compare_docx** — Compare two .docx files and produce a structured diff report. Optionally generates a redlined .docx showing changes.
- **extract_structure** — Extract document anatomy: sections, defined terms with definitions, provision types, exhibits. Use when you need the document's skeleton without reading every paragraph.
- **analyze_contract** — Get a structured risk category map and provision classification. Returns prompt-ready output for Sara to review with her own judgment. Specify the client's representation (buyer, seller, tenant, etc.).

**MCP mode** (default): Call tools directly by name (e.g., `read_docx`, `write_docx`).

**CLI mode**: Invoke via Bash:
- `python docx-tools/cli/read.py <path>`
- `python docx-tools/cli/write.py --input <file> --output <path>`
- `python docx-tools/cli/redline.py <original> --revised-text <json> --output <path>`
- `python docx-tools/cli/compare.py <path_a> <path_b>`
- `python docx-tools/cli/extract.py <path>`
- `python docx-tools/cli/analyze.py <path> --representation <role>`

When a partner provides a .docx file, use `read_docx` or `extract_structure` to ingest it. When producing work product, prefer `write_docx` to output as Word unless the partner specifically wants markdown.
```

**Step 2: Update document-drafter agent**

Add to the tools list in `agents/document-drafter.md` frontmatter: include a note that the drafter can use docx tools.

Add after the "**Important:**" section:

```markdown
**Docx Output:**

- When Sara asks you to draft a document, check if she wants .docx output
- If so, write your draft as markdown first, then use the write_docx tool (MCP) or `python docx-tools/cli/write.py` (CLI) to convert it
- If a template .docx was provided, pass it as the template parameter for style matching
```

**Step 3: Update document-reviewer agent**

Add after the "**Important:**" section in `agents/document-reviewer.md`:

```markdown
**Docx Input:**

- When Sara sends you a .docx file to review, use the read_docx tool (MCP) or `python docx-tools/cli/read.py` (CLI) to parse it
- For structural analysis, use extract_structure to get sections, defined terms, and provision classifications
- Reference paragraph IDs from the parsed output in your findings
```

**Step 4: Commit**

```bash
git add skills/sara-associate/SKILL.md agents/document-drafter.md agents/document-reviewer.md
git commit -m "feat: update Sara skill and agent files with docx tool references"
```

---

### Task 12: Run Full Test Suite and Verify

**Step 1: Run all tests**

Run: `cd /home/david/projects/AI-Associate/docx-tools && uv run pytest tests/ -v`
Expected: All tests PASS (approximately 20 tests across 5 test files)

**Step 2: Test MCP server starts**

Run: `cd /home/david/projects/AI-Associate/docx-tools && echo '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{}},"id":1}' | uv run python mcp_server.py`
Expected: Server responds with JSON-RPC initialize response (or starts without error)

**Step 3: Test one CLI script end-to-end**

Run: `cd /home/david/projects/AI-Associate && uv run --directory docx-tools python -c "
from docx import Document
doc = Document()
doc.add_paragraph('Test paragraph for CLI verification.')
doc.save('/tmp/test_cli.docx')
" && uv run --directory docx-tools python docx-tools/cli/read.py /tmp/test_cli.docx`

Expected: Parsed document output printed to stdout

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete docx-tools integration — core, MCP, CLI, toggle, skill updates"
```
