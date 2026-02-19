---
phase: 02-knowledge-layer
plan: 02
subsystem: knowledge
tags: [clause-library, market-standards, workflow-integration, reference-files]

requires:
  - phase: 01-behavioral-foundation
    provides: Sara's SKILL.md, contract-review-workflow.md, document-reviewer.md, document-drafter.md
provides:
  - Clause library stub with 24-category structure and model language placeholders
  - Market standards stub with 24-category structure and market data placeholders
  - Step 3-pre reference file loading in contract-review-workflow.md
  - LLM fallback with source markers and missing provisions report in SKILL.md
  - Source marker convention in document-reviewer.md and document-drafter.md
affects: [contract-review-workflow, document-reviewer, document-drafter, sara-skill]

tech-stack:
  added: []
  patterns: [reference-file-loading, selective-category-loading, coverage-reporting, source-marker-convention, graceful-degradation]

key-files:
  created:
    - skills/sara/references/clause-library.md
    - skills/sara/references/market-standards.md
  modified:
    - skills/sara/SKILL.md
    - skills/sara/references/contract-review-workflow.md
    - agents/document-reviewer.md
    - agents/document-drafter.md

key-decisions:
  - "Source marker uses dagger symbol for LLM-sourced items in disposition table and transmittal memo"
  - "Reference file loading is best-effort -- never blocks a review; graceful degradation to LLM knowledge"
  - "Missing provisions report distinguishes Common (always reported) vs Specialized (context-dependent)"
  - "Coverage report, LLM fallback, and source markers are MVP features tracked for removal once files are populated"
  - "Selective loading: read category index first, then only relevant categories -- prevents context window bloat"

patterns-established:
  - "Step 3-pre reference file loading pattern for practice-area-specific files"
  - "Source marker convention for distinguishing reference-backed vs LLM-backed assessments"
  - "Coverage report [MVP] pattern for tracking reference file population progress"

requirements-completed: [KNOW-02]

duration: 10 min
completed: 2026-02-19
---

# Phase 2 Plan 02: Clause Library + Market Standards + Wiring Summary

**Two reference file stubs (clause-library.md, market-standards.md) with matching 24-category structure, plus workflow integration wiring Step 3-pre loading, source markers, coverage reporting, and missing provisions reporting across 4 existing files**

## Performance

- **Duration:** 10 min
- **Started:** 2026-02-19T02:33:52Z
- **Completed:** 2026-02-19T02:44:05Z
- **Tasks:** 2
- **Files modified:** 6 (2 created, 4 modified)

## Accomplishments
- Created clause-library.md (320 lines, 24 categories, 59 [TODO] placeholders for model language with entry format template)
- Created market-standards.md (289 lines, 24 categories, 51 [TODO] placeholders for market data with population instructions)
- Added Step 3-pre to contract-review-workflow.md for reference file loading with selective loading and coverage reporting
- Added Reference Files [MVP] section to SKILL.md with LLM fallback, source marker, missing provisions report, and graceful degradation
- Added source marker convention to document-reviewer.md (Section A Market Assessment field)
- Added source marker convention to document-drafter.md (transmittal Key Changes and Open Items)

## Task Commits

1. **Task 1: Create stub files** - `a010e6c` (feat)
2. **Task 2: Wire reference files into workflow** - `0bbb7d6` (feat)

**Plan metadata:** (included in wave-level commit)

## Files Created/Modified
- `skills/sara/references/clause-library.md` - 320-line clause library stub with 24 categories and model language placeholders
- `skills/sara/references/market-standards.md` - 289-line market standards stub with 24 categories and market data placeholders
- `skills/sara/SKILL.md` - Added Reference Files [MVP] section (LLM fallback, source markers, missing provisions report, graceful degradation)
- `skills/sara/references/contract-review-workflow.md` - Added Step 3-pre (reference file loading), updated Step 3c (checklist merge), updated Step 3d (coverage report)
- `agents/document-reviewer.md` - Added source marker convention in Market Assessment field
- `agents/document-drafter.md` - Added source marker convention in transmittal memo

## Decisions Made
- Category numbers and names are identical across all 3 reference files (checklist, clause library, market standards)
- Sub-section headings in clause-library.md and market-standards.md correspond to checklist review points and See: cross-references
- Clause library includes entry format template with Source, When to use, Language, and Notes fields
- Market standards notes GitHub issue #1 for format refinement

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 3 reference files created and wired into Sara's Step 3 workflow
- Sara will now load reference files during PSA review, report coverage, mark LLM-sourced items with source markers, and generate missing provisions reports
- Phase 2 complete -- ready for verification

---
*Phase: 02-knowledge-layer*
*Completed: 2026-02-19*
