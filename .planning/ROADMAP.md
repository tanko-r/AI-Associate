# Roadmap: Sara — AI Law Firm Associate

## Overview

Sara already exists as a functioning plugin with docx tooling and subagents. The problem is quality — a PSA review produced ~19 substantive changes on a 170-paragraph document when a competent senior associate would produce 40-80+. This roadmap attacks the quality gap directly: first by rebuilding Sara's behavioral foundation (how she reviews, delegates, and enforces completeness), then by building the RE-specific knowledge layer that tells her what to look for and what good looks like, and finally by expanding to additional deal workflows once the core review quality is validated.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Behavioral Foundation** - Rewrite Sara's orchestration logic, delegation model, and subagent prompts to produce partner-ready PSA reviews with complete transmittal packages (completed 2026-02-18)
- [x] **Phase 2: Knowledge Layer** - Build RE-specific stub files (checklist, clause library, market standards) with correct structure and placeholders that Sara loads during framework building and the user fills in over time (completed 2026-02-19)
- [x] **Phase 3: Deal Workflows** - Add closing checklist generation, title objection letter drafting, and closing document drafting (deeds, assignments, estoppels, holdbacks) as validated Sara capabilities (completed 2026-02-18)
- [ ] **Phase 4: Integration Fixes & Cleanup** - Close 3 integration gaps (INT-01, INT-02, INT-03) and 3 tech debt items identified by milestone audit (gap closure)

## Phase Details

### Phase 1: Behavioral Foundation
**Goal**: Sara reliably produces thorough, partner-ready PSA reviews — every paragraph examined, complete transmittal packages delivered, junior work quality-gated before final output
**Depends on**: Nothing (first phase)
**Requirements**: REVQ-01, REVQ-02, REVQ-03, REVQ-04, REVQ-05, REVQ-06, DLGT-01, DLGT-02, DLGT-03, DLGT-04, COLB-01, COLB-02
**Success Criteria** (what must be TRUE):
  1. On a Level 4-5 PSA review, Sara produces a paragraph-level disposition table covering every paragraph (Accept/Revise/Delete/Insert/Comment) before beginning redline drafting
  2. Sara's final redline deliverable includes a transmittal memo and open items list — never a naked redline
  3. Every subagent delegation Sara issues contains: representation, aggressiveness level, target risk list, paragraph IDs, defined terms, and explicit output format
  4. Sara asks clarifying questions about representation, deal context, and aggressiveness level before starting any contract review
  5. Sara sends junior work back with specific written feedback at least once before accepting it for the final deliverable
**Plans:** 3/3 plans complete

Plans:
- [x] 01-01-PLAN.md — Rewrite Sara SKILL.md: smart-defaults interaction model, aggressiveness-level definitions with coverage floors, milestone check-ins, quality gate checklist, quality loop spec, prompt-log format, transmittal package enforcement. Update contract-review-workflow.md with Step 5.5 and new transmittal format. Update commands/sara.md. (Wave 1)
- [x] 01-02-PLAN.md — Upgrade document-reviewer agent: anti-context-poisoning framing, Section A disposition table with 6 mandatory columns, Section B thematic risk map with compound risk analysis, conforming changes identification, mandatory market citations. (Wave 2, depends on 01-01)
- [x] 01-03-PLAN.md — Upgrade contract-reviser, document-drafter, legal-researcher agents and reference files: anti-context-poisoning framing, mandatory delegation briefing template, quality loop protocol, delegation logging format, market rationale requirements, transmittal memo format, .msg delivery standard. (Wave 3, depends on 01-01 + 01-02)

### Phase 2: Knowledge Layer
**Goal**: Sara has RE-specific stub files she loads during Step 3 (framework building) — a PSA review checklist with correct section structure and per-category risk placeholders, and clause library and market standards stubs the user can populate with model language over time; Sara uses whatever content is present, even if stubs are only partially filled
**Depends on**: Phase 1
**Requirements**: KNOW-01, KNOW-02
**Success Criteria** (what must be TRUE):
  1. During PSA review Step 3, Sara loads a RE-specific checklist stub that has the correct section structure (DD period, title cure, deposit mechanics, representations, indemnification, default remedies, closing conditions, AS-IS provisions) with per-category target risk lists and clearly marked placeholders for user content
  2. Sara loads clause library and market-standards stubs that have correct section headers and placeholder structure — files are usable as-is and improve as the user adds content, without requiring full authoring before Sara can function
  3. The stub files ship as templates: structure, section headers, example placeholders, and instructions for how the user populates them — no substantive legal content authored by this project
