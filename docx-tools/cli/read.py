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
