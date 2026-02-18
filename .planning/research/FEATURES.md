# Feature Research

**Domain:** AI law firm associate — real estate transactional
**Researched:** 2026-02-17
**Confidence:** MEDIUM-HIGH (ecosystem surveyed via WebSearch + official product pages; legal professional standards drawn from project context and practice knowledge)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features the user assumes Sara has. Missing these = Sara feels like a toy, not an associate.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Clause-by-clause disposition at Level 4-5 | A real associate marks every paragraph (Accept/Revise/Delete/Insert/Comment), not just the ones that jump out | HIGH | This is the core quality gap. The first PSA review produced ~10 changes; a thorough senior associate produces 40-80+ dispositions on a 170-paragraph PSA. Every paragraph gets a decision. |
| Market standard benchmarking per clause | Associates know what's "market," "aggressive," "one-sided" — and say so explicitly. "This indemnification cap of $500K is below market for a deal of this size; standard is 2x purchase price." | HIGH | Requires domain knowledge embedded in prompts/references, not just extraction. Spellbook and Gavel both advertise this as a core differentiator. |
| Risk-relationship mapping | Provisions interact — a short DD period + hard deposit + AS-IS clause form a compound risk. Associates think in risk clusters, not isolated clauses | HIGH | Already in contract-review-workflow.md as a concept; the gap is execution — current system doesn't do this in practice |
| Complete deliverable package | Redline + transmittal memo + open items list. "Never send a naked redline" — this is a Big Law professional norm | MEDIUM | Workflow already defines this; execution gap is that prior reviews skipped the transmittal package |
| Cross-reference verification | Changes to one clause cascade to related provisions (DD termination rights affect deposit provisions, default remedies, leasing covenants) | HIGH | Explicitly called out in project lessons learned as the primary failure mode of the first PSA review |
| Practice-area-specific analysis framework | RE review of a PSA must cover DD period mechanics, title cure, deposit hard-going, estoppel conditions — not just generic contract risk categories | HIGH | Contract review workflow Step 3 defines this but relies on the LLM knowing what to research; current execution is too generic |
| Precise draft language in redlines | "Delete 'material'" is not a markup. The associate drafts replacement language: "Replace 'material adverse effect' with 'any adverse effect, whether or not material'" | HIGH | Contract-reviser agent is designed for this; gap is the quality of the language it produces |
| Aggressiveness calibration | Level 1 = accept market terms, Level 5 = push every clause maximally. Calibration must change *scope* (every paragraph reviewed vs. flagged items only), not just language tone | MEDIUM | Defined in workflow; execution gap is scope change isn't reliably triggered |
| Legal research integration | Associates research market terms, jurisdictional issues, recent case law affecting deal structure before writing their markup | MEDIUM | legal-researcher agent exists; gap is quality of research prompts and integration back into the review framework |
| Structured intake questioning | Before starting complex work, Sara asks: Who's the client? What's the representation? What's the aggressiveness? What's the commercial objective? | LOW | Already defined in workflow Step 1; needs reliable enforcement |
| Work product directory and audit trail | All output organized by matter; prompt-log.md for transparency | LOW | Already implemented |

### Differentiators (Competitive Advantage)

