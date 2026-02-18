# Roadmap: Sara — AI Law Firm Associate

## Overview

Sara already exists as a functioning plugin with docx tooling and subagents. The problem is quality — a PSA review produced ~19 substantive changes on a 170-paragraph document when a competent senior associate would produce 40-80+. This roadmap attacks the quality gap directly: first by rebuilding Sara's behavioral foundation (how she reviews, delegates, and enforces completeness), then by building the RE-specific knowledge layer that tells her what to look for and what good looks like, and finally by expanding to additional deal workflows once the core review quality is validated.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Behavioral Foundation** - Rewrite Sara's orchestration logic, delegation model, and subagent prompts to produce partner-ready PSA reviews with complete transmittal packages
- [ ] **Phase 2: Knowledge Layer** - Build RE-specific stub files (checklist, clause library, market standards) with correct structure and placeholders that Sara loads during framework building and the user fills in over time
- [ ] **Phase 3: Deal Workflows** - Add closing checklist generation, title objection letter drafting, and closing document drafting (deeds, assignments, estoppels, holdbacks) as validated Sara capabilities

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
**Plans**: TBD

Plans:
- [ ] 01-01: Rewrite Sara SKILL.md — aggressiveness-level scope requirements, coverage floor, quality gate definitions, collaborative interaction model
- [ ] 01-02: Upgrade document-reviewer agent — disposition table format, minimum entry counts, paragraph ID requirements, cross-reference conforming changes section
- [ ] 01-03: Upgrade contract-reviser and document-drafter agents — delegation briefing template, defined-terms injection, deal-specific language requirements, delegation logging

### Phase 2: Knowledge Layer
**Goal**: Sara has RE-specific stub files she loads during Step 3 (framework building) — a PSA review checklist with correct section structure and per-category risk placeholders, and clause library and market standards stubs the user can populate with model language over time; Sara uses whatever content is present, even if stubs are only partially filled
**Depends on**: Phase 1
**Requirements**: KNOW-01, KNOW-02
**Success Criteria** (what must be TRUE):
  1. During PSA review Step 3, Sara loads a RE-specific checklist stub that has the correct section structure (DD period, title cure, deposit mechanics, representations, indemnification, default remedies, closing conditions, AS-IS provisions) with per-category target risk lists and clearly marked placeholders for user content
  2. Sara loads clause library and market-standards stubs that have correct section headers and placeholder structure — files are usable as-is and improve as the user adds content, without requiring full authoring before Sara can function
  3. The stub files ship as templates: structure, section headers, example placeholders, and instructions for how the user populates them — no substantive legal content authored by this project
**Plans**: TBD

Plans:
- [ ] 02-01: Create re-checklist-psa.md stub — correct section structure for all PSA provision categories, per-category target risk list skeletons, placeholder content with instructions for user to complete
- [ ] 02-02: Create clause-library.md and market-standards.md stubs — correct section headers, placeholder structure for model language entries, instructions for user population; wire Sara to load all three files during Step 3

### Phase 3: Deal Workflows
**Goal**: Sara can handle the full closing phase of a deal — generating a closing checklist and deal calendar from a finalized PSA, drafting title objection letters from a title commitment, and drafting standard closing documents (deeds, assignments, estoppels, escrow holdback agreements, and other closing deliverables a senior RE associate would prepare)
**Depends on**: Phase 2
**Requirements**: DEAL-01, DEAL-02, DEAL-03
**Success Criteria** (what must be TRUE):
  1. Given a finalized PSA, Sara produces a closing checklist organized by responsible party (buyer/seller/escrow/lender) with deal-specific deadlines populated from the contract
  2. Given a title commitment, Sara produces a title objection letter that identifies Schedule B-II exceptions requiring curative action, specifies the cure required for each, and sets a reasonable objection deadline
  3. Given a finalized PSA and deal context, Sara drafts standard closing documents — including at minimum a deed, assignment and assumption agreement, and estoppel certificate — populated with deal-specific terms extracted from the PSA
  4. Sara's closing document drafts include a cover note identifying which provisions require partner review, deal-specific insertions that need verification, and any provisions she could not populate from available documents
**Plans**: TBD

Plans:
- [ ] 03-01: Build closing checklist workflow — PSA-to-checklist extraction, deal calendar generation, responsible-party organization
- [ ] 03-02: Build title objection letter workflow — title commitment review, Schedule B-II exception analysis, objection letter drafting
- [ ] 03-03: Build closing document drafting workflow — deed, assignment and assumption, estoppel certificate, and escrow holdback agreement templates; Sara extracts deal terms from PSA and populates drafts with cover note flagging items for partner review

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Behavioral Foundation | 0/3 | Not started | - |
| 2. Knowledge Layer | 0/2 | Not started | - |
| 3. Deal Workflows | 0/3 | Not started | - |
