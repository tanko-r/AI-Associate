# Phase 2: Knowledge Layer - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Build RE-specific stub files (PSA review checklist, clause library, market standards) with correct structure and detailed sub-items that Sara loads during Step 3 (framework building). The user populates risk notes and market references over time; Sara uses whatever content is present and falls back to LLM knowledge for placeholders.

Source material: 3 sample documents in `.sample-docs/` — a pro-buyer PSA (IL), a pro-seller PSA (detailed .docx), and a PSA Negotiation Checklist (NY) — merged exhaustively into the checklist structure.

</domain>

<decisions>
## Implementation Decisions

### Checklist Categories & Structure
- **24 provision categories** derived from merging all 3 sample documents exhaustively (every distinct concept across all docs goes in)
- Categories ordered by **typical PSA article order** (familiar to any RE attorney), not grouped by deal phase
- Full category list: Definitions & Key Defined Terms, Property Description & Conveyance, Purchase Price & Deposit Mechanics, Due Diligence / Investigation Period, Title & Survey, Representations & Warranties, Seller's Pre-Closing Covenants, Conditions Precedent to Closing, Closing Mechanics, Closing Deliveries, Costs Prorations & Adjustments, Casualty & Condemnation, Default & Remedies, AS-IS / Disclaimers & Waivers, Indemnification, Assignment & Transfer Rights, Tenant Estoppels & SNDAs, Escrow Provisions, Brokerage & Commissions, Confidentiality & Press Releases, Tax Proceedings, Assumption of Contracts, Mortgage Assignment, Miscellaneous / General Provisions
- Each category has **comprehensive sub-items** — not just headers but the full rotation of specific concepts (e.g., under Reps & Warranties: each typical rep, knowledge qualifiers, survival periods, anti-sandbagging, bring-down certificates)
- Sub-items framed as **imperative review points** ("Check whether...", "Verify that...")
- **Representation-adaptive** — checklist structured so Sara can read from either buyer or seller perspective depending on who she represents
- Each category ends with a **Key Risks** section listing specific risks Sara should flag for that category
- Sub-items include **cross-references to market-standards.md** for market data (format for memorializing market standards to be determined later — see GitHub issue #1)

### Placeholder Design
- **Hybrid approach**: Pre-populate structure and item labels from the 3 sample docs; leave risk notes and market references as `[TODO: description]` placeholders
- Placeholder format: `[TODO: description of what to fill in]` — standard, searchable, easy to find
- When Sara encounters a `[TODO]` placeholder during review, she uses **LLM knowledge as fallback** but **explicitly states** she is doing so (e.g., "Using general knowledge — no firm-specific reference data for this item")

### Graceful Degradation
- Sara **always loads all 3 reference files** (checklist, clause library, market standards) regardless of population level
- Sara **always reports file status** — shows coverage report during Step 3 (e.g., "Loaded PSA checklist: 14/24 categories populated, 10 categories using LLM fallback") **[MVP — remove once files fully populated]**
- Sara **marks LLM-sourced items** with a `†` marker in disposition table and transmittal memo so partner knows which items came from the checklist vs Sara's own knowledge **[MVP — remove once files fully populated]**
- Sara's review output includes a **missing provisions report** after the disposition table — lists checklist items the PSA doesn't address at all (permanent feature — helps identify gaps in the contract)

### MVP Features (Track for Removal)
These features exist because reference files will be partially populated at first. Remove or revise once files are mature:
1. **LLM fallback behavior** — Sara uses own knowledge when `[TODO]` placeholders exist; replace with "no reference data" once coverage is high
2. **Coverage report in Step 3** — Reports populated vs placeholder counts; becomes noise once files are fully populated
3. **`†` LLM-sourced markers** — Distinguishes checklist-backed vs LLM-backed review points; unnecessary once all items are checklist-backed

</decisions>

<specifics>
## Specific Ideas

- Source the sub-items by exhaustively merging all 3 sample documents — buyer PSA (21 articles, 90+ sections), seller PSA (63 sections), and the NY Negotiation Checklist (20 categories with practitioner-framed sub-items)
- The NY Negotiation Checklist is especially valuable as it's already framed as practitioner guidance (not raw contract language)
- GitHub issue #1 tracks ongoing refinement of checklists, market standards, and clause library content beyond what Phase 2 delivers
- Market standards format to be determined separately — for now, checklist items cross-reference market-standards.md with section markers

</specifics>

<deferred>
## Deferred Ideas

- Format for memorializing market standards in market-standards.md — tracked in GitHub issue #1
- Jurisdiction-specific checklist variations (NY vs IL vs other markets)
- Clause library population with model language from negotiated deals

</deferred>

---

*Phase: 02-knowledge-layer*
*Context gathered: 2026-02-18*
