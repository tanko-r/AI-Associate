"""
Compare two .docx files and produce a structured diff report.

Optionally generates a redlined .docx showing the differences.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

import diff_match_patch as dmp_module

from core.reader import read_docx
from core.redliner import redline_docx


def compare_docx(
    path_a: str,
    path_b: str,
    redline_output: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compare two .docx files and return a structured diff report.

    Args:
        path_a: Path to the first (original) .docx file.
        path_b: Path to the second (revised) .docx file.
        redline_output: Optional path to write a redlined .docx showing changes.

    Returns:
        Dict with keys: summary, changes, and optionally redline_path.
    """
    parsed_a = read_docx(path_a)
    parsed_b = read_docx(path_b)

    paras_a = [p for p in parsed_a["content"] if p["type"] == "paragraph"]
    paras_b = [p for p in parsed_b["content"] if p["type"] == "paragraph"]

    dmp = dmp_module.diff_match_patch()
    changes: List[Dict[str, Any]] = []
    revisions_for_redline: Dict[str, Dict[str, str]] = {}

    max_len = max(len(paras_a), len(paras_b))
    for i in range(max_len):
        if i < len(paras_a) and i < len(paras_b):
            text_a = paras_a[i]["text"]
            text_b = paras_b[i]["text"]
            para_id = paras_a[i]["id"]
            section_ref = paras_a[i].get("section_ref")

            if text_a != text_b:
                diffs = dmp.diff_main(text_a, text_b)
                dmp.diff_cleanupSemantic(diffs)
                changes.append({
                    "type": "modified",
                    "para_id": para_id,
                    "section_ref": section_ref,
                    "original": text_a,
                    "revised": text_b,
                    "diff": _format_diff(diffs),
                })
                revisions_for_redline[para_id] = {
                    "original": text_a,
                    "revised": text_b,
                }
        elif i < len(paras_a):
            changes.append({
                "type": "deleted",
                "para_id": paras_a[i]["id"],
                "section_ref": paras_a[i].get("section_ref"),
                "text": paras_a[i]["text"],
            })
        else:
            changes.append({
                "type": "added",
                "para_id": f"new_{i}",
                "text": paras_b[i]["text"],
            })

    result: Dict[str, Any] = {
        "summary": {
            "total_changes": len(changes),
            "modified": len([c for c in changes if c["type"] == "modified"]),
            "added": len([c for c in changes if c["type"] == "added"]),
            "deleted": len([c for c in changes if c["type"] == "deleted"]),
            "paragraphs_a": len(paras_a),
            "paragraphs_b": len(paras_b),
        },
        "changes": changes,
    }

    if redline_output and revisions_for_redline:
        redline_docx(path_a, revisions_for_redline, redline_output)
        result["redline_path"] = redline_output

    return result


def _format_diff(diffs) -> str:
    """Format diff operations as a readable string."""
    parts = []
    for op, text in diffs:
        if op == 0:
            parts.append(text)
        elif op == -1:
            parts.append(f"[-{text}-]")
        elif op == 1:
            parts.append(f"[+{text}+]")
    return "".join(parts)


def format_for_display(result: Dict[str, Any]) -> str:
    """Format comparison result as readable text for Sara."""
    lines = []
    s = result["summary"]
    lines.append(f"Comparison: {s['total_changes']} changes ({s['modified']} modified, {s['added']} added, {s['deleted']} deleted)")
    lines.append(f"Document A: {s['paragraphs_a']} paragraphs | Document B: {s['paragraphs_b']} paragraphs")
    lines.append("")

    for change in result["changes"]:
        ctype = change["type"].upper()
        pid = change.get("para_id", "")
        sec = change.get("section_ref", "")
        header = f"[{ctype}] {pid}"
        if sec:
            header += f" (Section {sec})"
        lines.append(header)

        if ctype == "MODIFIED":
            lines.append(f"  {change['diff']}")
        elif ctype == "DELETED":
            lines.append(f"  Removed: {change['text'][:200]}")
        elif ctype == "ADDED":
            lines.append(f"  Added: {change['text'][:200]}")
        lines.append("")

    if result.get("redline_path"):
        lines.append(f"Redlined document saved to: {result['redline_path']}")

    return "\n".join(lines)
