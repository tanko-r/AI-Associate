# Architecture Research

**Domain:** AI legal assistant plugin — deep contract analysis and delegation
**Researched:** 2026-02-17
**Confidence:** HIGH (based on official Claude Code documentation + Anthropic engineering blog + direct code analysis)

---

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                           │
│  /sara [practice-area]  ←→  Partner (user) in Claude Code session   │
└─────────────────────────┬───────────────────────────────────────────┘
                          │  Command activation
┌─────────────────────────▼───────────────────────────────────────────┐
│                     SARA ORCHESTRATOR LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  SKILL.md — persona, decision-making, quality standards,     │   │
│  │  delegation authority, document tool invocation              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  REFERENCE FILES — contract-review-workflow.md,              │   │
│  │  delegation-model.md, work-product-standards.md              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  KNOWLEDGE LAYER (proposed) — clause-library.md,             │   │
│  │  RE-checklist.md, market-standards.md, form-library/         │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────┬────────────┬───────────────┬────────────────┬──────────────┘
         │ Task tool  │               │                │
         │ delegation │               │                │
┌────────▼──────┐ ┌──▼────────────┐ ┌▼─────────────┐ ┌▼──────────────┐
│ legal-        │ │ document-     │ │ contract-    │ │ document-     │
│ researcher    │ │ reviewer      │ │ reviser      │ │ drafter       │
│ (3rd year)    │ │ (3rd year)    │ │ (3rd year)   │ │ (2nd year)    │
│               │ │               │ │              │ │               │
│ Context:      │ │ Context:      │ │ Context:     │ │ Context:      │
│ research Q,   │ │ framework +   │ │ batch of     │ │ Sara's        │
│ jurisdiction, │ │ document text │ │ paragraphs + │ │ outline +     │
│ matter dir    │ │ + target list │ │ risk map +   │ │ research +    │
│               │ │               │ │ concept map  │ │ matter dir    │
└───────┬───────┘ └──────┬────────┘ └──────┬───────┘ └──────┬────────┘
        │                │                 │                 │
        │                └────────┬────────┘                 │
        │                         │                          │
        └─────────────────────────┴──────────────────────────┘
                                  │
                         (output → files)
┌─────────────────────────────────▼───────────────────────────────────┐
│                    WORK PRODUCT FILESYSTEM                            │
│  Sara-Work-Product/[matter]/                                         │
│  ├── analysis/          ← intake-notes, initial-read,               │
│  │                         analysis-framework, concept-map, risk-map │
│  ├── research/          ← research delegation results               │
│  ├── junior-work/       ← raw subagent output (pre-review)          │
│  │   ├── researcher/                                                 │
│  │   ├── reviewer/                                                   │
│  │   ├── reviser/       ← batch-N-revisions.md files                │
│  │   └── drafter/                                                    │
│  ├── final/             ← redline.docx, transmittal-memo.md,        │
│  │                         open-items.md                             │
│  └── prompt-log.md      ← audit trail of all delegations            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    DOCUMENT TOOLING LAYER                             │
│  MCP Server (default) or CLI fallback                                │
│  ┌────────────┐ ┌───────────┐ ┌────────────┐ ┌────────────────┐    │
│  │ read_docx  │ │write_docx │ │redline_docx│ │extract_struct. │    │
│  └────────────┘ └───────────┘ └────────────┘ └────────────────┘    │
│  ┌───────────────────┐ ┌──────────────────────────────────────┐    │
│  │ compare_docx      │ │ analyze_contract                     │    │
│  └───────────────────┘ └──────────────────────────────────────┘    │
│                                                                      │
│  Core: reader.py, writer.py, redliner.py, analyzer.py,              │
│        extractor.py, comparer.py (python-docx, lxml, diff-match-p.) │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Command (`/sara`) | Entry point — activate Sara persona, set practice area | `commands/sara.md` loaded by Claude Code plugin system |
| Sara Skill | Orchestration — receive assignments, plan approach, delegate, review, deliver | `skills/sara/SKILL.md` — persona + decision logic |
| Contract Review Workflow | 7-step process definition for deep analysis | `references/contract-review-workflow.md` — consumed by Sara |
| Work Product Standards | Output format specs by document type | `references/work-product-standards.md` — consumed by Sara |
| Knowledge Layer (proposed) | Domain-specific playbooks, clause libraries, RE checklists | Markdown files in `skills/sara/references/knowledge/` |
| legal-researcher | Targeted legal research, case law, statutory analysis | `agents/legal-researcher.md` — invoked via Task tool |
| document-reviewer | First-pass review, concept map draft, risk map draft | `agents/document-reviewer.md` — invoked via Task tool |
| contract-reviser | Batched paragraph revision against risk map | `agents/contract-reviser.md` — invoked via Task tool sequentially |
| document-drafter | First-pass drafts from Sara's outline | `agents/document-drafter.md` — invoked via Task tool |
| Filesystem (work product) | State persistence across the matter | `Sara-Work-Product/[matter]/` directory tree |
| Document Tools (MCP/CLI) | .docx parsing, writing, redlining, comparison | `docx-tools/mcp_server.py` + `docx-tools/cli/` |

