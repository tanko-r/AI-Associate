---
phase: 01-formatting-preserving-redline-pipeline
plan: 02
subsystem: docx-processing
tags: [python-docx, track-changes, oxml, diff-match-patch, formatting-preservation]

# Dependency graph
requires:
  - phase: 01-formatting-preserving-redline-pipeline
    provides: CharFormatInfo, _build_char_format_map, _split_segment_by_runs, _make_run_from_rpr
provides:
  - Per-run formatting-preserving _apply_track_changes() using char map infrastructure
  - Removed legacy _make_run() function (5-property dict approach)
affects: [01-formatting-preserving-redline-pipeline]

# Tech tracking
tech-stack:
  added: []
  patterns: [char-map-driven-diff-rebuild, orig-pos-cursor-tracking]

key-files:
  created: []
  modified: [docx-tools/core/redliner.py]

key-decisions:
  - "Insertions inherit rPr from preceding character (or first char if at position 0)"
  - "Deletion w:id uses hash of sub_text+orig_pos for uniqueness across split segments"

patterns-established:
  - "orig_pos cursor pattern: equal and delete advance, insert does not"
  - "char_map must be built before any paragraph mutations"

requirements-completed: []

# Metrics
duration: 2min
completed: 2026-02-28
---

# Plan 01-02: Refactor _apply_track_changes() Summary

**Per-run formatting preservation in track changes via char-map-driven diff rebuild, replacing 5-property dict with full XML rPr fidelity**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-28T04:04:06Z
- **Completed:** 2026-02-28T04:06:11Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Rewrote _apply_track_changes() internals to use _build_char_format_map() for per-character formatting capture
- Equal and deletion segments split at run boundaries so each sub-segment preserves its original w:rPr
- Insertions inherit formatting from the character immediately preceding the insertion point
- Removed legacy _make_run() function (32 lines) that only captured 5 formatting properties

## Task Commits

Each task was committed atomically:

1. **Task B1: Rewrite _apply_track_changes() internals** - `f8087d6` (feat)
2. **Task B2: Remove old _make_run() and clean up imports** - `077f162` (refactor)

## Files Created/Modified
- `docx-tools/core/redliner.py` - Refactored _apply_track_changes() to use char map; removed _make_run()

## Decisions Made
- Insertions inherit rPr from the character immediately preceding the insertion point (orig_pos - 1), or from the first character if inserting at position 0. This matches Word's native behavior where typed text inherits formatting from the cursor position.
- Deletion w:id hashes include sub_text + orig_pos to produce unique IDs when a deletion is split across multiple run boundaries.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- _apply_track_changes() now preserves per-run formatting through the diff rebuild cycle
- Ready for Plan 03 (integration tests with multi-format paragraphs) and Plan 04 (end-to-end testing)
- All 8 existing tests continue to pass

## Self-Check: PASSED

- FOUND: docx-tools/core/redliner.py
- FOUND: f8087d6 (Task B1 commit)
- FOUND: 077f162 (Task B2 commit)
- FOUND: 01-02-SUMMARY.md

---
*Phase: 01-formatting-preserving-redline-pipeline*
*Completed: 2026-02-28*