Features that distinguish Sara from commodity AI contract review tools (Spellbook, Kira, Harvey). These are what make the user keep using Sara over switching to a purpose-built tool.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| RAG from user-provided reference library | Sara draws on the user's own precedents, forms, playbooks, and checklists — not generic training data. A RE attorney's library of forms beats any AI's generic knowledge. | HIGH | Identified in PROJECT.md as a key decision; no tool currently implemented. Requires vector DB or document store. High value because user's own clause preferences > market averages. |
| Counterparty argument anticipation | For each proposed change, Sara explains why opposing counsel will push back and how to respond. "The seller will argue this is standard; the market data shows 78% of PSAs in this market include a 5-day cure period." | HIGH | No existing AI tool does this reliably at clause level. Big Law associates do this instinctively. |
| RE-specific document interconnection | Sara understands how a title commitment schedule B-II exception connects to the survey, the AS-IS clause, and the indemnification section — not as separate documents but as a system | HIGH | Orbital Copilot (purpose-built RE AI) advertises this as core capability. Sara can do this via careful orchestration if given all documents. Complexity is prompting and context management. |
| Parallel research + review | Sara runs research concurrently with review steps rather than sequentially — shaving turnaround time | MEDIUM | Subagent architecture supports this; workflow currently does it sequentially |
| Transmittal memo calibrated to deal context | The transmittal memo isn't boilerplate — it reflects the specific commercial context, the client's priorities, and Sara's negotiation strategy recommendations | MEDIUM | Current template is structural; differentiation is in the quality of content and strategic framing |
| Disposition table for every paragraph | Section A of document-reviewer output: a table where every paragraph has a disposition (Accept/Revise/Delete/Insert/Comment) with reasoning. This is what distinguishes a thorough review from issue-spotting. | HIGH | Already defined in document-reviewer spec; execution gap is completeness and quality of reasoning |
| RE-specific clause library as reference | Sara's reference materials include a clause library of preferred RE language (buy-side DD provisions, seller's AS-IS disclaimers, title cure obligations) that she draws on when drafting replacements | HIGH | Not yet implemented. Would dramatically improve quality of proposed replacement language. |
| Closing checklist and deal calendar generation | From a PSA, Sara can generate a closing checklist, timeline, and responsibility matrix — turning a document into an actionable deal management tool | MEDIUM | Not implemented. High value for transactional practice. Standard product at major firms. |
| Title commitment + survey + underlying doc review | Sara reviews the title commitment, exception documents, and survey as an integrated package — not separately | HIGH | Orbital Copilot does this as their core differentiator. Requires providing all documents to Sara and orchestrating cross-document analysis. |
| Correspondence drafting at professional quality | Demand letters, response letters to opposing counsel, status memos to clients — Sara drafts at a level the partner can send with minimal edits | MEDIUM | Referenced in work-product-standards.md but no specific agent or workflow for correspondence |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem useful but would undermine Sara's quality, scope, or the user's workflow.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Automatic sending of correspondence | Efficiency — why draft if AI can send? | Sara is an associate, not a partner. The partner retains decision authority. Auto-sending removes review and creates professional liability. | Sara drafts + recommends; partner approves and sends |
| Client-facing output without partner review | Speed — skip the intermediary | Professional responsibility requires partner supervision. Sara's work product is always subject to attorney review. The plugin architecture makes this impossible to enforce at scale. | Sara always delivers to partner; partner reviews before forwarding |
| Litigation support features | Complete legal service | Sara is transactional. Litigation requires different expertise, workflows, and tools (brief writing, discovery, motion practice). Scope creep here dilutes the transactional quality focus. | Separate "litigation associate" skill if needed later |
| Real-time multi-party collaboration | Modern workflow expectation | Claude Code is a single-session, single-user tool. Multi-party features require infrastructure Sara doesn't have and would complicate the architecture. | Share work product as files; Sara works within one attorney's workflow |
| Generic "summarize this contract" mode at Level 4-5 | Fast intake | Summaries at high aggressiveness levels are insufficient — they miss the disposition-level review. At Level 1-2, summaries are appropriate. At Level 4-5, summaries are a trap that produces the ~10 changes problem. | Enforce the full 7-step workflow at Level 4-5; reserve summaries for Level 1-2 orientation passes |
| Fully automated redline without Sara judgment step | Speed | Automated redlines without senior review produce low-quality markup — the kind that embarrasses the firm. The human-in-the-loop step (Sara reviewing contractor-reviser output) is not optional. | Batch revision with mandatory Sara review between batches |
| Generic legal AI responses outside RE | Covering all practice areas | Quality comes from depth. Sara as a generic legal AI would be mediocre at everything. The RE specialization is what makes her good enough for a practicing attorney. | Hard scope to RE transactional; expand to other practice areas as distinct milestones |
| Auto-filing or docket integration | Convenience | Scope creep into practice management software. No current infrastructure. Creates liability if misfiled. | Out of scope entirely; refer to dedicated practice management tools |

