"""
Generate .docx files with native Word track changes.

Applies revisions to a document using Word's revision markup (w:ins, w:del)
so changes display correctly in Microsoft Word's track changes view.
"""

import re
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict

import diff_match_patch as dmp_module
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.inserter import find_paragraph_element


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

    # ------------------------------------------------------------------
    # Bucket revisions by action type
    # ------------------------------------------------------------------
    replacements: Dict[str, dict] = {}
    deletions: Dict[str, dict] = {}
    insertions: Dict[str, dict] = {}

    for para_key, rev in revisions.items():
        action = rev.get("action", "replace")
        if action == "replace":
            replacements[para_key] = rev
        elif action == "delete":
            deletions[para_key] = rev
        elif action == "insert_after":
            insertions[para_key] = rev

    # ------------------------------------------------------------------
    # 1) Replacements — existing behaviour, iterate body blocks in order
    # ------------------------------------------------------------------
    if replacements:
        para_id = 0
        for block in _iter_block_items(doc):
            if isinstance(block, Paragraph):
                para_id += 1
                para_key = f"p_{para_id}"
                if para_key in replacements:
                    rev = replacements[para_key]
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
                            if para_key in replacements:
                                rev = replacements[para_key]
                                original_text = rev.get("original", "")
                                revised_text = rev.get("revised", "")
                                if original_text != revised_text:
                                    _apply_track_changes(para, original_text, revised_text, author)

    # ------------------------------------------------------------------
    # 2) Deletions — mark existing paragraph runs as tracked deletions
    # ------------------------------------------------------------------
    for para_key in deletions:
        _apply_tracked_deletion(doc, para_key, author)

    # ------------------------------------------------------------------
    # 3) Insertions — process in reverse para order to maintain positions
    # ------------------------------------------------------------------
    for para_key in sorted(insertions, key=_para_sort_key, reverse=True):
        rev = insertions[para_key]
        _apply_tracked_insertion(doc, para_key, rev["text"], author)

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


# ------------------------------------------------------------------
# Helpers for insert_after / delete actions
# ------------------------------------------------------------------

def _para_sort_key(para_key: str) -> int:
    """Extract the numeric part of a paragraph ID for sorting (e.g., 'p_12' -> 12)."""
    m = re.search(r"\d+", para_key)
    return int(m.group()) if m else 0


def _apply_tracked_deletion(doc: Document, para_key: str, author: str):
    """
    Mark every run in the paragraph as a tracked deletion.

    Each existing <w:r> is wrapped in a <w:del> element and its <w:t>
    children are converted to <w:delText>, so Word shows the paragraph
    with strikethrough in Track Changes view.  The paragraph itself is
    preserved (not removed) to keep numbering stable.
    """
    p = find_paragraph_element(doc, para_key)
    if p is None:
        return

    rev_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Collect existing runs (snapshot the list to avoid mutation issues)
    runs = list(p.findall(qn("w:r")))
    for run in runs:
        # Convert every <w:t> inside the run to <w:delText>
        for t in run.findall(qn("w:t")):
            del_text = OxmlElement("w:delText")
            del_text.set(qn("xml:space"), "preserve")
            del_text.text = t.text or ""
            run.replace(t, del_text)

        # Wrap the run in a <w:del> element
        del_elem = OxmlElement("w:del")
        del_elem.set(qn("w:id"), str(abs(hash(para_key)) % 100000))
        del_elem.set(qn("w:author"), author)
        del_elem.set(qn("w:date"), rev_date)

        # Replace run in its parent with the del wrapper containing the run
        run.addnext(del_elem)
        p.remove(run)
        del_elem.append(run)


def _apply_tracked_insertion(doc: Document, para_key: str, text: str, author: str):
    """
    Insert a new paragraph after *para_key* with tracked-insertion markup.

    The new paragraph copies <w:pPr> and the first run's <w:rPr> from the
    target so it inherits formatting.  The run is wrapped in <w:ins> so
    Word displays it as a tracked insertion.
    """
    target = find_paragraph_element(doc, para_key)
    if target is None:
        return

    rev_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build the new <w:p>
    new_p = OxmlElement("w:p")

    # Copy paragraph properties from target
    source_pPr = target.find(qn("w:pPr"))
    if source_pPr is not None:
        new_p.append(deepcopy(source_pPr))

    # Build a run with copied formatting
    new_r = OxmlElement("w:r")
    first_run = target.find(qn("w:r"))
    if first_run is not None:
        source_rPr = first_run.find(qn("w:rPr"))
        if source_rPr is not None:
            new_r.append(deepcopy(source_rPr))

    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    new_r.append(t)

    # Wrap the run in <w:ins>
    ins_elem = OxmlElement("w:ins")
    ins_elem.set(qn("w:id"), str(abs(hash(text)) % 100000))
    ins_elem.set(qn("w:author"), author)
    ins_elem.set(qn("w:date"), rev_date)
    ins_elem.append(new_r)

    new_p.append(ins_elem)

    # Position after the target paragraph
    target.addnext(new_p)
