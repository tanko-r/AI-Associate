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
from core.scanner import scan_document as _scan_document, format_for_display as _scanner_display

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
    """Generate a .docx with native Word track changes. revisions_json is a JSON string mapping paragraph IDs to {"original": "...", "revised": "..."}."""
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


@mcp.tool()
def scan_document(docx_path: str) -> str:
    """Scan a .docx for unfilled placeholders and missing exhibit/schedule references. Use during QC review."""
    result = _scan_document(docx_path)
    return _scanner_display(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
