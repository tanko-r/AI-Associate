#!/usr/bin/env python3
"""Generate a redlined .docx with track changes."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.redliner import redline_docx

parser = argparse.ArgumentParser(description="Generate a redlined .docx with track changes")
parser.add_argument("original", help="Path to the original .docx file")
parser.add_argument("--revised-text", required=True, help="Path to JSON file mapping para IDs to {original, revised}")
parser.add_argument("--output", required=True, help="Path for output .docx file")
parser.add_argument("--author", default="Sara", help="Author name for track changes")
args = parser.parse_args()

revisions = json.loads(Path(args.revised_text).read_text(encoding="utf-8"))
path = redline_docx(args.original, revisions, args.output, author=args.author)
print(f"Redlined document saved to: {path}")
