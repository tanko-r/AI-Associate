#!/usr/bin/env python3
"""Analyze a contract for risk categories."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import analyze_contract, format_for_display

parser = argparse.ArgumentParser(description="Analyze a contract for risk categories")
parser.add_argument("docx_path", help="Path to the .docx file")
parser.add_argument("--representation", required=True, help="Who the client is (buyer, seller, tenant, etc.)")
parser.add_argument("--focus", default="", help="Comma-separated focus areas")
args = parser.parse_args()

areas = [a.strip() for a in args.focus.split(",") if a.strip()] if args.focus else None
result = analyze_contract(args.docx_path, args.representation, focus_areas=areas)
print(format_for_display(result))
