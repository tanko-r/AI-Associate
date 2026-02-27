"""
Paragraph positioning: find, insert after, and remove paragraphs by ID.

Uses the same sequential counting logic as reader.py and redliner.py:
body-level <w:p> elements are counted first, then within each <w:tbl>
the paragraphs in every cell are counted in row/cell/paragraph order.
"""

from copy import deepcopy
from typing import Optional

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _iter_paragraphs_with_id(doc: Document):
    """
    Yield (para_id_str, lxml_element) for every paragraph in the document,
    following the same counting order as reader.py and redliner.py.
    """
    body = doc.element.body
    para_id = 0

    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            para_id += 1
            yield f"p_{para_id}", child
        elif child.tag == qn("w:tbl"):
            # Walk rows -> cells -> paragraphs inside the table
            for tr in child.findall(qn("w:tr")):
                for tc in tr.findall(qn("w:tc")):
                    for p in tc.findall(qn("w:p")):
                        para_id += 1
                        yield f"p_{para_id}", p


def find_paragraph_element(doc: Document, para_id: str) -> Optional[object]:
    """
    Find a paragraph's raw lxml <w:p> element by its sequential ID.

    Args:
        doc: An open python-docx Document.
        para_id: Paragraph ID string like "p_1", "p_2", etc.

    Returns:
        The lxml <w:p> element, or None if not found.
    """
    for pid, elem in _iter_paragraphs_with_id(doc):
        if pid == para_id:
            return elem
    return None


def insert_paragraph_after(
    doc: Document,
    target_para_id: str,
    text: str,
    style_source_id: Optional[str] = None,
) -> Optional[object]:
    """
    Insert a new paragraph immediately after the target paragraph.

    The new paragraph copies formatting (pPr, rPr) from the style source
    paragraph (or the target paragraph if no style source is specified).

    Args:
        doc: An open python-docx Document.
        target_para_id: ID of the paragraph to insert after.
        text: Text content for the new paragraph.
        style_source_id: Optional ID of a paragraph to copy formatting from.
                         Defaults to the target paragraph.

    Returns:
        The new lxml <w:p> element, or None if the target was not found.
    """
    target_elem = find_paragraph_element(doc, target_para_id)
    if target_elem is None:
        return None

    # Determine the style source element
    if style_source_id is not None:
        style_source = find_paragraph_element(doc, style_source_id)
        if style_source is None:
            style_source = target_elem
    else:
        style_source = target_elem

    # Build the new <w:p> element
    new_p = OxmlElement("w:p")

    # Copy paragraph properties (w:pPr) from style source
    source_pPr = style_source.find(qn("w:pPr"))
    if source_pPr is not None:
        new_p.append(deepcopy(source_pPr))

    # Build a run with the text
    new_r = OxmlElement("w:r")

    # Copy run properties (w:rPr) from the first run of the style source
    first_run = style_source.find(qn("w:r"))
    if first_run is not None:
        source_rPr = first_run.find(qn("w:rPr"))
        if source_rPr is not None:
            new_r.append(deepcopy(source_rPr))

    # Add the text element
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    new_r.append(t)
    new_p.append(new_r)

    # Insert after the target using lxml's addnext
    target_elem.addnext(new_p)

    return new_p


def remove_paragraph(doc: Document, para_id: str) -> bool:
    """
    Remove a paragraph from the document by its sequential ID.

    Args:
        doc: An open python-docx Document.
        para_id: ID of the paragraph to remove.

    Returns:
        True if the paragraph was found and removed, False otherwise.
    """
    elem = find_paragraph_element(doc, para_id)
    if elem is None:
        return False

    parent = elem.getparent()
    parent.remove(elem)
    return True
