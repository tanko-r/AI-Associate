---
phase: 01-formatting-preserving-redline-pipeline
plan: 01
subsystem: docx-processing
tags: [ooxml, redline, formatting, deepcopy, lxml, tracked-changes]

# Dependency graph
requires: []
provides:
  - CharFormatInfo dataclass for per-character formatting metadata
  - _build_char_format_map() for mapping paragraph text positions to source run rPr elements
  - _split_segment_by_runs() for splitting diff segments at original run boundaries
  - _make_run_from_rpr() for creating w:r elements with full XML formatting fidelity
affects: [01-02, 01-03, 01-04]

# Tech tracking
tech-stack:
  added: []
  patterns: [deepcopy-rPr-preservation, per-character-format-mapping]

key-files:
  created: []
  modified:
    - docx-tools/core/redliner.py

key-decisions:
  - "Used dataclass for CharFormatInfo (lightweight, typed, readable)"
  - "Shared deepcopy per run (not per character) with caller-must-deepcopy-before-modify contract"
  - "Kept _make_run() intact -- removal deferred to Plan B when callers are migrated"

patterns-established:
  - "rPr preservation: always deepcopy source <w:rPr> XML, never reconstruct from properties"
  - "char-map contract: callers must deepcopy rpr_element before modifying (shared within a run)"

requirements-completed: []

# Metrics
duration: 3min
completed: 2026-02-27
---

# Phase 1 Plan A: Character-to-Run Mapping Infrastructure Summary

**Per-character format mapping and XML-fidelity run construction helpers for formatting-preserving redlines**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-28T03:57:11Z
- **Completed:** 2026-02-28T04:00:08Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Built CharFormatInfo dataclass and _build_char_format_map() that maps each character in a paragraph's concatenated text to its source run's deepcopy'd rPr element
- Added _split_segment_by_runs() that splits diff segments at original run boundaries for per-run formatting output
- Added _make_run_from_rpr() that creates w:r elements using full XML rPr deepcopy instead of a 5-property dict
- All 8 existing redliner tests continue to pass

## Task Commits

Each task was committed atomically:

1. **Task A1: Add _build_char_format_map helper** - `a945818` (feat)
2. **Task A2: Add _split_segment_by_runs and _make_run_from_rpr helpers** - `550aad2` (feat)

## Files Created/Modified
- `docx-tools/core/redliner.py` - Added CharFormatInfo dataclass, _build_char_format_map(), _split_segment_by_runs(), and _make_run_from_rpr() helper functions

## Decisions Made
- Used dataclass for CharFormatInfo over NamedTuple -- provides mutability option and cleaner field defaults
- Shared deepcopy per run rather than per character for efficiency, with caller-must-deepcopy contract documented
- Kept existing _make_run() function intact per plan -- removal happens in Plan B when _apply_track_changes is migrated

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All three new helper functions are available and tested via smoke tests
- Plan B (01-02) can now integrate these helpers into _apply_track_changes to replace the 5-property dict approach
- Existing _make_run() preserved for backward compatibility until Plan B migrates callers

## Self-Check: PASSED

All files exist, all commits verified.

---
*Phase: 01-formatting-preserving-redline-pipeline*
*Completed: 2026-02-27*
