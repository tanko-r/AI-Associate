"""
Extract document structure from .docx files.

Returns sections, defined terms with definitions, provision classifications,
and exhibits without requiring LLM analysis.
"""

import re
from typing import Dict, Any, List

from core.reader import read_docx


# Patterns for classifying provisions
PROVISION_PATTERNS = {
    "obligation": [
        r'\bshall\b(?!\s+not)',
        r'\bmust\b',
        r'\bagrees?\s+to\b',
        r'\bcovenants?\s+to\b',
    ],
    "right": [
        r'\bmay\b(?!\s+not)',
        r'\bis\s+entitled\b',
        r'\bhas\s+the\s+(?:right|option)\b',
        r'\bshall\s+have\s+the\s+(?:right|option)\b',
    ],
    "condition": [
        r'\bsubject\s+to\b',
        r'\bprovided\s+that\b',
        r'\bconditioned?\s+upon\b',
        r'\bif\s+and\s+only\s+if\b',
    ],
    "termination": [
        r'\bterminate\b',
        r'\bcancell?(?:ation|ed)\b',
        r'\bexpir(?:e|ation)\b',
    ],
    "indemnification": [
        r'\bindemnif(?:y|ication)\b',
        r'\bhold\s+harmless\b',
        r'\bdefend\b.*\bclaims?\b',
    ],
    "representation": [
        r'\brepresents?\s+(?:and\s+warrants?|that)\b',
        r'\bwarrants?\s+(?:and\s+represents?|that)\b',
    ],
}

# Patterns for extracting defined terms with their definitions
DEFINITION_PATTERN = re.compile(
    r'["\u201c]([A-Z][^"\u201d]+)["\u201d]\s+(?:means?|shall\s+mean|refers?\s+to|is\s+defined\s+as)\s+(.+?)(?:\.(?:\s|$)|\.$)',
    re.IGNORECASE
)

# Parenthetical definitions: (the "Term")
PAREN_DEFINITION_PATTERN = re.compile(
    r'(.{10,120}?)\s+\((?:the\s+|this\s+|each,?\s+a\s+)?["\u201c]([A-Z][^"\u201d]+)["\u201d]\)',
)


def extract_structure(docx_path: str) -> Dict[str, Any]:
    """
    Extract document structure from a .docx file.

    Args:
        docx_path: Path to the .docx file.

    Returns:
        Dict with keys: sections, defined_terms, provisions, exhibits, summary.
    """
    parsed = read_docx(docx_path)
    paragraphs = [p for p in parsed["content"] if p["type"] == "paragraph"]

    sections = parsed["sections"]
    exhibits = parsed["exhibits"]

    defined_terms = _extract_defined_terms_with_definitions(paragraphs)
    provisions = _classify_provisions(paragraphs)

    return {
        "sections": sections,
        "defined_terms": defined_terms,
        "provisions": provisions,
        "exhibits": exhibits,
        "summary": {
            "total_paragraphs": len(paragraphs),
            "total_sections": len(sections),
            "total_defined_terms": len(defined_terms),
            "total_provisions": len(provisions),
            "total_exhibits": len(exhibits),
        }
    }


def _extract_defined_terms_with_definitions(paragraphs: List[Dict]) -> List[Dict]:
    """Extract defined terms and their definitions from paragraph text."""
    terms = {}

    for para in paragraphs:
        text = para["text"]
        if not text:
            continue

        # Explicit definitions: "Term" means ...
        for match in DEFINITION_PATTERN.finditer(text):
            term_name = match.group(1).strip()
            definition = match.group(2).strip()
            terms[term_name] = {
                "term": term_name,
                "definition": definition,
                "para_id": para["id"],
                "section_ref": para.get("section_ref"),
            }

        # Parenthetical definitions: ... (the "Term")
        for match in PAREN_DEFINITION_PATTERN.finditer(text):
            context = match.group(1).strip()
            term_name = match.group(2).strip()
            if term_name not in terms:
                terms[term_name] = {
                    "term": term_name,
                    "definition": context,
                    "para_id": para["id"],
                    "section_ref": para.get("section_ref"),
                }

    return sorted(terms.values(), key=lambda t: t["term"])


def _classify_provisions(paragraphs: List[Dict]) -> List[Dict]:
    """Classify paragraphs by provision type based on language patterns."""
    provisions = []

    for para in paragraphs:
        text = para["text"]
        if not text or len(text) < 30:
            continue

        matched_types = []
        for ptype, patterns in PROVISION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matched_types.append(ptype)
                    break

        if matched_types:
            provisions.append({
                "para_id": para["id"],
                "section_ref": para.get("section_ref"),
                "type": matched_types[0],  # Primary classification
                "all_types": matched_types,
                "caption": para.get("caption", ""),
                "text_preview": text[:150],
            })

    return provisions


def format_for_display(result: Dict[str, Any]) -> str:
    """Format extraction result as readable text for Sara."""
    lines = []
    s = result["summary"]
    lines.append(f"Document Structure: {s['total_paragraphs']} paragraphs, {s['total_sections']} sections")
    lines.append("")

    lines.append("--- Sections ---")
    for sec in result["sections"]:
        num = sec.get("number", "")
        title = sec.get("title", "")
        lines.append(f"  {num} {title}".strip())
    lines.append("")

    lines.append(f"--- Defined Terms ({s['total_defined_terms']}) ---")
    for term in result["defined_terms"]:
        defn = term["definition"][:100]
        lines.append(f"  \"{term['term']}\" — {defn}")
    lines.append("")

    lines.append(f"--- Provisions ({s['total_provisions']}) ---")
    type_counts = {}
    for p in result["provisions"]:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {ptype}: {count}")
    lines.append("")

    if result["exhibits"]:
        lines.append("--- Exhibits ---")
        for ex in result["exhibits"]:
            lines.append(f"  {ex['title']}")

    return "\n".join(lines)