---

## Feature Dependencies

```
[RAG Reference Library]
    └──enhances──> [Market Standard Benchmarking]
    └──enhances──> [RE-Specific Clause Library]
    └──enhances──> [Precise Draft Language in Redlines]

[Structured Intake Questioning]
    └──requires──> [Practice-Area Analysis Framework]
    └──requires──> [Aggressiveness Calibration]

[Practice-Area Analysis Framework]
    └──requires──> [Legal Research Integration]
    └──enables──> [Clause-by-Clause Disposition]
    └──enables──> [Risk-Relationship Mapping]

[Clause-by-Clause Disposition]
    └──requires──> [Practice-Area Analysis Framework]
    └──enables──> [Precise Draft Language in Redlines]
    └──enables──> [Complete Deliverable Package]

[Precise Draft Language in Redlines]
    └──requires──> [Clause-by-Clause Disposition]
    └──enhanced by──> [RE-Specific Clause Library]
    └──enhanced by──> [RAG Reference Library]

[Complete Deliverable Package]
    └──requires──> [Precise Draft Language in Redlines]
    └──requires──> [Transmittal Memo (Context-Calibrated)]
    └──requires──> [Cross-Reference Verification]

[Title + Survey + Underlying Doc Review]
    └──requires──> [RE-Specific Document Interconnection]
    └──enhanced by──> [RAG Reference Library]

[Counterparty Argument Anticipation]
    └──requires──> [Market Standard Benchmarking]
    └──enhanced by──> [Legal Research Integration]

[Closing Checklist Generation]
    └──requires──> [Clause-by-Clause Disposition] (have to know what was agreed)
    └──uses──> [Practice-Area Analysis Framework]
```

### Dependency Notes

