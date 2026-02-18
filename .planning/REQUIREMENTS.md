# Requirements: Sara — AI Law Firm Associate

**Defined:** 2026-02-18
**Core Value:** Sara's work product must be thorough enough that a partner would approve it with light review — every clause examined, every risk flagged with specific alternative language, every deliverable complete.

## v1 Requirements

Requirements for initial release. MVP scope: PSA review and deal-related workflows (title objections, closing checklists, closing documents). Sara uses an iterative review loop with juniors — sending work back until it meets her exacting standards.

### Contract Review Quality

- [x] **REVQ-01**: Sara examines every paragraph and assigns a disposition (Accept/Revise/Delete/Insert/Comment) at aggressiveness Level 4-5
- [x] **REVQ-02**: Sara builds practice-area-specific analysis framework (target concept list + target risk list) before starting clause-by-clause review
- [x] **REVQ-03**: Sara drafts full replacement paragraph language with specific legal rationale for each revision
- [x] **REVQ-04**: Sara verifies cross-references and conforming changes before compiling final revision set
- [x] **REVQ-05**: Sara delivers complete transmittal package (redline + transmittal memo + open items list) for every contract review
- [x] **REVQ-06**: Sara includes market standard citations in every substantive markup

### Subagent Delegation & Quality Loop

- [x] **DLGT-01**: Every subagent delegation includes representation, aggressiveness, target risk list, paragraph IDs, defined terms, and explicit output format
- [x] **DLGT-02**: Sara iteratively reviews junior work product and sends it back with specific feedback until it meets her standards (ralph loop pattern)
- [x] **DLGT-03**: Sara's review of junior work is exacting — she checks legal reasoning, drafting precision, cross-reference accuracy, and market standard compliance before accepting
- [x] **DLGT-04**: Sara logs every delegation and review cycle in prompt-log.md

### RE Knowledge Layer

- [ ] **KNOW-01**: RE-specific PSA review checklist stub that Sara loads during framework building (Step 3) — structured skeleton with correct sections, per-category target risk lists, and placeholders for the user to fill in; covers DD period, title cure, deposit mechanics, representations, indemnification, default remedies, closing conditions, AS-IS provisions
- [ ] **KNOW-02**: Clause library stub and market-standards stub with correct structure, section headers, and placeholders for model language — files ship as templates the user completes, not fully authored reference material

### Deal Workflows

- [ ] **DEAL-01**: Sara can generate a closing checklist and deal calendar from a finalized PSA
- [ ] **DEAL-02**: Sara can draft title objection letters based on title commitment review
- [ ] **DEAL-03**: Sara can draft standard closing and deal documents from a finalized PSA — including deeds, assignments, estoppels, escrow holdback agreements, and other closing deliverables a senior RE associate would prepare

### Collaborative Interaction

- [x] **COLB-01**: Sara asks clarifying questions before starting complex work (representation, deal context, aggressiveness level, client priorities)
- [x] **COLB-02**: Sara proposes her approach and checks in with the partner before finalizing major work product

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Additional Practice Areas

- **PRAC-01**: RE-specific commercial lease review checklist and workflow
- **PRAC-02**: Market standards reference file for common RE provisions across deal types
- **PRAC-03**: Correspondence drafting workflow (demand letters, response letters, client memos)
- **PRAC-04**: Counterparty argument anticipation per markup
- **PRAC-05**: Skill routing — Sara selects appropriate practice-area skill based on assignment

### Infrastructure

- **INFR-01**: RAG from user-provided reference library (ChromaDB + embeddings + hybrid retrieval)
- **INFR-02**: Parallel subagent orchestration for concurrent research + review
- **INFR-03**: Multi-document cross-analysis (PSA + loan commitment + title commitment + survey)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Litigation support | Sara is transactional; different expertise and workflows required |
| Auto-sending correspondence | Professional responsibility requires partner review before sending |
| Client-facing output without partner review | Sara delivers to the partner, not directly to clients |
| Generic legal AI responses outside RE | Quality comes from depth; MVP is RE deals only |
| Lease review workflow | Deferred to v2; PSA and deal workflows are the validation target |
| Real-time multi-party collaboration | Claude Code is single-session; share work product as files |
| Full authoring of RE checklist/clause library content | User authors the substantive content; Phase 2 delivers the structure and stubs |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REVQ-01 | Phase 1 | Complete |
| REVQ-02 | Phase 1 | Complete |
| REVQ-03 | Phase 1 | Complete |
| REVQ-04 | Phase 1 | Complete |
| REVQ-05 | Phase 1 | Complete |
| REVQ-06 | Phase 1 | Complete |
| DLGT-01 | Phase 1 | Complete |
| DLGT-02 | Phase 1 | Complete |
| DLGT-03 | Phase 1 | Complete |
| DLGT-04 | Phase 1 | Complete |
| KNOW-01 | Phase 2 | Pending |
| KNOW-02 | Phase 2 | Pending |
| DEAL-01 | Phase 3 | Pending |
| DEAL-02 | Phase 3 | Pending |
| DEAL-03 | Phase 3 | Pending |
| COLB-01 | Phase 1 | Complete |
| COLB-02 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-02-18*
*Last updated: 2026-02-18 — KNOW-01/KNOW-02 updated to stub approach; DEAL-03 added for closing document drafting*
