"""Generate INDEX.md files for playbook directories.

Reads all 15 playbook topic files from seller-side and buyer-side directories,
extracts H2 subtopics and their Risk Assessment subsections, and produces
a compact INDEX.md summary for each side.
"""

import re
from pathlib import Path

# Topic-to-checklist-category mapping (from contract-review-workflow.md)
TOPIC_CATEGORIES = {
    "01": "1 (Definitions), 2 (Property Description)",
    "02": "3 (Purchase Price and Deposits)",
    "03": "4 (Due Diligence and Inspections)",
    "04": "5 (Title and Survey)",
    "05": "6 (Representations and Warranties)",
    "06": "7 (Covenants and Interim Operations)",
    "07": "8 (Conditions Precedent)",
    "08": "17 (Tenant Estoppels and SNDAs)",
    "09": "9 (Closing Mechanics), 10 (Closing Deliverables)",
    "10": "11 (Prorations and Adjustments)",
    "11": "12 (Casualty and Condemnation)",
    "12": "13 (Default and Remedies)",
    "13": "15 (Indemnification and Survival)",
    "14": "16 (Assignment and Transfer)",
    "15": "18 (Governing Law and Dispute Resolution), 19 (Notices), 20 (Miscellaneous), 24 (Exhibits and Schedules)",
}


def parse_playbook_file(filepath: Path) -> dict:
    """Parse a playbook .md file, extracting H2 subtopics and their Risk Assessment."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Extract H1 title
    title = ""
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            break

    # Parse H2 sections and their Risk Assessments
    subtopics = []
    current_h2 = None
    current_h3 = None
    risk_lines = []
    in_risk_section = False

    for line in lines:
        # Detect H2 headings
        if line.startswith("## ") and not line.startswith("### "):
            # Save previous subtopic's risk if we have one
            if current_h2 is not None:
                risk_text = _extract_risk_summary(risk_lines)
                subtopics.append({"name": current_h2, "risk": risk_text})

            current_h2 = line[3:].strip()
            # Strip leading number prefix like "1. " or "14. "
            current_h2 = re.sub(r"^\d+\.\s*", "", current_h2)
            current_h3 = None
            risk_lines = []
            in_risk_section = False

        # Detect H3 headings
        elif line.startswith("### "):
            h3_text = line[4:].strip()
            current_h3 = h3_text
            in_risk_section = h3_text.lower().startswith("risk assessment")

        # Collect lines in Risk Assessment section
        elif in_risk_section:
            stripped = line.strip()
            if stripped:
                risk_lines.append(stripped)

    # Don't forget the last subtopic
    if current_h2 is not None:
        risk_text = _extract_risk_summary(risk_lines)
        subtopics.append({"name": current_h2, "risk": risk_text})

    return {"title": title, "subtopics": subtopics}


def _extract_risk_summary(risk_lines: list[str]) -> tuple[str, str]:
    """Extract severity and one-sentence summary from Risk Assessment lines.

    Returns (severity, summary). Risk Assessment lines typically start with
    **HIGH**, **MEDIUM**, **LOW**, **CRITICAL**, or bold-formatted severity.
    """
    if not risk_lines:
        return ("—", "No risk assessment provided")

    first_line = risk_lines[0]

    # Match patterns like "**HIGH** — description" or "**High risk**: description"
    severity_match = re.match(
        r"\*\*(\w+?)(?:\s+risk)?\*\*[\s:—–-]+(.+)", first_line, re.IGNORECASE
    )
    if severity_match:
        severity = severity_match.group(1).upper()
        summary = severity_match.group(2).strip()
        # Truncate to first sentence
        summary = _first_sentence(summary)
        return (severity, summary)

    # Fallback: try to find severity keyword anywhere in first line
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if level.lower() in first_line.lower():
            # Strip the severity word and clean up
            summary = re.sub(
                rf"\*?\*?{level}\*?\*?[\s:—–-]*",
                "",
                first_line,
                flags=re.IGNORECASE,
            ).strip()
            summary = _first_sentence(summary) if summary else first_line
            return (level, summary)

    # Last resort
    return ("—", _first_sentence(first_line))


def _first_sentence(text: str) -> str:
    """Return the first sentence of text, capped at ~120 chars."""
    # Remove markdown bold markers for clean output
    text = text.replace("**", "")
    # Find first sentence boundary
    match = re.match(r"(.+?[.!?])(?:\s|$)", text)
    if match:
        sentence = match.group(1)
        if len(sentence) <= 150:
            return sentence
    # If no sentence boundary or too long, truncate
    if len(text) > 120:
        return text[:117] + "..."
    return text


def generate_index(side_dir: Path, side_label: str) -> str:
    """Generate INDEX.md content for a playbook side directory."""
    files = sorted(side_dir.glob("*.md"))

    # Filter out any existing INDEX.md
    files = [f for f in files if f.name.upper() != "INDEX.MD"]

    output_lines = [
        f"# Playbook Index — {side_label.replace('-', ' ').title()}",
        "",
        f"Compact summary of all {len(files)} playbook topics for {side_label.replace('-', ' ')} PSA review.",
        "Use this index to determine which topics are relevant to the current document.",
        "Full topic files are loaded during delegation (Step 6b) — not at framework time.",
        "",
        "---",
        "",
    ]

    for filepath in files:
        # Extract topic number from filename
        topic_num = filepath.stem[:2]
        categories = TOPIC_CATEGORIES.get(topic_num, "—")

        parsed = parse_playbook_file(filepath)
        topic_title = parsed["title"]

        # Clean title: remove suffixes like " — Seller Playbook", " -- Seller's Playbook",
        # " -- Seller Side Playbook", " -- Buyer Side Playbook", etc.
        topic_title = re.sub(
            r"\s*[-—–]+\s*Seller'?s?\s*(Side\s*)?Playbook\s*$", "", topic_title
        )
        topic_title = re.sub(
            r"\s*[-—–]+\s*Buyer'?s?\s*(Side\s*)?Playbook\s*$", "", topic_title
        )
        # Remove "Section NN:" prefix (some files use this inconsistently)
        topic_title = re.sub(r"^Section\s+\d+:\s*", "", topic_title)

        output_lines.append(f"## {topic_num} — {topic_title}")
        output_lines.append(f"**Checklist categories:** {categories}")
        output_lines.append(f"**File:** `{filepath.name}`")
        output_lines.append("")

        if parsed["subtopics"]:
            output_lines.append("| Subtopic | Risk | Summary |")
            output_lines.append("|----------|------|---------|")
            for st in parsed["subtopics"]:
                severity, summary = st["risk"]
                name = st["name"]
                output_lines.append(f"| {name} | {severity} | {summary} |")
            output_lines.append("")

        output_lines.append("---")
        output_lines.append("")

    return "\n".join(output_lines)


def main():
    base = Path(__file__).resolve().parent.parent / "skills" / "sara" / "references" / "playbook"

    for side in ["seller-side", "buyer-side"]:
        side_dir = base / side
        if not side_dir.exists():
            print(f"WARNING: {side_dir} does not exist, skipping")
            continue

        index_content = generate_index(side_dir, side)
        index_path = side_dir / "INDEX.md"
        index_path.write_text(index_content, encoding="utf-8")

        # Count lines and topics
        line_count = index_content.count("\n") + 1
        topic_count = index_content.count("\n## ")
        print(f"Generated {index_path}")
        print(f"  {topic_count} topics, {line_count} lines")


if __name__ == "__main__":
    main()
