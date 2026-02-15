#!/usr/bin/env python3
"""Compare two .docx files."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.comparer import compare_docx, format_for_display

parser = argparse.ArgumentParser(description="Compare two .docx files")
parser.add_argument("path_a", help="Path to the first .docx file")
parser.add_argument("path_b", help="Path to the second .docx file")
parser.add_argument("--redline-output", default=None, help="Optional path to write a redlined .docx")
args = parser.parse_args()

result = compare_docx(args.path_a, args.path_b, redline_output=args.redline_output)
print(format_for_display(result))
