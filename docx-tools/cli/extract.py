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
