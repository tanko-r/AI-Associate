# Sara — AI Law Firm Associate

## What This Is

A Claude Code plugin that provides "Sara," an AI senior associate who performs real estate legal work at the quality level of a 9th-year associate at a top US law firm. Sara delivers thorough, partner-ready PSA reviews with paragraph-level disposition tables, complete transmittal packages, and RE-specific knowledge grounding — plus deal workflow support for closing checklists, title objection letters, and closing document drafting. She works collaboratively with the partner (user), asking clarifying questions and checking in at milestone gates.

## Core Value

Sara's work product must be thorough enough that a partner would approve it with light review — every clause examined, every risk flagged with specific alternative language, every deliverable complete (redline + transmittal memo + open items list).

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Plugin structure with `/sara` command entry point — existing
- ✓ Docx tooling: read, write, redline, compare, extract, analyze — existing
- ✓ MCP server + CLI fallback for docx tools — existing
- ✓ Paragraph ID system for precise revision targeting — existing
- ✓ Revision JSON format with revise/delete/insert actions — existing
- ✓ Track changes + Word comment bubbles in redlines — existing
- ✓ Subagent delegation model (researcher, drafter, reviewer, reviser) — existing
- ✓ Matter-based work product directory structure — existing
- ✓ Thorough, partner-ready contract reviews with dozens of substantive changes — v1.0
- ✓ Every-clause disposition at high aggressiveness levels (Section A/B/C output) — v1.0
- ✓ Substantive legal reasoning with market standard citations — v1.0
- ✓ Clarifying questions before complex work (smart defaults interaction model) — v1.0
- ✓ Precise subagent delegation with mandatory briefing templates and quality loop — v1.0
- ✓ Complete work product packages (redline + transmittal memo + open items list) — v1.0
- ✓ RE-specific knowledge layer with reference file loading, source markers, graceful degradation — v1.0
- ✓ Title commitment review and objection letter drafting — v1.0
- ✓ Closing checklists with deal calendars from finalized PSA — v1.0
- ✓ Closing document drafting (deeds, assignments, estoppels, holdbacks) — v1.0

### Active

<!-- Next milestone scope. -->

- [ ] Sara can draft agreements from scratch or templates (PSAs, leases, easements, LOIs, amendments)
- [ ] Sara can conduct standalone legal research (jurisdictional issues, title questions, zoning, due diligence)
- [ ] Sara can write correspondence (demand letters, response letters, comment letters to opposing counsel)
- [ ] Sara has RAG capabilities to draw from a user-provided library of source material
- [ ] RE-specific commercial lease review checklist and workflow
- [ ] Multi-document cross-analysis (PSA + loan commitment + title commitment + survey)

### Out of Scope

- Litigation support — Sara is a transactional associate (future practice area expansion)
- General practice areas beyond real estate — MVP is real estate only (eventual expansion planned)
- Client-facing communication without partner review — Sara delivers to the partner, not directly to clients
- Real-time collaboration with other AI agents — Sara works within a single Claude Code session
- Full authoring of RE checklist/clause library content — user authors the substantive content; v1.0 delivered structure and stubs

## Context

Shipped v1.0 with ~10,075 LOC across Python and Markdown. 4 phases, 9 plans, 17 requirements satisfied.

Tech stack: Claude Code plugin (skills, agents, commands, hooks), Python docx-tools (python-docx 1.2.0), MCP server.

Key components:
- `skills/sara/SKILL.md` — behavioral framework with smart defaults, 5-level aggressiveness, coverage floors, quality loop
- `agents/` — 4 subagent definitions with experienced-attorney framing, mandatory briefing templates
- `docx-tools/` — document processing pipeline (read, write, redline, compare, .ics calendar)
- `skills/sara/references/` — 7 reference files: contract-review-workflow, delegation-model, work-product-standards, deal-workflows, re-checklist-psa, clause-library, market-standards

The user is a practicing real estate attorney who evaluates work product against professional standards. Initial PSA review test (pre-v1.0) produced ~10 changes; v1.0 behavioral framework targets 40-80+ changes for a 150-paragraph PSA.

Known calibration needs: coverage floor thresholds (35+ at L4, 40+ at L5) are analytical estimates pending empirical validation against real reviews.

## Constraints

- **Platform**: Claude Code plugin system — must work within plugin architecture (skills, agents, commands, hooks)
- **Document format**: All legal work product delivered as .docx via existing docx-tools pipeline
- **LLM context**: Contract review of long documents requires careful context management — can't fit entire PSA + analysis in one pass
- **Source materials**: User will provide RE reference library; need RAG integration to make it accessible during work (v2)
- **Quality bar**: Work product judged against actual Big Law associate standards, not "good for AI"

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Start with real estate, expand later | User's domain expertise enables quality evaluation; RE is concrete enough to test against | ✓ Good — focused scope enabled shipping v1.0 in 5 days |
| Collaborative interaction model | Sara asks questions before complex work, doesn't just execute blindly | ✓ Good — COLB-01/02 shipped, smart defaults avoids over-questioning |
| Both reference materials + LLM knowledge | Checklists/clause libraries for structure, LLM for reasoning and drafting | ✓ Good — source markers distinguish grounded vs LLM-sourced assessments |
| RAG for user-provided source library | Large reference library can't fit in context; needs retrieval system | — Pending (v2) |
| Existing docx tooling is adequate | Problem is Sara's brain (prompting/architecture), not her hands (tools) | ✓ Good — only added table/list rendering and .ics writer |
| Anti-context-poisoning: experienced-attorney framing | "Subagent attorneys" not "junior associates" — quality expectation through competence | ✓ Good — consistent across all 4 agent prompts |
| Quality loop: substantive feedback, max 2 rounds | Always provide refinement feedback, not artificial rejection | ✓ Good — 6 named checks prevent checkbox reviewing |
| Reference files are stubs with [TODO] placeholders | User populates firm content; Sara degrades gracefully to LLM knowledge | ✓ Good — stub files usable immediately, improve as user adds content |
| Source markers (dagger) distinguish checklist vs LLM assessments | Partner sees which items are grounded in firm data vs general knowledge | ✓ Good — transparent provenance |
| Closing documents drafted from scratch, no templates | LLM legal knowledge with mandatory partner verification flags | ⚠️ Revisit — may need templates for jurisdiction-specific forms |
| Three-bucket title exception categorization | Review items need partner decision before inclusion in letter | ✓ Good — prevents premature objections |
| Deal context persists in SARA.md | Avoids re-extracting terms from source documents | ✓ Good — enables multi-workflow deals |
| Coverage floors: 35+ at L4, 40+ at L5 for 150-para PSA | Analytical estimates for minimum thoroughness | ⚠️ Revisit — needs empirical calibration |
| Canonical path references use ${CLAUDE_PLUGIN_ROOT} | Consistent path convention across all reference files | ✓ Good — eliminated stale path confusion |

---
*Last updated: 2026-02-19 after v1.0 milestone*