- **Clause-by-clause disposition requires Practice-Area Analysis Framework:** You cannot disposition every clause well without knowing what good looks like for each clause type in this deal context. The framework (Step 3 of contract-review-workflow.md) has to be built before the review starts.
- **Precise draft language is enhanced by RE-Specific Clause Library:** Without a clause library, Sara invents replacement language from scratch every time — inconsistent and slower. With a library, she pulls preferred language and adapts it.
- **RAG enhances multiple features but is not required for any single one:** RAG is a force multiplier, not a prerequisite. Everything works without it, but quality improves significantly with it.
- **Complete deliverable package requires cross-reference verification:** A redline where changes cascade incorrectly (e.g., changed DD termination right but didn't update deposit return provision) is worse than no redline — it creates professional liability.

---

## MVP Definition

### Launch With (v1) — Fix the Quality Gap

The core problem is a PSA review producing ~10 superficial changes instead of 40-80+ substantive ones. Everything in this MVP directly attacks that problem.

- [ ] **Mandatory clause-by-clause disposition at Level 4-5** — Every paragraph in every section gets a disposition table entry (Accept/Revise/Delete/Insert/Comment). Non-negotiable at high aggressiveness. The document-reviewer agent must output this by design, not optionally.
- [ ] **Practice-area analysis framework enforcement** — Contract review cannot proceed past Step 3 without a built target concept list and target risk list tailored to RE transaction type and representation. These must be written to file before review begins.
- [ ] **Substantive replacement language quality** — Contract-reviser batches must produce full draft paragraphs with specific legal rationale, not hedged descriptions of what could be changed. "To Seller's actual knowledge" not "consider adding a knowledge qualifier."
- [ ] **Cross-reference verification as a checklist item** — Sara's quality checklist must include explicit cross-reference verification before generating the redline. Workflow already defines this; needs enforcement.
- [ ] **Complete transmittal package enforcement** — Workflow must produce all three deliverables or be considered incomplete. The transmittal memo and open items list are not optional appendices.
- [ ] **Market standard citations** — Every substantive markup must include a brief rationale citing market standard. "This provision is unusual — standard market language provides a 5-business-day cure period."

### Add After Validation (v1.x) — Depth and Coverage Expansion

Features to add once the core quality gap is closed and the user confirms v1 output meets professional standards.

- [ ] **RE-specific clause library** — A curated library of preferred clause language for common RE transactional provisions, organized by deal type and party representation. Sara pulls from this when drafting replacement language. Add when: user provides feedback that replacement language is too generic.
- [ ] **Title commitment + survey review workflow** — A dedicated workflow for reviewing title commitments, schedule B-II exceptions, underlying documents, and surveys as an integrated package. Add when: user assigns a title review task.
- [ ] **Closing checklist and deal calendar** — From a finalized PSA, Sara generates a closing checklist, timeline, and responsibility matrix. Add when: user asks for deal management output post-review.
- [ ] **Correspondence drafting workflow** — Dedicated workflow for demand letters, response letters to opposing counsel, and status memos. Add when: user assigns a correspondence task.
- [ ] **Counterparty argument anticipation** — For each major markup, Sara includes a brief note on expected pushback and suggested response. Add when: v1 clause-level quality is confirmed adequate.

### Future Consideration (v2+) — Architecture Changes Required

Features that require new infrastructure, not just better prompting.

- [ ] **RAG from user-provided reference library** — Vector database integration so Sara can retrieve relevant precedents, forms, and checklists from the user's document library during review. Defer because: requires infrastructure build (vector DB, embedding pipeline, retrieval integration) that is separate from the behavioral quality work. Trigger: user accumulates enough reference material to make retrieval valuable.
- [ ] **Parallel subagent orchestration** — Running research and review concurrently rather than sequentially to reduce turnaround time. Defer because: sequential is easier to control for quality; parallel requires careful output merging and conflict resolution. Trigger: turnaround time becomes a user complaint.
- [ ] **Multi-document cross-analysis** — Analyzing a PSA, loan commitment, title commitment, and survey simultaneously with explicit cross-document relationship mapping. Defer because: context management for multiple long documents is complex and requires RAG infrastructure. Trigger: user assigns a multi-document package.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Clause-by-clause disposition (Level 4-5) | HIGH | MEDIUM (prompting/workflow) | P1 |
| Practice-area analysis framework enforcement | HIGH | MEDIUM (prompting/workflow) | P1 |
| Substantive replacement language quality | HIGH | MEDIUM (agent instructions) | P1 |
| Complete transmittal package enforcement | HIGH | LOW (workflow enforcement) | P1 |
| Cross-reference verification checklist | HIGH | LOW (workflow checklist) | P1 |
| Market standard citations in markups | HIGH | MEDIUM (domain knowledge prompts) | P1 |
| RE-specific clause library | HIGH | HIGH (content creation) | P2 |
| Title commitment + survey review workflow | HIGH | HIGH (new workflow) | P2 |
| Counterparty argument anticipation | MEDIUM | MEDIUM (prompting) | P2 |
| Closing checklist generation | MEDIUM | MEDIUM (new workflow) | P2 |
| Correspondence drafting workflow | MEDIUM | MEDIUM (new workflow) | P2 |
| RAG reference library integration | HIGH | HIGH (new infrastructure) | P3 |
| Parallel subagent orchestration | LOW | HIGH (orchestration complexity) | P3 |
| Multi-document cross-analysis | MEDIUM | HIGH (context + infrastructure) | P3 |

**Priority key:**
- P1: Core quality gap — must fix before the user finds Sara useful for professional work
- P2: Depth expansion — adds coverage and differentiation once core quality is solid
- P3: Infrastructure investment — requires architectural work, not just prompting

---

## Competitor Feature Analysis

These are the tools the user implicitly compares Sara against when evaluating quality.

| Feature | Spellbook | Harvey AI | Kira Systems | Orbital Copilot | Sara's Target |
|---------|-----------|-----------|--------------|-----------------|---------------|
| Contract review mode | Clause-level review with redline suggestions in Word | Document Q&A, issues list, clause strengthening | ML-based clause extraction from large doc sets | RE-specific due diligence automation | Clause-by-clause disposition at associate level of depth |
| Market standard benchmarking | Yes — compares to industry norms | Yes — based on precedents/playbooks | Yes — trained on 45K+ lawyer-reviewed contracts | RE-specific norms | Yes — with explicit citations |
| Redline generation | Native Word track changes | Issues list → lawyer-executed redline | Extractions → lawyer-executed redline | Not primary use case | Native .docx track changes via redline_docx tool |
| Complete deliverable package | Review report only (no transmittal memo) | Issues list only | Extraction report only | Due diligence summary | Full package: redline + transmittal memo + open items |
| RE-specific analysis | Generic real estate clauses | Generic (broad practice scope) | Limited | Deep RE specialization | RE-specific workflows by document type |
| Title/survey review | No | No | No | Yes (core feature) | Planned (v1.x) |
| Counterparty argument prep | No | No | No | No | Planned (v1.x) |
| RAG from firm's documents | Playbooks (rule-based) | Yes (trained on firm's docs) | Yes (trained on extractions) | RE domain training | Planned (v2) |
| Works within attorney workflow | Word add-in | Browser/API | Separate platform | Separate platform | Claude Code session (native to partner's environment) |

**Key competitive observation (MEDIUM confidence, multiple sources):**
No existing tool produces a complete transmittal package (redline + memo + open items list). This is a Big Law professional norm that AI tools universally skip — likely because their target buyer is in-house counsel or CLM teams, not law firm associates. For a practicing attorney, the package completeness is non-negotiable. This is Sara's core differentiator if she executes it well.

---

## Sources

- [6 Best AI Tools for Real Estate Lawyers in 2026 — Spellbook](https://www.spellbook.legal/learn/best-ai-tools-for-real-estate-lawyers) (MEDIUM confidence — marketing content, but feature descriptions consistent across multiple sources)
- [Spellbook Contract Review Features](https://www.spellbook.legal/features/review) (MEDIUM confidence — official product page)
- [Harvey AI Transactional](https://www.harvey.ai/solutions/transactional) (MEDIUM confidence — official product page)
- [Orbital Copilot — What Legal AI Misses in Real Estate](https://www.orbital.tech/blog/more-than-words-what-legal-ai-misses-in-real-estate-document-reviews) (MEDIUM confidence — vendor content, but specific about RE gaps)
- [Rethinking Real Estate Legal AI](https://www.orbital.tech/blog/rethinking-real-estate-legal-ai-why-your-practice-area-demands-a-specialized-approach) (MEDIUM confidence — vendor content)
- [How Real Estate Lawyers Use AI for Contract Drafting and Redlining — Gavel](https://www.gavel.io/resources/how-real-estate-lawyers-use) (MEDIUM confidence — practitioner-focused content)
- [Best AI Contract Review Tools for Lawyers — Gavel](https://www.gavel.io/resources/best-ai-contract-review-tools-for-lawyers-in-2026) (MEDIUM confidence — comparative review)
- [Real Estate Due Diligence AI — Magistral Consulting](https://magistralconsulting.com/real-estate-due-diligence-ai-automation-for-speed-accuracy/) (LOW confidence — consulting firm content)
- Project source: `skills/sara/references/contract-review-workflow.md` (HIGH confidence — defines current intended behavior)
- Project source: `.planning/PROJECT.md` (HIGH confidence — defines validated gaps)
- Project memory: `MEMORY.md` lessons learned (HIGH confidence — post-mortem from actual PSA review test)

---

*Feature research for: AI law firm associate — real estate transactional*
*Researched: 2026-02-17*
