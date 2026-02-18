# Sara — AI Law Firm Associate

## What This Is

A Claude Code plugin that provides "Sara," an AI senior associate who performs real estate legal work at the quality level of a 9th-year associate at a top US law firm. Sara reviews contracts, drafts agreements, conducts legal research, prepares memos, and handles correspondence — collaboratively with the partner (user), asking questions when needed and delivering complete, partner-ready work product.

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

### Active

<!-- Current scope. Building toward these. -->

- [ ] Sara produces thorough, partner-ready contract reviews (dozens of changes, not 10)
- [ ] Sara examines every clause and assigns a disposition at high aggressiveness levels
- [ ] Sara's legal reasoning is substantive — cites market standards, anticipates counterparty arguments
- [ ] Sara asks clarifying questions before diving into complex work (representation, deal context, priorities)
- [ ] Sara instructs subagents with precision — specific paragraphs, exact proposed language, clear acceptance criteria
- [ ] Sara delivers complete work product packages (redline + transmittal memo + open items list)
- [ ] Sara can draft agreements from scratch or templates (PSAs, leases, easements, LOIs, amendments)
- [ ] Sara can conduct legal research (jurisdictional issues, title questions, zoning, due diligence)
- [ ] Sara can prepare analytical memos (issue-spotting, risk assessments, deal summaries, closing checklists)
- [ ] Sara can write correspondence (demand letters, transmittal memos, comment letters to opposing counsel)
- [ ] Sara can review title commitments and underlying title documents
- [ ] Sara has RAG capabilities to draw from a user-provided library of source material
- [ ] Sara's knowledge combines reference materials (checklists, clause libraries) with LLM legal reasoning

### Out of Scope

- Litigation support — Sara is a transactional associate (future practice area expansion)
- General practice areas beyond real estate — MVP is real estate only (eventual expansion planned)
- Client-facing communication without partner review — Sara delivers to the partner, not directly to clients
- Real-time collaboration with other AI agents — Sara works within a single Claude Code session

## Context

Sara already exists as a working plugin with docx tools, subagents, and a contract review workflow. The core problem is quality — a PSA review test produced ~10 superficial changes when a real associate would have produced dozens of substantive markups. The architecture (plugin, tools, agents) is sound; the behavioral framework, delegation precision, and domain knowledge depth need significant improvement.

Key existing components:
- `skills/sara/SKILL.md` — behavioral framework (needs major rework)
- `agents/` — 4 subagent definitions (need precision and quality standards)
- `docx-tools/` — document processing pipeline (working, adequate)
- `references/` — workflow guides and standards (need expansion with RE-specific content)

The user is a practicing real estate attorney who will provide source materials and evaluate work product against professional standards.

## Constraints

- **Platform**: Claude Code plugin system — must work within plugin architecture (skills, agents, commands, hooks)
- **Document format**: All legal work product delivered as .docx via existing docx-tools pipeline
- **LLM context**: Contract review of long documents requires careful context management — can't fit entire PSA + analysis in one pass
- **Source materials**: User will provide RE reference library; need RAG integration to make it accessible during work
- **Quality bar**: Work product judged against actual Big Law associate standards, not "good for AI"

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Start with real estate, expand later | User's domain expertise enables quality evaluation; RE is concrete enough to test against | — Pending |
| Collaborative interaction model | Sara asks questions before complex work, doesn't just execute blindly | — Pending |
| Both reference materials + LLM knowledge | Checklists/clause libraries for structure, LLM for reasoning and drafting | — Pending |
| RAG for user-provided source library | Large reference library can't fit in context; needs retrieval system | — Pending |
| Existing docx tooling is adequate | Problem is Sara's brain (prompting/architecture), not her hands (tools) | — Pending |

---
*Last updated: 2026-02-17 after initialization*