---

## Recommended Project Structure

The current structure is sound. The primary gap is the missing Knowledge Layer. The recommended structure adds it:

```
skills/sara/
├── SKILL.md                           # Core persona + orchestration logic
└── references/
    ├── contract-review-workflow.md    # 7-step process definition
    ├── delegation-model.md            # Subagent delegation patterns
    ├── work-product-standards.md      # Output format specs
    └── knowledge/                     # NEW: domain knowledge layer
        ├── re-concepts.md             # RE concepts: PSA, leases, financing
        ├── re-checklist-psa.md        # PSA review checklist (what to look for)
        ├── re-checklist-lease.md      # Commercial lease review checklist
        ├── market-standards.md        # What is "market" for each provision type
        ├── clause-library/            # Model language for key provisions
        │   ├── indemnification.md
        │   ├── representations.md
        │   ├── termination.md
        │   └── dispute-resolution.md
        └── user-materials/            # User-provided reference library (RAG source)

agents/
├── legal-researcher.md
├── document-reviewer.md
├── contract-reviser.md
└── document-drafter.md

docx-tools/
├── core/                  # Python document processing (working, adequate)
├── mcp_server.py
└── cli/
```

### Structure Rationale

- **knowledge/**: The core gap between current Sara and a competent associate. An associate doing a PSA review has internalized years of practice-area knowledge — what's market, what's dangerous, what to propose. This must be accessible to Sara without requiring it to fit in a single context window. Structured markdown files are the right medium: they can be referenced, read, and selectively loaded.
- **knowledge/clause-library/**: Model language removes the hardest part of redlining — knowing what to propose, not just what to object to. Sara currently spots risks but struggles to draft realistic alternatives. Clause libraries solve this.
- **user-materials/**: The user (a practicing RE attorney) has practice-specific materials (forms, firm playbooks, deal experience) that should inform Sara's work. This is the RAG source directory.
- **agents/**: Four subagents are the right number. `contract-reviser` is the most recently added and most important for depth — it is the mechanism by which Sara gets hundreds of paragraph-level revisions without context overflow.

---

## Architectural Patterns

### Pattern 1: Multi-Pass Document Analysis (The Core Pattern)

**What:** Sara does not attempt to analyze an entire contract in a single pass. The 7-step workflow in `contract-review-workflow.md` enforces multiple distinct passes over the document, each with a specific objective. Each pass produces a structured artifact that feeds the next.

**When to use:** Always, for any contract review. The passes are:
1. Intake (framing) — produces `intake-notes.md`
2. Initial read (orientation) — produces `initial-read.md`
3. Research + framework building — produces `analysis-framework.md`
4. Concept extraction — produces `concept-map.md`
5. Risk mapping — produces `risk-map.md`
6. Batched revision — produces `batch-N-revisions.md` files → `redline.docx`
7. Transmittal package — produces `transmittal-memo.md` + `open-items.md`

**Trade-offs:** Slower than a single-pass approach. Far more thorough. Each intermediate artifact is also a deliverable in its own right (the risk map has partner value even before the redline is prepared). The separation of "what the deal says" (concept map) from "what could go wrong" (risk map) is borrowed from how senior associates actually think — it prevents conflating description with analysis.

**Example structure for a pass:**
```markdown
## Sara's Analysis Pass

### Pass: Risk Mapping
Input: concept-map.md + analysis-framework.md + full document text
Output: risk-map.md

For each paragraph (paragraph ID from read_docx):
  - If paragraph has identified risk → create risk entry
  - Record: section ref, risk type, severity, title, description,
            problematic text (exact quote), recommendation
  - Cross-reference: mitigated_by, amplified_by, triggers
  - At aggressiveness 4-5: EVERY paragraph gets a disposition
```

**Confidence:** HIGH. This pattern is validated by the existing `contract-review-workflow.md` and aligns with Anthropic's research on multi-agent analysis showing 90%+ improvement over single-pass approaches.

---

### Pattern 2: Context-Isolated Subagent Delegation (The Depth Pattern)

**What:** Long documents exceed what any single context window can analyze deeply. The solution is to dispatch subagents with precisely scoped work packages — enough context to do the job, not the entire document.

**When to use:** Any time a task would require reading and analyzing the full document in one pass. Specifically:
- Concept extraction (Step 4): `document-reviewer` gets the full document + target concept list
- Risk mapping (Step 5): `document-reviewer` gets sections + risk framework + concept map
- Batched revision (Step 6): `contract-reviser` gets 10-20 paragraphs + filtered risk map entries + concept map + defined terms + document outline

**The critical insight from Anthropic's multi-agent research:** "Subagents maintain separate context from the main agent, preventing information overload and keeping interactions focused. A research-assistant subagent can explore dozens of files and documentation pages without cluttering the main conversation with all the intermediate search results, returning only the relevant findings."

For contract review, this means: the `contract-reviser` processing paragraphs 45-60 of a 200-paragraph document does not need paragraphs 1-44 or 61-200 in its context. It needs: (a) the 15 paragraphs in its batch, (b) the risk map entries for those paragraphs, (c) the full concept map for cross-reference, (d) the document outline for section numbering, and (e) the defined terms list. This is a far smaller and more focused context than the full document.

**Trade-offs:** Sequential batching (required for conforming change tracking) is slower than parallel. The benefit is that each batch gets the model's full attention on a bounded problem, rather than the model skimming a 170-paragraph document and missing most of it.

**Example delegation package for contract-reviser:**
```markdown
Batch 3 of 7 — Representations and Warranties (pp. 45-62)

PARAGRAPHS IN BATCH:
[p_45 through p_62, full text from read_docx]

RISK MAP ENTRIES FOR THIS BATCH:
- p_47: HIGH — Unlimited seller rep on environmental [...]
- p_51: MEDIUM — No knowledge qualifier on title rep [...]
- p_58: HIGH — Survival period is 6 months (should be 18-24 months) [...]

FULL CONCEPT MAP: [entire concept-map.md]
DOCUMENT OUTLINE: [article/section headings with paragraph IDs]
DEFINED TERMS: [full list from extract_structure]
CLIENT: Buyer | AGGRESSIVENESS: 4

Save output to: Sara-Work-Product/[matter]/junior-work/reviser/batch-3-revisions.md
```

**Confidence:** HIGH. Pattern validated by official Claude Code subagent documentation and Anthropic engineering blog.

---

### Pattern 3: Playbook-Driven Analysis Framework (The Knowledge Pattern)

**What:** The industry standard for commercial AI contract review (Spellbook, Luminance, Ivo, Gavel) is playbook-driven analysis: a structured list of checks the tool makes on every document. Sara should emulate this by maintaining a domain-specific knowledge layer that defines what to look for, what is market, and what to propose.

**When to use:** Step 3 of the contract review workflow (Research Phase — Build the Analysis Framework). Instead of relying solely on LLM general knowledge or requiring full web research on every review, Sara loads practice-area-specific reference files from the knowledge layer.

**Implementation:** The knowledge layer lives in `skills/sara/references/knowledge/` as markdown files:

- `re-checklist-psa.md` — Every provision a buyer's or seller's counsel should examine in a PSA, with what to look for and what is market
- `re-checklist-lease.md` — Same for commercial leases
- `market-standards.md` — What terms are "market" in 2025-2026 for different RE transaction types (DD period length, deposit percentages, rep survival periods, liability caps, etc.)
- `clause-library/` — Model language that Sara can adapt as the basis for proposed changes

**Trade-offs:** Requires upfront investment in building the knowledge files (this is the work of the improvement milestone). Once built, dramatically reduces the research burden per review and ensures Sara doesn't miss document-type-specific issues.

**Confidence:** MEDIUM. Playbook architecture is validated by commercial legal AI tools (HIGH confidence on the pattern). The specific markdown file implementation is a reasonable adaptation for the Claude Code plugin context (MEDIUM — untested but well-reasoned).

---

### Pattern 4: Structured Intermediate Artifacts as State (The Continuity Pattern)

**What:** Because Claude Code sessions can end and restart, and because long reviews span many agent turns, Sara must externalize all analytical state to the filesystem as structured markdown files. The work product directory is not just a place to save deliverables — it is the memory of the matter.

**When to use:** Always. Every significant analytical step produces a file. The pattern is:
- Before each step, read the relevant prior artifacts (intake-notes.md before initial-read, analysis-framework.md before risk mapping, etc.)
- After each step, write the artifact before proceeding
- The `prompt-log.md` provides the audit trail linking all artifacts to decisions

**Why this matters for depth:** When Sara can read her own prior analysis from structured files, she can build on it. When she cannot, each step starts from scratch. The concept map in `analysis-framework.md` is not just documentation — it is Sara's mental model of the deal that she consults when evaluating each clause.

**Example:**
```markdown
# Before starting risk mapping, Sara reads:
1. analysis/intake-notes.md (client, deal context, aggressiveness)
2. analysis/initial-read.md (first-pass observations, defined terms)
3. analysis/analysis-framework.md (target concept and risk categories)
4. analysis/concept-map.md (what the deal says)
# Then she proceeds paragraph by paragraph, informed by all prior analysis
```

**Confidence:** HIGH. File-based state persistence is validated by official Claude Code documentation and is already implemented in the existing architecture.

---

### Pattern 5: Sara-Reviews-Junior-Work Quality Gate (The Quality Pattern)

**What:** No junior associate output becomes part of the deliverable without Sara's explicit review. The model is not "delegate and trust" — it is "delegate, review, escalate or incorporate." The prompt-log records whether Sara reviewed each delegation and what judgment she applied.

**When to use:** After every subagent invocation. Sara reads the output and evaluates:
- Does it address what was asked?
- Are the findings accurate?
- Is the proposed language realistic and legally sound?
- Are there "FLAG FOR SARA" items that need her judgment?
- Are conforming changes correctly identified?

**Trade-offs:** Slower than direct pipeline. The quality gate is what separates partner-ready work from drafts. Given that the user evaluates Sara's output against Big Law associate standards, cutting this step would be counterproductive.

**Confidence:** HIGH. Quality control pattern is embedded in existing `SKILL.md` and delegation-model.md. Validated against stated project requirement that work product be "thorough enough that a partner would approve it with light review."

---

## Data Flow

### Contract Review Request Flow

```
Partner assignment (e.g., "Review this PSA for the buyer")
    │
    ▼
[Sara: Intake] ──────────────────────────────────────────────────────►
  Establish: representation, doc type, practice area, aggressiveness    │
  Save: analysis/intake-notes.md                                        │
                                                                        │
    ▼                                                                   │
[Sara: Initial Read] ─────────────────────────────────────────────────►
  read_docx → structured text with paragraph IDs                       │
  extract_structure → document skeleton, defined terms                  │
  Save: analysis/initial-read.md                                        │
                                                                        │
    ▼                                                                   │
[legal-researcher subagent] ──────────────────────────────────────────►
  Input: research questions, jurisdiction, matter dir                   │
  Output: key issues for this doc type from this representation         │
  Save: junior-work/researcher/research-[topic].md                      │
    │                                                                   │
    ▼                                                                   │
[Sara: Build Analysis Framework] ─────────────────────────────────────►
  Synthesize: initial read + research findings                          │
  Produce: target concept categories + target risk categories           │
  Save: analysis/analysis-framework.md                                  │
  Present to partner briefly before proceeding                          │
                                                                        │
    ▼                                                                   │
[document-reviewer subagent] ─────────────────────────────────────────►
  Input: full document + analysis-framework (target lists)              │
  Output: draft concept map + draft risk map                            │
  Save: junior-work/reviewer/concept-map-draft.md + risk-map-draft.md  │
    │                                                                   │
    ▼                                                                   │
[Sara: Review and Finalize Maps] ─────────────────────────────────────►
  Elevate junior drafts with senior judgment                            │
  Add risk relationships (mitigated_by, amplified_by, triggers)         │
  Apply aggressiveness calibration to severity levels                   │
  Save: analysis/concept-map.md + analysis/risk-map.md                 │
                                                                        │
    ▼                                                                   │
[contract-reviser subagent × N batches] ──────────────────────────────►
  SEQUENTIAL (not parallel) — conforming change tracking requires it    │
  Each batch input:                                                     │
    - 10-20 paragraphs with IDs + text                                 │
    - Filtered risk map entries for this batch                          │
    - Full concept map                                                  │
    - Document outline + defined terms                                  │
    - Client representation + aggressiveness                            │
  Each batch output:                                                    │
    - Per-paragraph: REVISED / NO CHANGE / FLAG FOR SARA               │
    - Full replacement text for each revision                           │
    - Conforming changes flagged                                        │
  Sara reviews between each batch                                       │
  Save: junior-work/reviser/batch-N-revisions.md                        │
                                                                        │
    ▼                                                                   │
[Sara: Compile Revision Set] ─────────────────────────────────────────►
  Resolve FLAG FOR SARA items                                           │
  Resolve cross-batch conforming changes                                │
  Check consistency across all batches                                  │
  Compile revision JSON: {"p_N": {"action": "revise", ...}, ...}        │
                                                                        │
    ▼                                                                   │
[redline_docx tool] ──────────────────────────────────────────────────►
  Input: original .docx + compiled revision JSON                        │
  Output: .docx with native Word track changes + comment bubbles        │
  Save: final/redline-[document-name].docx                              │
                                                                        │
    ▼                                                                   │
[document-drafter subagent] ──────────────────────────────────────────►
  Input: Sara's outline + risk map + concept map                        │
  Output: transmittal memo draft + open items list draft                │
  Save: junior-work/drafter/transmittal-draft.md + open-items-draft.md │
    │                                                                   │
    ▼                                                                   │
[Sara: Finalize and Present] ─────────────────────────────────────────►
  Review transmittal + open items                                       │
  Save: final/transmittal-memo.md + final/open-items.md                │
  Present transmittal package to partner                                │◄─
```

### Key Data Flows

1. **Paragraph IDs as coordination keys:** `read_docx` assigns `p_1`, `p_2`, etc. These IDs flow through every artifact — concept map references `p_N`, risk map entries cite `p_N`, contract-reviser batches are keyed by `p_N`, revision JSON uses `p_N` as keys. This is the spine of the entire system.

2. **Risk map as shared context:** The risk map is the central artifact of a review. It flows into the concept extraction (cross-checking), into every contract-reviser batch (driving revision decisions), and into the transmittal memo (framing the narrative). Every subagent that works on the document post-Step-5 receives a copy of the relevant risk map entries.

3. **Context passed to subagents (not held by Sara):** Sara does not hold the full document in her own context during revision. She reads the risk map and concept map, builds batches, and passes the necessary context to each `contract-reviser` invocation. This is how the system handles documents that exceed a single context window.

4. **Filesystem as working memory:** The directory tree is not just output storage — it is Sara's working memory. When Sara needs to recall something from earlier in the review, she reads the relevant file rather than relying on conversation history.

---

## Scaling Considerations

This is a single-user plugin, so "scale" means analytical depth, not user concurrency.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Simple document (< 30 paragraphs, NDA, short amendment) | 1-2 passes, minimal subagent delegation, Sara handles most analysis directly |
| Medium document (30-80 paragraphs, standard PSA, commercial lease) | Full 7-step workflow, 3-5 contract-reviser batches, one legal-researcher delegation |
| Complex document (80+ paragraphs, development agreement, credit agreement, APA) | Full 7-step workflow, 5-10 contract-reviser batches, multiple researcher delegations, multiple reviewer delegations per section group |
| Multi-document matter (closing package, due diligence set) | Parallel document-reviewer delegations, consolidated risk map across documents, single transmittal covering all documents |

### Scaling Priorities

1. **First bottleneck: Sara's context window.** A 170-paragraph PSA plus accumulated analysis exceeds what Sara can hold and still reason deeply. The batched contract-reviser pattern is the direct solution. Sara holds the risk map and concept map (compact artifacts), not the full document text.

2. **Second bottleneck: Knowledge freshness.** Sara's embedded legal knowledge is 6-18 months stale. This hits for market standards (what is "market" for a 2026 PSA?), recent case law, and regulatory changes. The solution is the knowledge layer (reference files Sara reads) plus legal-researcher delegation for time-sensitive questions.

3. **Third bottleneck: Instruction quality for subagents.** "Most sub-agent failures aren't execution failures — they're invocation failures." (claudefa.st, 2025). Contract-reviser output quality is entirely dependent on how precisely Sara packages the batch: paragraph IDs, full text, filtered risk entries, concept map, document outline, defined terms. Vague invocations produce vague revisions.

---

## Anti-Patterns

### Anti-Pattern 1: Single-Pass Full-Document Review

**What people do:** Ask Sara to "review this contract" and let her read it once and produce output in one pass.
**Why it's wrong:** A 170-paragraph PSA cannot be reviewed with the depth a senior associate would apply in one LLM pass. The model will skim, miss cross-references, and produce surface-level findings. This is exactly the problem ("19 of 170 paragraphs is not enough").
**Do this instead:** Enforce the multi-pass workflow. Sara reads once (orientation), builds frameworks, delegates systematically. The 7-step workflow exists precisely to prevent this.

### Anti-Pattern 2: Delegating Without Packed Context

**What people do:** Sara delegates to `contract-reviser` with only the paragraph text and a generic instruction like "revise these sections for the buyer."
**Why it's wrong:** The reviser has no idea what risks were identified, what the client's position is, what defined terms exist, or how these paragraphs relate to the rest of the document. Output will be generic and legally naive.
**Do this instead:** Each contract-reviser invocation must include the filtered risk map, concept map, document outline, defined terms, and aggressiveness level. The delegation package should be long — the reviser's output quality is proportional to the richness of context it receives.

### Anti-Pattern 3: Parallel Contract-Reviser Batches

**What people do:** Dispatch all contract-reviser batches simultaneously for speed.
**Why it's wrong:** Batch 2 may identify a conforming change in a provision that Batch 4 also touches. If batches run in parallel, both will revise that provision independently and inconsistently. Cross-document consistency cannot be maintained with parallel batches.
**Do this instead:** Dispatch batches sequentially. Sara reviews each batch's output — including conforming change flags — before dispatching the next batch, and updates the context passed to subsequent batches with any conforming changes already committed.

### Anti-Pattern 4: Raw Junior Output to Partner

**What people do:** Pass document-reviewer or contract-reviser output directly to the partner without Sara's review layer.
**Why it's wrong:** Junior associates miss materiality judgment, may flag non-issues, may miss cross-reference consequences, and do not know what the partner needs to decide vs. what has already been decided. Sara's review layer is what makes the output partner-ready.
**Do this instead:** Sara reads all junior output critically. She incorporates findings selectively, adds judgment about materiality, resolves FLAG FOR SARA items, and makes the final call on what goes into deliverables.

### Anti-Pattern 5: Naked Redline Delivery

**What people do:** Produce the redline .docx and present it directly to the partner.
**Why it's wrong:** A redline without a transmittal memo forces the partner to read every tracked change to understand the negotiation strategy. A redline without an open items list fails to capture business decisions needed from the client. "Never send a naked redline" is a Big Law principle for good reason.
**Do this instead:** Always deliver the full transmittal package: redline .docx + transmittal memo + open items list.

### Anti-Pattern 6: Generic Knowledge, No Domain Specialization

**What people do:** Rely entirely on the LLM's embedded legal knowledge for market standards, provision analysis, and proposed language.
**Why it's wrong:** The LLM's legal knowledge is stale (6-18 months behind) and not specialized to the user's practice area. "What is market for a 2026 PSA in [jurisdiction]?" requires current, practice-specific knowledge that cannot come from training data.
**Do this instead:** Build and maintain the knowledge layer (reference files) with practice-area-specific checklists, market standards, and clause libraries. Sara reads these files as part of Step 3 (framework building) and references them when proposing alternative language.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Claude Code plugin system | SKILL.md + command definition | Standard plugin architecture — no custom code required |
| MCP Server (docx-tools) | FastMCP stdio transport | Configured in `.claude-plugin/plugin.json` |
| CourtListener API | WebSearch/WebFetch tools via legal-researcher | Free API key required; legal-researcher uses directly |
| User-provided documents | Local filesystem via read_docx | Partner places .docx files in working directory |
| User-provided reference library | Local filesystem — knowledge/ directory | Sara reads files; future: vector search for larger libraries |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Sara → subagents | Task tool invocation with packed text prompt | Context passed in the Task prompt itself — no shared memory |
| Subagents → filesystem | Write tool — structured markdown to designated paths | Sara instructs each subagent where to save output |
| Sara → filesystem | Read/Write tools — structured markdown artifacts | Intermediate artifacts are Sara's working memory |
| Sara → docx tools | MCP tool calls (preferred) or Bash CLI invocation | Mode configured in `.claude/ai-associate.local.md` |
| Sara → knowledge layer | Read tool — reference files loaded on demand | Sara reads relevant reference files during Step 3 |
| Revision JSON → redline_docx | JSON structure `{"p_N": {action, original, revised, comment}}` | Paragraph IDs from read_docx must match exactly |

---

## Component Dependency Graph

Build order implications — each layer depends on the one above being correct:

```
Level 0 (Foundation — already built, working):
  docx-tools core (reader, writer, redliner, extractor, analyzer, comparer)
    ↓
Level 1 (Tool Exposure — already built, working):
  MCP server + CLI scripts exposing docx-tools to Sara
    ↓
Level 2 (Subagent Definitions — built, need refinement):
  legal-researcher, document-reviewer, contract-reviser, document-drafter
    ↓
Level 3 (Knowledge Layer — NOT YET BUILT, critical gap):
  RE-specific checklists, market standards, clause libraries
  User-provided reference library integration
    ↓
Level 4 (Orchestrator Behavior — partially built, needs major work):
  Sara SKILL.md — multi-pass enforcement, delegation precision,
  quality gates, context management, depth calibration
    ↓
Level 5 (Reference Workflow — built, adequate):
  contract-review-workflow.md as explicit process Sara follows
```

**Build order for improvement work:**
1. Improve subagent prompts (Level 2) — sharpen delegation precision and output format enforcement
2. Build knowledge layer (Level 3) — RE checklists, market standards, clause libraries
3. Improve Sara's orchestration logic (Level 4) — multi-pass enforcement, context packing for delegation, quality gate articulation
4. Integrate user-provided reference library into Sara's Step 3 workflow

The docx tooling (Levels 0-1) is sound and does not need improvement for this milestone.

---

## Sources

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — HIGH confidence, official source. Orchestrator-worker pattern, parallel subagent architecture, prompting principles for thorough analysis.
- [Claude Code: Create custom subagents documentation](https://code.claude.com/docs/en/sub-agents) — HIGH confidence, official source. Subagent configuration, context isolation, skills injection, delegation patterns.
- [Claude Agent SDK: Subagents documentation](https://platform.claude.com/docs/en/agent-sdk/subagents) — HIGH confidence, official source. AgentDefinition configuration, context management, tool restrictions.
- [claudefa.st: Claude Code Sub-Agents Parallel vs Sequential Patterns](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) — MEDIUM confidence, third-party but consistent with official docs. "Most sub-agent failures aren't execution failures — they're invocation failures." Context density in invocations.
- [Spellbook: Legal Contract Playbook architecture](https://www.spellbook.legal/learn/contract-playbook) — MEDIUM confidence, commercial legal AI product. Playbook-driven analysis as industry standard pattern.
- [Gavel: Redlining with AI playbooks](https://www.gavel.io/resources/redlining-with-ai-the-new-playbook-for-contract-review) — MEDIUM confidence, commercial legal AI product. RAG + playbook combination for contract review.
- Existing project code — HIGH confidence, direct analysis. `skills/sara/SKILL.md`, `references/contract-review-workflow.md`, `agents/`, `docx-tools/`, `.planning/codebase/ARCHITECTURE.md`.

---

*Architecture research for: AI legal assistant plugin — deep contract analysis*
*Researched: 2026-02-17*
