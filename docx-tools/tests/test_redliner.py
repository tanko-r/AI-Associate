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


def test_redline_insert_after(original_docx, tmp_path):
    """Insert a new paragraph after p_1 with tracked changes."""
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "action": "insert_after",
            "text": "Seller shall provide all closing documents five (5) days prior to Closing.",
        }
    }
    output_path = tmp_path / "inserted.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()
    doc = Document(str(output_path))
    assert len(doc.paragraphs) == 4
    # Text inside <w:ins> is not visible via python-docx's .text property,
    # so we extract all text from the XML body (including tracked changes).
    all_xml_text = "".join(doc.element.body.itertext())
    assert "closing documents" in all_xml_text


def test_redline_insert_after_has_tracking_markup(original_docx, tmp_path):
    """Verify insert_after wraps content in w:ins."""
    from core.redliner import redline_docx
    from docx.oxml.ns import qn
    revisions = {
        "p_1": {
            "action": "insert_after",
            "text": "New provision here.",
        }
    }
    output_path = tmp_path / "tracked_insert.docx"
    redline_docx(str(original_docx), revisions, str(output_path))
    doc = Document(str(output_path))
    body = doc.element.body
    ins_elements = body.findall(f".//{qn('w:ins')}")
    assert len(ins_elements) > 0


def test_redline_delete_paragraph(original_docx, tmp_path):
    """Delete p_2 with tracked changes."""
    from core.redliner import redline_docx
    from docx.oxml.ns import qn
    revisions = {
        "p_2": {"action": "delete"}
    }
    output_path = tmp_path / "deleted.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()
    doc = Document(str(output_path))
    body = doc.element.body
    del_elements = body.findall(f".//{qn('w:del')}")
    assert len(del_elements) > 0


def test_redline_mixed_actions(original_docx, tmp_path):
    """Replace p_1, insert after p_2, delete p_3 — all in one pass."""
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "original": "The Seller shall deliver the Property on the Closing Date.",
            "revised": "The Seller shall deliver the Property on or before the Closing Date.",
        },
        "p_2": {
            "action": "insert_after",
            "text": "Buyer acknowledges receipt of all disclosures.",
        },
        "p_3": {"action": "delete"},
    }
    output_path = tmp_path / "mixed.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()
    doc = Document(str(output_path))
    # 3 original + 1 inserted = 4 paragraphs (delete keeps para with markup)
    assert len(doc.paragraphs) == 4


def test_redline_backward_compatible(original_docx, tmp_path):
    """Existing format without 'action' key still works as replace."""
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "original": "The Seller shall deliver the Property on the Closing Date.",
            "revised": "The Seller shall deliver the Property on or before the Closing Date."
        }
    }
    output_path = tmp_path / "compat.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()
