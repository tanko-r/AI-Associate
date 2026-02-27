"""
Scan .docx documents for unfilled placeholders and missing cross-references.

Detects dollar blanks, entry fields, TBD/TBA markers, XX placeholders,
blank brackets, and underscore runs — with signature block exclusion for
underscore patterns.
"""

import re
from typing import Any, Dict, List

from core.reader import read_docx


# ---------------------------------------------------------------------------
# Placeholder patterns
# ---------------------------------------------------------------------------

_PATTERNS: List[Dict[str, Any]] = [
    {"name": "dollar_blank",    "regex": re.compile(r'\$[_\s]{2,}')},
    {"name": "entry_field",     "regex": re.compile(
        r'\[(?:enter|insert|amount|name|date|address|number)[^\]]*\]', re.IGNORECASE)},
    {"name": "tbd",             "regex": re.compile(r'\bTBD\b')},
    {"name": "tba",             "regex": re.compile(r'\bTBA\b')},
    {"name": "xx_placeholder",  "regex": re.compile(r'\bX{2,}\b')},
    {"name": "blank_brackets",  "regex": re.compile(r'\[\s*\]|\[_{2,}\]')},
    {"name": "underscores",     "regex": re.compile(r'_{4,}')},
]

# ---------------------------------------------------------------------------
# Signature block detection helpers
# ---------------------------------------------------------------------------

_SIG_HEADER_RE = re.compile(
    r'\b(IN\s+WITNESS\s+WHEREOF|SIGNATURES?|EXECUTION|COUNTERPARTS)\b',
    re.IGNORECASE,
)

_SIG_INDICATORS = re.compile(
    r'^(By|Name|Title|Date|Printed\s+Name|Its)\s*:', re.IGNORECASE
)


def _detect_signature_start(paragraphs: List[Dict[str, Any]]) -> int | None:
    """Return the index of the earliest paragraph that begins a signature region.

    A signature region starts at either:
    - A paragraph matching a signature header keyword, or
    - The first paragraph of a cluster of 3+ signature indicators within
      5 consecutive paragraphs.

    Returns the paragraph *index* (into the list), or None if no signature
    region is found.
    """
    earliest: int | None = None

    for i, para in enumerate(paragraphs):
        text = para.get("text", "")
        if _SIG_HEADER_RE.search(text):
            if earliest is None or i < earliest:
                earliest = i

    # Cluster detection: sliding window of 5 paragraphs
    for i in range(len(paragraphs)):
        window_end = min(i + 5, len(paragraphs))
        indicator_count = 0
        for j in range(i, window_end):
            text = paragraphs[j].get("text", "").strip()
            if _SIG_INDICATORS.match(text):
                indicator_count += 1
        if indicator_count >= 3:
            if earliest is None or i < earliest:
                earliest = i

    return earliest


def _text_context(text: str, match: re.Match, radius: int = 20) -> str:
    """Return ~40 chars of context around the match."""
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    ctx = text[start:end]
    if start > 0:
        ctx = "..." + ctx
    if end < len(text):
        ctx = ctx + "..."
    return ctx


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_placeholders(docx_path: str) -> List[Dict[str, Any]]:
    """Scan a .docx for unfilled placeholder patterns.

    Returns a list of findings, each with keys:
        para_id, section_ref, text_context, pattern_type, match
    """
    parsed = read_docx(docx_path)
    paragraphs = [item for item in parsed.get("content", []) if item.get("type") == "paragraph"]

    sig_start = _detect_signature_start(paragraphs)

    findings: List[Dict[str, Any]] = []

    for idx, para in enumerate(paragraphs):
        text = para.get("text", "")
        if not text:
            continue

        in_signature = sig_start is not None and idx >= sig_start

        for pat in _PATTERNS:
            # Skip underscore patterns inside signature blocks
            if pat["name"] == "underscores" and in_signature:
                continue

            for m in pat["regex"].finditer(text):
                # If this underscore run is part of a dollar_blank, skip it
                # to avoid double-reporting
                if pat["name"] == "underscores":
                    # Check whether a dollar_blank pattern covers this span
                    dollar_re = _PATTERNS[0]["regex"]  # dollar_blank
                    skip = False
                    for dm in dollar_re.finditer(text):
                        if dm.start() <= m.start() and dm.end() >= m.end():
                            skip = True
                            break
                    if skip:
                        continue

                findings.append({
                    "para_id": para.get("id", ""),
                    "section_ref": para.get("section_ref", ""),
                    "text_context": _text_context(text, m),
                    "pattern_type": pat["name"],
                    "match": m.group(),
                })

    return findings