**Plans:** 2/2 plans complete

Plans:
- [x] 02-01-PLAN.md — Create re-checklist-psa.md stub: 24-category PSA review checklist with comprehensive sub-items sourced from 3 sample documents, Key Risks tables with buyer/seller columns, [Common]/[Specialized] tags, [TODO] placeholders, cross-references to market-standards.md (Wave 1)
- [x] 02-02-PLAN.md — Create clause-library.md and market-standards.md stubs with matching 24-category structure; wire Sara to load all 3 files during Step 3 with selective loading, coverage reporting, † LLM-source markers, and missing provisions report (Wave 1)

### Phase 3: Deal Workflows
**Goal**: Sara can handle the full closing phase of a deal — generating a closing checklist and deal calendar from a finalized PSA, drafting title objection letters from a title commitment, and drafting standard closing documents (deeds, assignments, estoppels, escrow holdback agreements, and other closing deliverables a senior RE associate would prepare)
**Depends on**: Phase 2
**Requirements**: DEAL-01, DEAL-02, DEAL-03
**Success Criteria** (what must be TRUE):
  1. Given a finalized PSA, Sara produces a closing checklist organized by responsible party (buyer/seller/escrow/lender) with deal-specific deadlines populated from the contract
  2. Given a title commitment, Sara produces a title objection letter that identifies Schedule B-II exceptions requiring curative action, specifies the cure required for each, and sets a reasonable objection deadline
  3. Given a finalized PSA and deal context, Sara drafts standard closing documents — including at minimum a deed, assignment and assumption agreement, and estoppel certificate — populated with deal-specific terms extracted from the PSA
  4. Sara's closing document drafts include a cover note identifying which provisions require partner review, deal-specific insertions that need verification, and any provisions she could not populate from available documents
**Plans:** 3/3 plans complete

Plans:
- [x] 03-01-PLAN.md — Enhance write_docx with table and list rendering, create calendar_writer.py for .ics generation, create deal-workflows.md with Workflow 1 (closing checklist), add SARA.md persistence to SKILL.md, update work-product-standards.md with checklist and calendar standards (Wave 1)
- [x] 03-02-PLAN.md — Define Workflow 2 (title objection letter + title summary memo) in deal-workflows.md with three-bucket exception categorization (Accept/Object/Review), add title letter and memo standards to work-product-standards.md (Wave 2, depends on 03-01)
- [x] 03-03-PLAN.md — Define Workflow 3 (closing document drafting) in deal-workflows.md for deeds, assignments, estoppels, and holdbacks; update document-drafter.md and delegation-model.md with closing document patterns; add closing document standards to work-product-standards.md (Wave 2, depends on 03-01)

### Phase 4: Integration Fixes & Cleanup
**Goal**: Close all integration gaps and actionable tech debt items identified by the v1.0 milestone audit — fix delegation template wiring, stale path references, and documentation drift
**Depends on**: Phase 3
**Requirements**: DLGT-01, KNOW-01, KNOW-02, REVQ-05, DEAL-03 (integration fixes for already-satisfied requirements)
**Gap Closure**: Closes INT-01, INT-02, INT-03 from v1.0 audit + 3 tech debt items
**Success Criteria** (what must be TRUE):
  1. Document-Reviewer and Contract-Reviser briefing templates in delegation-model.md include a "Reference File Coverage" field
  2. work-product-standards.md references the canonical `skills/sara/references/contract-review-workflow.md` path, not the stale root-level copy
  3. deal-workflows.md Workflow 3 explicitly cross-references the Closing Document Briefing Template in delegation-model.md
  4. Stale root-level `references/` directory is deleted
  5. gen_calendar.py docstring references the correct filename
  6. README.md uses the correct skill name `sara`
**Plans:** 1 plan

Plans:
- [ ] 04-01-PLAN.md — Fix all 3 integration gaps (INT-01, INT-02, INT-03) and 3 tech debt items in a single plan (Wave 1)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Behavioral Foundation | 3/3 | Complete | 2026-02-18 |
| 2. Knowledge Layer | 2/2 | Complete | 2026-02-19 |
| 3. Deal Workflows | 3/3 | Complete | 2026-02-18 |
| 4. Integration Fixes & Cleanup | 0/1 | Not started | - |
