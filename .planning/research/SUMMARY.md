# Project Research Summary

**Project:** Sara AI Associate — Quality Overhaul & RAG Capabilities
**Domain:** AI law firm associate plugin (Claude Code) — real estate transactional
**Researched:** 2026-02-17
**Confidence:** HIGH (architecture grounded in official Anthropic docs + observed failure; stack verified against PyPI; pitfalls validated against real PSA review failure)

## Executive Summary

Sara is a Claude Code plugin that functions as a law firm associate persona specializing in real estate transactional work. The central finding from all four research tracks is a single, concrete quality gap: the first PSA review produced ~19 substantive changes on a 170-paragraph document when a competent senior associate would produce 40-80+. This is not a bug — it is the default behavior of an LLM given a vague instruction ("review this contract") without explicit completion criteria, structured workflows, domain-specific knowledge, or quality gates. Every research track points to the same root cause: insufficient scaffolding that forces depth, completeness, and deal-specificity.

The recommended approach is a behavioral overhaul before any infrastructure investment. The architecture (multi-pass workflow, subagent delegation, file-based state) is sound and well-grounded in Anthropic's own documentation. The failure is execution: Sara's SKILL.md, the subagent prompts, the delegation model, and the knowledge layer are all underdeveloped relative to what the workflow requires. The highest-value work is building the knowledge layer (RE-specific checklists, market standards, clause libraries) and tightening the behavioral specifications (paragraph-level disposition requirements, delegation context packing, quality gate enforcement). These are prompting and content investments, not infrastructure ones.

RAG is confirmed as the right long-term architecture for reference library integration, with a clear, validated stack (ChromaDB + sentence-transformers + bm25s + pymupdf4llm + FastMCP). However, RAG is a force multiplier on a working foundation, not a substitute for one. The research is unambiguous: ship the quality overhaul first, validate that Sara's output meets professional standards, then layer in RAG. Attempting RAG before the behavioral foundation is solid would improve retrieval of knowledge that Sara cannot currently apply well.

## Key Findings

### Recommended Stack

The RAG stack is purpose-built for a local, single-user Claude Code plugin. ChromaDB 1.5.0 in embedded mode (zero server setup, SQLite+DuckDB persistence) is the right vector store for this scale. The embedding strategy is two-tier: local default using `BAAI/bge-large-en-v1.5` via sentence-transformers (offline, CPU-capable, ~1.3 GB download), with optional upgrade to `voyage-law-2` via Voyage AI API (6-15% better on legal benchmarks, first 50M tokens free). The hybrid retrieval pattern (dense vector + BM25 keyword via bm25s + cross-encoder reranking) is critical for legal text because exact term matching ("Section 4.2(c)") must work alongside semantic search. All new dependencies integrate into the existing docx-tools pyproject.toml managed by uv.

**Core technologies:**
- ChromaDB 1.5.0: local vector store — embedded mode, zero server setup, Rust-core performance
- sentence-transformers 5.2.3: local embeddings — CPU-capable, no API dependency, bge-large-en-v1.5 default
- bm25s 0.2.x: keyword/lexical search — 100-500x faster than rank-bm25, essential for section number matching
- pymupdf4llm 0.3.4: PDF ingestion — purpose-built for RAG, structure-aware markdown conversion
- FastMCP 2.14.5: MCP server — already in use, extend existing server rather than introduce a second one
- voyageai (optional): voyage-law-2 — best-in-class legal embeddings when API key is available

**Critical version notes:** Pin FastMCP to 2.14.5 (not 3.x which has breaking changes). Note pymupdf4llm dual license (AGPL/commercial) — verify compliance. ChromaDB on WSL2 may need `CHROMA_SERVER_NOFILE=65536` for large ingestion.

### Expected Features

The feature research identified a clear priority structure driven by the PSA review failure. Everything in the MVP attacks the same core problem: reviews that look thorough but cover only a fraction of what they should.

