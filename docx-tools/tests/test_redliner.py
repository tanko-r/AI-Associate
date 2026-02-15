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
