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
