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