def scan_references(docx_path: str) -> Dict[str, Any]:
    """Scan a .docx for exhibit/schedule/annex/appendix/attachment references.

    Returns dict with keys: defined, referenced, missing.
    """
    parsed = read_docx(docx_path)
    paragraphs = [item for item in parsed.get("content", []) if item.get("type") == "paragraph"]

    ref_re = re.compile(
        r'(Exhibit|Schedule|Annex|Appendix|Attachment)\s+([A-Z0-9]+)',
        re.IGNORECASE,
    )
    # Definitions: paragraphs starting with the label in title position
    def_re = re.compile(
        r'^\s*(EXHIBIT|SCHEDULE|ANNEX|APPENDIX|ATTACHMENT)\s+([A-Z0-9]+)',
        re.IGNORECASE,
    )

    referenced: set = set()
    defined: set = set()

    for para in paragraphs:
        text = para.get("text", "")
        if not text:
            continue

        for m in ref_re.finditer(text):
            label = m.group(1).title() + " " + m.group(2).upper()
            referenced.add(label)

        dm = def_re.match(text)
        if dm:
            label = dm.group(1).title() + " " + dm.group(2).upper()
            defined.add(label)

    missing = sorted(referenced - defined)

    return {
        "defined": sorted(defined),
        "referenced": sorted(referenced),
        "missing": missing,
    }


def scan_document(docx_path: str) -> Dict[str, Any]:
    """Run all scanners and return a combined report."""
    placeholders = scan_placeholders(docx_path)
    references = scan_references(docx_path)

    return {
        "placeholders": placeholders,
        "references": references,
        "summary": {
            "placeholder_count": len(placeholders),
            "missing_reference_count": len(references.get("missing", [])),
        },
    }


def format_for_display(report: Dict[str, Any]) -> str:
    """Format a scan report as readable text."""
    lines: List[str] = []

    summary = report.get("summary", {})
    ph_count = summary.get("placeholder_count", 0)
    mr_count = summary.get("missing_reference_count", 0)

    lines.append("=== Document Scan Report ===")
    lines.append(f"Placeholders found: {ph_count}")
    lines.append(f"Missing references: {mr_count}")
    lines.append("")

    # Placeholders section
    placeholders = report.get("placeholders", [])
    if placeholders:
        lines.append("--- Placeholders ---")
        for f in placeholders:
            sec = f.get("section_ref") or "n/a"
            lines.append(
                f"  [{f['para_id']}] (sec {sec}) {f['pattern_type']}: "
                f"\"{f['match']}\"  ...{f['text_context']}..."
            )
        lines.append("")

    # References section
    refs = report.get("references", {})
    defined = refs.get("defined", [])
    referenced = refs.get("referenced", [])
    missing = refs.get("missing", [])

    if referenced:
        lines.append("--- References ---")
        lines.append(f"  Referenced: {', '.join(referenced)}")
        lines.append(f"  Defined:    {', '.join(defined) if defined else '(none)'}")
        if missing:
            lines.append(f"  MISSING:    {', '.join(missing)}")
        lines.append("")

    if ph_count == 0 and mr_count == 0:
        lines.append("No issues found.")

    return "\n".join(lines)
