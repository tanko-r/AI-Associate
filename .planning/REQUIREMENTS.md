# Requirements: Sara — AI Law Firm Associate

**Defined:** 2026-02-18
**Core Value:** Sara's work product must be thorough enough that a partner would approve it with light review — every clause examined, every risk flagged with specific alternative language, every deliverable complete.

## v1 Requirements

Requirements for initial release. MVP scope: PSA review and deal-related workflows (title objections, closing checklists). Sara uses an iterative review loop with juniors — sending work back until it meets her exacting standards.

### Contract Review Quality

- [ ] **REVQ-01**: Sara examines every paragraph and assigns a disposition (Accept/Revise/Delete/Insert/Comment) at aggressiveness Level 4-5
- [ ] **REVQ-02**: Sara builds practice-area-specific analysis framework (target concept list + target risk list) before starting clause-by-clause review
- [ ] **REVQ-03**: Sara drafts full replacement paragraph language with specific legal rationale for each revision
- [ ] **REVQ-04**: Sara verifies cross-references and conforming changes before compiling final revision set
- [ ] **REVQ-05**: Sara delivers complete transmittal package (redline + transmittal memo + open items list) for every contract review
- [ ] **REVQ-06**: Sara includes market standard citations in every substantive markup

### Subagent Delegation & Quality Loop

- [ ] **DLGT-01**: Every subagent delegation includes representation, aggressiveness, target risk list, paragraph IDs, defined terms, and explicit output format
- [ ] **DLGT-02**: Sara iteratively reviews junior work product and sends it back with specific feedback until it meets her standards (ralph loop pattern)
- [ ] **DLGT-03**: Sara's review of junior work is exacting — she checks legal reasoning, drafting precision, cross-reference accuracy, and market standard compliance before accepting
- [ ] **DLGT-04**: Sara logs every delegation and review cycle in prompt-log.md

### RE Knowledge Layer

- [ ] **KNOW-01**: RE-specific PSA review checklist that Sara loads during framework building (Step 3) — covers DD period, title cure, deposit mechanics, representations, indemnification, default remedies, closing conditions, AS-IS provisions
- [ ] **KNOW-02**: Clause library with model language for critical RE deal provision types (indemnification caps, rep qualifiers, DD termination rights, deposit hard-going triggers, estoppel requirements, assignment restrictions)

### Deal Workflows

- [ ] **DEAL-01**: Sara can generate a closing checklist and deal calendar from a finalized PSA
- [ ] **DEAL-02**: Sara can draft title objection letters based on title commitment review

### Collaborative Interaction

- [ ] **COLB-01**: Sara asks clarifying questions before starting complex work (representation, deal context, aggressiveness level, client priorities)
- [ ] **COLB-02**: Sara proposes her approach and checks in with the partner before finalizing major work product

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

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REVQ-01 | — | Pending |
| REVQ-02 | — | Pending |
| REVQ-03 | — | Pending |
| REVQ-04 | — | Pending |
| REVQ-05 | — | Pending |
| REVQ-06 | — | Pending |
| DLGT-01 | — | Pending |
| DLGT-02 | — | Pending |
| DLGT-03 | — | Pending |
| DLGT-04 | — | Pending |
| KNOW-01 | — | Pending |
| KNOW-02 | — | Pending |
| DEAL-01 | — | Pending |
| DEAL-02 | — | Pending |
| COLB-01 | — | Pending |
| COLB-02 | — | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 0
- Unmapped: 16

---
*Requirements defined: 2026-02-18*
*Last updated: 2026-02-18 after initial definition*
