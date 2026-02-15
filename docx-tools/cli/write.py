#!/usr/bin/env python3
"""Write content to a .docx file."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.writer import write_docx

parser = argparse.ArgumentParser(description="Write content to a .docx file")
parser.add_argument("--input", required=True, help="Path to input file (markdown/text)")
parser.add_argument("--output", required=True, help="Path for output .docx file")
parser.add_argument("--template", default=None, help="Optional template .docx for style inheritance")
args = parser.parse_args()

content = Path(args.input).read_text(encoding="utf-8")
path = write_docx(content, args.output, template_path=args.template)
print(f"Document written to: {path}")
