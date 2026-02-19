"""
Generate .ics calendar files for deal milestones.

Produces RFC 5545 compliant VCALENDAR files with multi-VEVENT entries
for all-day events. No external dependencies -- uses stdlib only.
"""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


def generate_ics(
    events: List[Dict[str, str]],
    output_path: str,
    calendar_name: str = "Deal Calendar",
) -> str:
    """
    Generate an .ics file with multiple VEVENT entries.

    Args:
        events: List of dicts with keys: date (YYYY-MM-DD), summary,
                description (optional).
        output_path: Path for the output .ics file.
        calendar_name: Display name for the calendar.

    Returns:
        The output file path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sara AI Associate//Deal Calendar//EN",
        f"X-WR-CALNAME:{_ics_escape(calendar_name)}",
    ]

    for event in events:
        dt = event["date"].replace("-", "")
        dt_end = _next_day(event["date"]).replace("-", "")
        uid = f"sara-{uuid.uuid4().hex[:12]}@ai-associate"

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt}",
            f"DTEND;VALUE=DATE:{dt_end}",
            f"SUMMARY:{_ics_escape(event['summary'])}",
            f"DESCRIPTION:{_ics_escape(event.get('description', ''))}",
            f"UID:{uid}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    # RFC 5545 requires CRLF line endings
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")

    return str(output_path)


def _ics_escape(text: str) -> str:
    """Escape special characters per RFC 5545."""
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def _next_day(date_str: str) -> str:
    """Return the next day as YYYY-MM-DD for all-day event DTEND."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return (dt + timedelta(days=1)).strftime("%Y-%m-%d")
