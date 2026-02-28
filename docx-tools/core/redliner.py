"""
Generate .docx files with native Word track changes.

Applies revisions to a document using Word's revision markup (w:ins, w:del)
so changes display correctly in Microsoft Word's track changes view.
"""

import re
import shutil
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import diff_match_patch as dmp_module
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.inserter import find_paragraph_element


@dataclass
class CharFormatInfo:
    """Maps a character position to its source run's formatting."""
    run_index: int
    rpr_element: Optional[OxmlElement]


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
    """Apply track changes to a single paragraph using Word revision markup.

    Uses per-character formatting map to preserve each run's original <w:rPr>,
    so bold/italic/font changes within a paragraph survive the diff rebuild.
    """
    # Build char map BEFORE any mutations
    char_map = _build_char_format_map(paragraph)

    # Run diff
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(original_text, revised_text)
    dmp.diff_cleanupSemantic(diffs)

    # Clear existing runs
    p = paragraph._p
    for child in list(p):
        if child.tag == qn('w:r'):
            p.remove(child)

    rev_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    orig_pos = 0  # cursor into char_map (tracks position in original text)

    for op, text in diffs:
        if op == 0:  # Equal — text exists in both original and revised
            segments = _split_segment_by_runs(text, orig_pos, char_map)
            for sub_text, rpr in segments:
                run = _make_run_from_rpr(sub_text, rpr)
                p.append(run)
            orig_pos += len(text)

        elif op == -1:  # Deletion — text from original, not in revised
            segments = _split_segment_by_runs(text, orig_pos, char_map)
            for sub_text, rpr in segments:
                del_elem = OxmlElement('w:del')
                del_elem.set(qn('w:id'), str(abs(hash(sub_text + str(orig_pos))) % 100000))
                del_elem.set(qn('w:author'), author)
                del_elem.set(qn('w:date'), rev_date)
                run = _make_run_from_rpr(sub_text, rpr, is_delete=True)
                del_elem.append(run)
                p.append(del_elem)
            orig_pos += len(text)

        elif op == 1:  # Insertion — new text not in original
            # Inherit formatting from the character just before insertion point
            if char_map and orig_pos > 0:
                insert_rpr = char_map[orig_pos - 1].rpr_element
            elif char_map:
                insert_rpr = char_map[0].rpr_element
            else:
                insert_rpr = None

            ins_elem = OxmlElement('w:ins')
            ins_elem.set(qn('w:id'), str(abs(hash(text)) % 100000))
            ins_elem.set(qn('w:author'), author)
            ins_elem.set(qn('w:date'), rev_date)
            run = _make_run_from_rpr(text, insert_rpr)
            ins_elem.append(run)
            p.append(ins_elem)
            # Do NOT advance orig_pos — insertions don't consume original text


def _build_char_format_map(paragraph) -> List[CharFormatInfo]:
    """
    Build a per-character map from paragraph text positions to source run formatting.

    Returns a list where each index corresponds to a character in the paragraph's
    concatenated text. Each entry holds the run_index and a deepcopy'd <w:rPr>
    element (or None if the run has no explicit formatting).

    Callers that need to modify an rpr_element must deepcopy it again — the same
    object is shared across all characters within a single run for efficiency.
    """
    char_map: List[CharFormatInfo] = []
    p = paragraph._p
    run_elements = p.findall(qn("w:r"))

    for run_idx, run_el in enumerate(run_elements):
        rpr = run_el.find(qn("w:rPr"))
        rpr_copy = deepcopy(rpr) if rpr is not None else None

        for t_el in run_el.findall(qn("w:t")):
            text = t_el.text or ""
            for _ in text:
                char_map.append(CharFormatInfo(run_index=run_idx, rpr_element=rpr_copy))

    return char_map


def _split_segment_by_runs(
    text: str, start_pos: int, char_map: List[CharFormatInfo]
) -> list:
    """
    Split a diff segment into sub-segments aligned to original run boundaries.

    Returns a list of (sub_text, rpr_element) tuples, where each tuple covers
    a contiguous span of characters that belonged to the same original run.

    If start_pos >= len(char_map) (e.g. for pure insertions with no original
    mapping), the entire text is returned with the last known rpr_element.
    """
    if not text:
        return []

    # Fallback when the segment is beyond the char_map (pure insertion)
    if start_pos >= len(char_map):
        last_rpr = char_map[-1].rpr_element if char_map else None
        return [(text, last_rpr)]

    segments: list = []
    current_start = 0
    current_run_idx = char_map[start_pos].run_index
    current_rpr = char_map[start_pos].rpr_element

    for offset in range(1, len(text)):
        pos = start_pos + offset
        if pos >= len(char_map):
            # Remaining chars extend past the map — keep current formatting
            break
        if char_map[pos].run_index != current_run_idx:
            segments.append((text[current_start:offset], current_rpr))
            current_start = offset
            current_run_idx = char_map[pos].run_index
            current_rpr = char_map[pos].rpr_element

    # Final segment
    segments.append((text[current_start:], current_rpr))
    return segments


def _make_run_from_rpr(
    text: str, rpr_element=None, is_delete: bool = False
):
    """
    Create a <w:r> element using a deepcopy'd <w:rPr> XML element.

    Preserves full XML fidelity by copying the original run's entire <w:rPr>
    element — including color, highlight, character styles, superscript,
    complex script properties, and any other attributes.

    Args:
        text: The text content for the run.
        rpr_element: An lxml <w:rPr> element to deepcopy into the run,
                     or None to omit rPr (preserves style inheritance).
        is_delete: If True, use <w:delText> instead of <w:t>.
    """
    run = OxmlElement("w:r")

    if rpr_element is not None:
        run.append(deepcopy(rpr_element))

    if is_delete:
        t = OxmlElement("w:delText")
    else:
        t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
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