**Must have (table stakes — fix before anything else):**
- Clause-by-clause disposition at Level 4-5 — every paragraph gets Accept/Revise/Delete/Insert/Comment; "no disposition" is not allowed
- Practice-area analysis framework enforcement — Step 3 cannot be skipped; builds the target concept and risk lists before review begins
- Substantive replacement language — full draft paragraphs with legal rationale, not hedged descriptions
- Complete transmittal package — redline + transmittal memo + open items list; redline alone is never complete
- Cross-reference verification — explicit conforming changes reconciliation before final revision set compilation
- Market standard citations in every substantive markup — sourced claims distinguished from analytical judgment

**Should have (competitive differentiators — add after MVP validation):**
- RE-specific clause library — preferred language for common RE provisions, dramatically improves replacement quality
- Title commitment + survey integrated review — dedicated workflow for reviewing the full title package as a system
- Counterparty argument anticipation — per-markup note on expected pushback and suggested response
- Closing checklist and deal calendar generation — turning a PSA into an actionable deal management tool
- Correspondence drafting workflow — demand letters, response letters, status memos at professional quality

**Defer to v2+ (infrastructure required):**
- RAG from user-provided reference library — vector DB + embedding pipeline; defer until behavioral foundation is solid
- Parallel subagent orchestration — complex output merging; defer until sequential quality is confirmed
- Multi-document cross-analysis — requires RAG infrastructure and context management not yet built

**Anti-features to avoid:** Auto-sending correspondence, client-facing output without partner review, litigation support features, generic "summarize this contract" mode at Level 4-5, fully automated redline without Sara judgment step.

**Key competitive observation:** No existing AI legal tool (Spellbook, Harvey, Kira, Orbital Copilot) produces a complete transmittal package. This is Sara's core differentiator if she executes it consistently.

### Architecture Approach

