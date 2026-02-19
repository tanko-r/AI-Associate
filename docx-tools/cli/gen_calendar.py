"""
CLI wrapper for calendar_writer -- generate .ics deal calendar files.

Usage:
    python docx-tools/cli/calendar.py --events '<json>' --output calendar.ics
    python docx-tools/cli/calendar.py --events events.json --output calendar.ics

Events JSON format:
    [{"date": "2026-04-15", "summary": "DD Expiry", "description": "Section 4.1"}]
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.calendar_writer import generate_ics


def main():
    parser = argparse.ArgumentParser(description="Generate .ics deal calendar files")
    parser.add_argument(
        "--events",
        required=True,
        help="JSON string or path to JSON file containing events",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the .ics file",
    )
    parser.add_argument(
        "--name",
        default="Deal Calendar",
        help="Calendar display name (default: Deal Calendar)",
    )
    args = parser.parse_args()

    # Parse events -- try as file path first, then as JSON string
    events_path = Path(args.events)
    if events_path.exists():
        with open(events_path) as f:
            events = json.load(f)
    else:
        try:
            events = json.loads(args.events)
        except json.JSONDecodeError as e:
            print(f"Error parsing events JSON: {e}", file=sys.stderr)
            sys.exit(1)

    output = generate_ics(events, args.output, calendar_name=args.name)
    print(f"Calendar written to: {output}")


if __name__ == "__main__":
    main()