The architecture is well-defined and sound. Five patterns drive the system: multi-pass analysis (7-step workflow producing structured intermediate artifacts at each step), context-isolated subagent delegation (subagents receive scoped work packages, not full documents), playbook-driven analysis (domain-specific knowledge layer defines what to look for and what is market), filesystem-as-working-memory (all analytical state externalized to structured markdown files for session continuity), and Sara-reviews-junior-work quality gate (no subagent output becomes a deliverable without Sara's explicit review).

The component dependency graph identifies a clear build order: docx tooling (Levels 0-1) is complete and adequate; subagent definitions (Level 2) need refinement; the knowledge layer (Level 3) is the critical missing piece; Sara's orchestration logic (Level 4) needs major improvement; the workflow reference file (Level 5) is adequate but execution against it is not enforced.

**Major components:**
1. Sara SKILL.md (orchestrator) — persona, decision-making, multi-pass enforcement, quality gates, delegation precision
2. Knowledge Layer (new, critical gap) — RE checklists, market standards, clause libraries in `skills/sara/references/knowledge/`
3. Subagent agents (legal-researcher, document-reviewer, contract-reviser, document-drafter) — need prompt refinement
4. Document tooling (docx-tools MCP/CLI) — already complete, adequate for all planned features
5. Work product filesystem — state persistence, audit trail, already implemented

**Key data flow insight:** Paragraph IDs from `read_docx` (p_1, p_2, ...) are the coordination key throughout the entire system — concept map, risk map, batch dispatches, revision JSON all use these IDs. Any break in this chain breaks the whole workflow.

### Critical Pitfalls

Eight pitfalls were identified. All eight are preventable with the Quality Overhaul phase; four have specific technical solutions in the RAG Integration phase.

1. **Shallow pass mistaken for complete review** — Require paragraph-level disposition table (Accept/Revise/Delete/Insert/Comment) for every paragraph at Level 4-5. Add hard floor to Sara's SKILL.md: 35+ revision entries on a 150-paragraph PSA at Level 4, 40+ at Level 5. Sara reports coverage ratio before presenting to partner.

2. **Overconfident wrong legal analysis** — Distinguish sourced claims from analytical claims in output. Flag "market standard" assertions as requiring attorney validation unless sourced from the knowledge layer. Prohibit case citations without verified source. RAG against user-provided reference materials is the long-term mitigation (Stanford HAI research shows 17-34% hallucination rate even with RAG; 75%+ without it).

3. **Vague delegation producing generic junior output** — Every subagent delegation must include representation + aggressiveness + target risk list + paragraph ID map + defined terms + explicit output format. Delegation prompts under 200 words should be rejected. Sara logs every delegation in prompt-log.md before dispatching.

4. **Cross-reference blindness on conforming changes** — Batch sequentially (never in parallel). Every batch output must include a "Conforming Changes Required" section. Sara runs a conforming-changes reconciliation pass after all batches complete, before compiling the final revision set.

5. **Context degradation on long documents (lost-in-the-middle)** — Structure review in sequential article-by-article passes. Never ask a single agent to review a 170-paragraph document in one pass. Position highest-priority provisions at the start of each batch. Validate that risk map entries are distributed proportionally across document sections.

Additional pitfalls (lower severity but important): generic language instead of deal-specific drafting (requires defined-terms injection in every batch), naked redline delivery (transmittal package must be mandatory in workflow), and aggressiveness not changing scope (Level 4-5 must change coverage requirements, not just tone calibration).

## Implications for Roadmap

Based on combined research, the following phase structure is strongly recommended:

### Phase 1: Behavioral Foundation (Quality Overhaul)

**Rationale:** All pitfalls originate from behavioral failures, not infrastructure gaps. The multi-pass workflow and subagent architecture are already in place — the problem is how Sara executes them. This phase delivers the core quality improvement before any new infrastructure is added. Everything else depends on this being right.

**Delivers:** A Sara that reliably produces 40+ substantive revision entries on a PSA, with complete transmittal packages, proper cross-reference handling, and quality-gated junior output.

**Addresses (from FEATURES.md):** All six P1 features — clause-by-clause disposition, practice-area framework enforcement, substantive replacement language, transmittal package enforcement, cross-reference verification, market standard citations.

**Avoids (from PITFALLS.md):** Pitfalls 1 (shallow pass), 3 (vague delegation), 4 (cross-reference blindness), 7 (naked redline), 8 (aggressiveness scope problem).

**Work involved:**
- Rewrite Sara's SKILL.md with explicit aggressiveness-level scope requirements, coverage floor, and quality gate definitions
- Upgrade document-reviewer agent instructions: disposition table format, minimum entry counts per aggressiveness level, paragraph ID requirements
- Upgrade contract-reviser agent instructions: defined-terms injection, deal-specific language requirements, conforming changes section
- Upgrade delegation model: briefing template format, mandatory context fields, rejection criteria
- Build RE-specific PSA checklist (re-checklist-psa.md) — the minimum viable knowledge layer for PSA review

**Research flag:** LOW — standard patterns, existing code, high-confidence architecture. No phase-level research needed.

### Phase 2: Knowledge Layer Buildout

**Rationale:** The behavioral foundation (Phase 1) tells Sara how to analyze; the knowledge layer tells her what to analyze for and what good looks like. The PSA checklist is the MVP knowledge artifact, but a full library covering leases, market standards, and model clause language requires systematic content creation. This directly enables the "market standard benchmarking" feature that all competitive tools advertise.

**Delivers:** RE-specific checklists (PSA and commercial lease), market standards reference file, clause library for critical provision types (indemnification, representations, termination, dispute resolution). These are the reference files Sara loads during Step 3 (framework building).

**Addresses (from FEATURES.md):** RE-specific clause library (P2), market standard benchmarking improvement, counterparty argument anticipation foundation.

**Avoids (from PITFALLS.md):** Pitfall 2 (overconfident wrong analysis), Pitfall 6 (generic vs. deal-specific language).

**Architecture note:** Knowledge files live in `skills/sara/references/knowledge/` as structured markdown. Sara reads them via the Read tool during Step 3. This requires no new infrastructure — it is a content investment.

**Research flag:** LOW for structure; MEDIUM for content accuracy. The checklist and market standards content should be validated by the user (a practicing RE attorney) before Sara relies on them heavily. Flag knowledge files as "user-validation required" during planning.

### Phase 3: Additional Document Type Workflows

**Rationale:** Once the PSA review workflow is proven at professional quality (validated by user feedback after Phase 1-2), expand to adjacent document types. Title commitment + survey review is the most requested unimplemented feature and is Sara's closest competitive gap against Orbital Copilot. Closing checklist generation and correspondence drafting are high-value, medium-complexity additions.

**Delivers:** Title commitment + schedule B-II review workflow, closing checklist and deal calendar generation from finalized PSAs, correspondence drafting workflow (demand letters, response letters, client memos).

**Addresses (from FEATURES.md):** Title + survey review (P2), closing checklist generation (P2), correspondence drafting (P2).

**Avoids (from PITFALLS.md):** Anti-pattern of scope creep into litigation support; each new workflow should be as tightly scoped as the PSA workflow.

**Research flag:** MEDIUM — title commitment review in particular has distinct analysis patterns (Schedule B-II exceptions, underlying document review, survey correlation) that warrant a dedicated research pass during planning.

### Phase 4: RAG Reference Library Integration

**Rationale:** With a quality-proven behavioral foundation and a knowledge layer in place, RAG becomes a force multiplier rather than a speculative infrastructure investment. The user's own reference materials (form agreements, firm playbooks, deal experience) should inform Sara's work. This phase also addresses the hallucination problem more systematically — retrieval from verified source materials replaces pattern-matching from training data.

**Delivers:** Vector database integration allowing Sara to retrieve relevant precedents, model language, and reference materials from the user's document library during Step 3 (framework building) and replacement language drafting. Two-tier embedding (local default / Voyage AI premium).

**Uses (from STACK.md):** ChromaDB 1.5.0, sentence-transformers/bge-large-en-v1.5, bm25s, pymupdf4llm, optional voyageai. Extend existing FastMCP server. Add to docx-tools pyproject.toml via uv.

**Implements (from ARCHITECTURE.md):** Knowledge Layer extension — `user-materials/` directory becomes the RAG source; `read_docx` + `pymupdf4llm` pipeline for ingestion; hybrid retrieval (dense + BM25 + reranking) for query.

**Avoids (from PITFALLS.md):** Client confidentiality (never index client work product — reference materials only), context degradation (chunk at provision/section level, not full documents), overconfident analysis (retrieval from verified sources beats LLM pattern matching).

**Research flag:** HIGH — RAG integration for legal documents has well-documented patterns (STACK.md covers them) but implementation details (chunking strategy for legal provisions, metadata schema, collection structure) warrant a focused research pass during planning. Section-boundary chunking at 400-600 tokens with 100-token overlap is the recommended starting point.

### Phase Ordering Rationale

- **Quality before infrastructure:** RAG improves retrieval of knowledge that Sara cannot yet apply well. Inverting this order produces a system that retrieves good references and still produces shallow reviews.
- **Behavioral changes first:** Phases 1-2 are entirely prompting and content work — highest return per unit of effort with zero infrastructure risk. Fail fast here if the approach is wrong.
- **Feature expansion after validation:** Phase 3 should not begin until the user confirms Phase 1-2 output meets professional standards on at least 2-3 PSA reviews.
- **Infrastructure last:** Phase 4 requires the most technical investment and has the most integration risk. Building it on a validated foundation is much safer than building it speculatively.
- **Parallel RAG research:** The STACK.md research can inform early architecture decisions for Phase 4 during Phase 2/3 planning — no need to wait until Phase 4 starts to lock in the stack.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Title Commitment Workflow):** Title commitment analysis has distinct domain patterns (schedule B-II exceptions, curative requirements, endorsement options, survey correlation). A targeted research pass is warranted before designing the workflow. Standard legal AI tools mostly skip this, so community precedent is sparse.
- **Phase 4 (RAG Integration):** Implementation-level decisions — metadata schema, collection architecture, chunking validation, hybrid search tuning — benefit from a focused research pass. The STACK.md provides the starting point; a phase-level research task should address the legal-specific implementation details.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Behavioral Foundation):** All components exist; this is refinement work. Anthropic's official documentation on subagent patterns and the existing codebase provide sufficient guidance.
- **Phase 2 (Knowledge Layer):** Content creation, not technical implementation. The structure is defined; the work is writing the checklist and market standards content, which the user (as a practicing RE attorney) is best positioned to validate.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core libraries verified against PyPI (current versions as of 2026-02-17); legal RAG architecture validated against ACL 2025 peer-reviewed research and production precedent (knowledge-rag project). Voyage AI benchmark claims are vendor-sourced (MEDIUM on that specific claim). |
| Features | MEDIUM-HIGH | Table stakes features validated against observed failure (HIGH confidence). Competitive feature landscape from vendor marketing content (MEDIUM confidence). MVP scope grounded in first-principles analysis of the quality gap — very likely correct, but user validation of what constitutes "good enough" quality is needed. |
| Architecture | HIGH | All five patterns grounded in official Anthropic documentation (Claude Code subagent docs, Anthropic engineering blog). Existing codebase directly analyzed. Build order derived from dependency analysis. |
| Pitfalls | HIGH | Pitfalls 1, 4, 7, 8 are observed failures from the actual PSA review (direct evidence). Pitfalls 2 and 5 validated by peer-reviewed research (Stanford HAI, Liu et al. TACL 2024). Pitfall 3 validated by multi-agent LLM research. Pitfall 6 validated by 2025 legal AI lessons-learned. |

**Overall confidence:** HIGH

### Gaps to Address

- **Market standards accuracy:** The knowledge layer content (re-checklist-psa.md, market-standards.md) will be written based on general legal knowledge. The user (a practicing RE attorney) must review and validate these files before Sara relies on them for professional work. Flag as "user validation required" in Phase 2 planning.
- **Voyage AI benchmark independence:** The 6-15% improvement claim for voyage-law-2 over other embeddings is from Voyage AI's own benchmarks. Independent validation is not available. The claim is directionally likely correct (domain-specific embeddings consistently outperform general ones in NLP research) but the specific magnitude should not be treated as a hard number.
- **Aggressiveness level thresholds:** The specific numbers proposed in PITFALLS.md (35+ entries at Level 4, 40+ at Level 5 for a 150-paragraph PSA) are grounded in analysis of what professional quality requires, but not empirically validated. These thresholds need calibration against real reviews once Phase 1 is implemented.
- **WSL2 ChromaDB file limit:** ChromaDB 1.5.x on WSL2 may require `CHROMA_SERVER_NOFILE=65536` environment variable for large ingestion. Not a blocker but needs verification during Phase 4 implementation.

## Sources

### Primary (HIGH confidence)
- Official Anthropic documentation: Claude Code subagent creation, multi-agent research system blog post — architecture patterns
- Observed PSA review failure (2026-02-15): 10 changes on 170-paragraph document — pitfalls grounding
- Project MEMORY.md: post-mortem lessons learned from first PSA review — feature priorities
- Existing project codebase: direct analysis of SKILL.md, contract-review-workflow.md, agents/, docx-tools/ — architecture baseline
- PyPI (chromadb, sentence-transformers, fastmcp, pymupdf4llm): version verification 2026-02-17 — stack currency
- Liu et al., "Lost in the Middle" (TACL/MIT Press, 2024): 30%+ middle-context degradation — Pitfall 5
- Stanford HAI / Journal of Legal Analysis (2024): 17-34% hallucination in legal RAG — Pitfall 2

### Secondary (MEDIUM confidence)
- Voyage AI docs and blog: voyage-law-2 pricing, benchmark claims — stack recommendations
- ACL 2025 NLLP Workshop: section-aware chunking for legal documents — chunking strategy
- knowledge-rag GitHub project: ChromaDB + BM25 + FastMCP production precedent — architecture validation
- Commercial legal AI product pages (Spellbook, Harvey, Orbital Copilot, Gavel): feature landscape — competitive context
- claudefa.st: subagent invocation failure patterns — delegation pitfalls
- Definely/LawNext: conforming change tracking problem — cross-reference pitfall
- Artificial Lawyer (2025): contract AI reliability and prompt engineering — pitfall context
- arXiv 2512.08769: multi-agent instruction adherence degradation — delegation pitfalls

### Tertiary (LOW confidence)
- Lexology, Jones Walker AI Law Blog: AI drafting lessons 2025 — general context only; not relied upon for specific recommendations

---
*Research completed: 2026-02-17*
*Ready for roadmap: yes*
