# Phase 2: Knowledge Layer - Research

**Researched:** 2026-02-18
**Domain:** Structured reference file design for LLM-driven legal document review -- markdown checklist architecture, placeholder patterns, graceful degradation, and Sara integration points
**Confidence:** HIGH

## Summary

Phase 2 creates three markdown reference files that Sara loads during Step 3 (framework building) of the contract review workflow: `re-checklist-psa.md` (24-category PSA review checklist), `clause-library.md` (model language stubs), and `market-standards.md` (market data stubs). The files are structured from an exhaustive merge of three source documents -- a pro-buyer PSA (IL, 21 articles, 90+ sections), a pro-seller PSA (detailed .docx, 531 paragraphs, 63 sections, 86 defined terms), and a NY PSA Negotiation Checklist (20 categories of practitioner-framed guidance). The implementation is entirely markdown file creation plus behavioral changes to Sara's SKILL.md and contract-review-workflow.md to wire in the new files. No new Python code, no new tools, no infrastructure changes.

The primary challenge is structural: designing a checklist format that (1) is parseable by Sara during Step 3 to generate target concept and risk lists, (2) works from either buyer or seller perspective, (3) degrades gracefully when items contain `[TODO]` placeholders, and (4) is maintainable by the user as a living document. The three sample documents provide comprehensive coverage of PSA provisions -- the NY Checklist alone has 20 categories with dozens of practitioner-framed sub-items, and the two PSAs together cover every standard provision category plus specialized topics (tax proceedings, mortgage assignment, 1031 exchange cooperation).

**Primary recommendation:** Create the three stub files with the locked 24-category structure, wire them into Sara's Step 3 workflow with explicit load-and-report logic, and implement the three MVP degradation features (coverage report, LLM fallback with explicit disclosure, `+` marker). Design the checklist format as a structured markdown document with consistent heading hierarchy and machine-parseable sub-item format that Sara can read section-by-section.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Checklist Categories & Structure
- **24 provision categories** derived from merging all 3 sample documents exhaustively (every distinct concept across all docs goes in)
- Categories ordered by **typical PSA article order** (familiar to any RE attorney), not grouped by deal phase
- Full category list: Definitions & Key Defined Terms, Property Description & Conveyance, Purchase Price & Deposit Mechanics, Due Diligence / Investigation Period, Title & Survey, Representations & Warranties, Seller's Pre-Closing Covenants, Conditions Precedent to Closing, Closing Mechanics, Closing Deliveries, Costs Prorations & Adjustments, Casualty & Condemnation, Default & Remedies, AS-IS / Disclaimers & Waivers, Indemnification, Assignment & Transfer Rights, Tenant Estoppels & SNDAs, Escrow Provisions, Brokerage & Commissions, Confidentiality & Press Releases, Tax Proceedings, Assumption of Contracts, Mortgage Assignment, Miscellaneous / General Provisions
- Each category has **comprehensive sub-items** -- not just headers but the full rotation of specific concepts (e.g., under Reps & Warranties: each typical rep, knowledge qualifiers, survival periods, anti-sandbagging, bring-down certificates)
- Sub-items framed as **imperative review points** ("Check whether...", "Verify that...")
- **Representation-adaptive** -- checklist structured so Sara can read from either buyer or seller perspective depending on who she represents
- Each category ends with a **Key Risks** section listing specific risks Sara should flag for that category
- Sub-items include **cross-references to market-standards.md** for market data (format for memorializing market standards to be determined later -- see GitHub issue #1)

#### Placeholder Design
- **Hybrid approach**: Pre-populate structure and item labels from the 3 sample docs; leave risk notes and market references as `[TODO: description]` placeholders
- Placeholder format: `[TODO: description of what to fill in]` -- standard, searchable, easy to find
- When Sara encounters a `[TODO]` placeholder during review, she uses **LLM knowledge as fallback** but **explicitly states** she is doing so (e.g., "Using general knowledge -- no firm-specific reference data for this item")

#### Graceful Degradation
- Sara **always loads all 3 reference files** (checklist, clause library, market standards) regardless of population level
- Sara **always reports file status** -- shows coverage report during Step 3 (e.g., "Loaded PSA checklist: 14/24 categories populated, 10 categories using LLM fallback") **[MVP -- remove once files fully populated]**
- Sara **marks LLM-sourced items** with a `+` marker in disposition table and transmittal memo so partner knows which items came from the checklist vs Sara's own knowledge **[MVP -- remove once files fully populated]**
- Sara's review output includes a **missing provisions report** after the disposition table -- lists checklist items the PSA doesn't address at all (permanent feature -- helps identify gaps in the contract)

#### MVP Features (Track for Removal)
These features exist because reference files will be partially populated at first. Remove or revise once files are mature:
1. **LLM fallback behavior** -- Sara uses own knowledge when `[TODO]` placeholders exist; replace with "no reference data" once coverage is high
2. **Coverage report in Step 3** -- Reports populated vs placeholder counts; becomes noise once files are fully populated
3. **`+` LLM-sourced markers** -- Distinguishes checklist-backed vs LLM-backed review points; unnecessary once all items are checklist-backed

### Claude's Discretion

No items explicitly designated as Claude's discretion in the CONTEXT.md. Research identified the following areas where the planner has design freedom:

1. **Exact markdown format of checklist sub-items** -- the structure (imperative review points with Key Risks sections) is locked, but the exact markdown syntax (heading levels, bullet nesting, metadata fields per item) is implementation detail
2. **How Sara parses the checklist files** -- the behavior (load, count populated vs TODO, report) is locked, but the parsing strategy (read entire file vs section-by-section, regex for `[TODO]` counting) is implementation detail
3. **Clause library and market standards internal structure** -- the user locked the checklist format but the clause library and market standards are stubs with "section headers and placeholder structure" -- the internal format is less constrained
4. **Integration point in SKILL.md** -- where exactly the reference file loading instruction goes and how it interacts with the existing Step 3 workflow

### Deferred Ideas (OUT OF SCOPE)

- Format for memorializing market standards in market-standards.md -- tracked in GitHub issue #1
- Jurisdiction-specific checklist variations (NY vs IL vs other markets)
- Clause library population with model language from negotiated deals
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| KNOW-01 | RE-specific PSA review checklist stub that Sara loads during framework building (Step 3) -- structured skeleton with correct sections, per-category target risk lists, and placeholders for the user to fill in; covers DD period, title cure, deposit mechanics, representations, indemnification, default remedies, closing conditions, AS-IS provisions | Exhaustive analysis of all 3 sample documents provides category structure and sub-items; checklist format designed with heading hierarchy, imperative review points, and Key Risks sections; integration point identified in Step 3c of contract-review-workflow.md; graceful degradation behavior specified |
| KNOW-02 | Clause library stub and market-standards stub with correct structure, section headers, and placeholders for model language -- files ship as templates the user completes, not fully authored reference material | Clause library organized by the same 24 PSA categories for cross-reference consistency; market-standards stub uses matching section headers with `[TODO]` placeholders for market data; both stubs include user instructions; market standards format deferred per GitHub issue #1 |
</phase_requirements>

## Standard Stack

This phase is entirely markdown file creation and behavioral prompt updates. No new libraries, no new Python code, no new infrastructure.

### Core (Files Being Created)

| File | Location | Purpose | Estimated Size |
|------|----------|---------|----------------|
| `re-checklist-psa.md` | `skills/sara/references/` | PSA review checklist with 24 categories, comprehensive sub-items, Key Risks sections, `[TODO]` placeholders | 800-1200 lines |
| `clause-library.md` | `skills/sara/references/` | Clause library stub with 24 matching category headers, placeholder entries for model language | 200-400 lines |
| `market-standards.md` | `skills/sara/references/` | Market standards stub with 24 matching category headers, placeholder entries for market data | 200-400 lines |

### Files Being Modified

| File | Location | What Changes |
|------|----------|--------------|
| `skills/sara/SKILL.md` | Section: Additional Resources | Add reference to 3 new files; add graceful degradation behavior instructions (coverage report, LLM fallback disclosure, `+` marker, missing provisions report) |
| `skills/sara/references/contract-review-workflow.md` | Step 3 (Research Phase) | Add Step 3a-pre: "Load reference files" before research; modify Step 3c to merge checklist items with research-derived target lists; add coverage report to Step 3d presentation |
| `agents/document-reviewer.md` | Output format section | Add `+` marker convention for LLM-sourced items in Section A disposition table |
| `agents/document-drafter.md` | Transmittal section | Add `+` marker convention for LLM-sourced items in transmittal memo |

### No Libraries Required

This phase has zero library dependencies. All files are markdown. The only tooling involved is Sara's existing Read tool to load files during a review session.

## Architecture Patterns

### Recommended File Structure After Phase 2

```
skills/sara/
├── SKILL.md                           # MODIFIED: reference file loading, degradation behavior
└── references/
    ├── contract-review-workflow.md     # MODIFIED: Step 3 reference file integration
    ├── delegation-model.md            # UNCHANGED
    ├── work-product-standards.md      # UNCHANGED
    ├── re-checklist-psa.md            # NEW: 24-category PSA review checklist
    ├── clause-library.md              # NEW: model language stub
    └── market-standards.md            # NEW: market data stub

agents/
├── document-reviewer.md              # MODIFIED: + marker convention
├── document-drafter.md               # MODIFIED: + marker convention
├── contract-reviser.md               # UNCHANGED
└── legal-researcher.md               # UNCHANGED
```

### Pattern 1: Checklist Sub-Item Format

**What:** Each of the 24 categories in `re-checklist-psa.md` follows a consistent internal format that Sara can parse during Step 3.

**Design rationale:** Sara needs to read the checklist and extract two things: (1) target concept categories (what to extract from the document) and (2) target risk categories (what to watch for). The checklist format must make both extractions natural for an LLM reading markdown.

**Recommended format:**

```markdown
## 3. Purchase Price & Deposit Mechanics

### Review Points

- [ ] **Check deposit structure** -- Is the deposit soft (refundable) through the DD period, or does it go hard immediately? What triggers the deposit going hard?
  - See: market-standards.md > Purchase Price & Deposit Mechanics > Deposit Structure
  - [TODO: Add firm's standard position on deposit timing for institutional deals]

- [ ] **Verify deposit amount** -- Is the deposit amount market for this transaction size and type? Typical range is 3-10% of purchase price.
  - See: market-standards.md > Purchase Price & Deposit Mechanics > Deposit Amount

- [ ] **Check additional deposit requirements** -- Does the PSA require an additional deposit at the end of the DD period? What is the amount? What happens if the buyer fails to post the additional deposit?

- [ ] **Verify interest on deposit** -- Who receives interest earned on the deposit during the contract period? Does the buyer get a credit at closing?

- [ ] **Check purchase price adjustments** -- Are there any purchase price adjustment mechanisms (e.g., rent roll adjustments, working capital adjustments, prorations)?

- [ ] **Verify payment mechanics** -- How is the balance of the purchase price paid at closing? Wire transfer requirements? Same-day funds?

- [ ] **Check financing contingency** -- Does the buyer have a financing contingency? If so, what are the terms (commitment deadline, rate lock, walk-away right)?
  - [TODO: Add firm's standard position on financing contingencies in institutional vs non-institutional deals]

### Key Risks

| Risk | Buyer Perspective | Seller Perspective |
|------|-------------------|-------------------|
| Deposit goes hard immediately | High -- buyer loses exit flexibility; negotiate soft deposit through DD period | Favorable -- seller has leverage to keep buyer committed |
| No financing contingency | High if buyer needs financing -- negotiate contingency with reasonable commitment deadline | Favorable -- eliminates closing risk from buyer's financing failure |
| No additional deposit trigger | Medium -- buyer has lower at-risk amount throughout contract period | Unfavorable -- seller wants additional deposit to increase buyer's commitment after DD period |
| Interest on deposit to seller | Low -- small economic impact but principle matters | Standard in some markets |
| [TODO: Add additional risks from firm experience] | | |
```

**Key design principles:**
- Checkbox format (`- [ ]`) makes sub-items visually scannable and allows Sara to track which items she has addressed during a review
- Bold imperative framing ("Check deposit structure") is the review point label
- Descriptive text after the `--` provides context and what to look for
- `See:` cross-references point to market-standards.md
- `[TODO]` placeholders are inline where firm-specific content belongs
- Key Risks table has separate buyer/seller columns for representation-adaptive reading
- Sara reads the buyer column when representing the buyer, seller column when representing the seller

**Confidence:** HIGH. This is a structured format design. The format serves LLM reading (natural markdown), human editing (standard checklist), and machine parsing (consistent heading levels, `[TODO]` markers, checkbox syntax).

### Pattern 2: Representation-Adaptive Design

**What:** The checklist is structured so Sara can read it from either buyer or seller perspective without needing separate files.

**Implementation approach:** Each Key Risks table has separate Buyer Perspective and Seller Perspective columns. Each review point's descriptive text is framed neutrally ("Check deposit structure") rather than from one side ("Negotiate better deposit terms for buyer"). Sara reads the column matching her current representation.

**How Sara uses it during Step 3:**

1. Sara loads `re-checklist-psa.md`
2. Sara identifies current representation (buyer or seller) from Step 1 intake
3. For each category, Sara reads the review points (neutral) and the Key Risks column matching her representation
4. Sara synthesizes checklist items with her own research into the analysis framework target lists
5. During Step 5 (risk mapping), Sara uses the checklist's risk entries as a baseline and adds risks she identified independently

**Confidence:** HIGH. Dual-column risk tables are a standard legal reference pattern. No technical complexity.

### Pattern 3: Graceful Degradation with Coverage Reporting

**What:** Sara reports how populated the reference files are during Step 3, uses LLM fallback for `[TODO]` items, and marks LLM-sourced items with `+`.

**Implementation pattern for Step 3:**

```markdown
### Step 3-pre: Load Reference Files

Before beginning research, Sara loads the practice-area-specific reference files:

1. **Read checklist:** `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/re-checklist-psa.md`
2. **Read clause library:** `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/clause-library.md`
3. **Read market standards:** `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/market-standards.md`

**Coverage report [MVP]:** Count the number of categories with substantive content vs `[TODO]` placeholders. Report to partner:
> "Reference files loaded. PSA checklist: 14/24 categories have firm-specific content, 10 categories using general legal knowledge as fallback. Clause library: 3/24 categories populated. Market standards: 2/24 categories populated."

**Fallback behavior [MVP]:** For any checklist item containing a `[TODO]` placeholder, Sara uses her own legal knowledge but marks the resulting analysis with `+` in:
- The disposition table (Section A): append `+` to the Market Assessment field
- The transmittal memo: append `+` to any recommendation sourced from LLM knowledge rather than the checklist

**Missing provisions report [Permanent]:** After completing the disposition table, Sara generates a list of checklist items that the PSA does not address at all. This is a gap analysis -- provisions the checklist says should be present but are absent from the document.
```

**Confidence:** HIGH. This is behavioral specification. The `[TODO]` counting is trivial string matching. The `+` marker is a formatting convention.

### Pattern 4: Cross-Reference Consistency Across Three Files

**What:** All three files (checklist, clause library, market standards) use the same 24-category heading structure so cross-references work.

**Implementation:**

```markdown
# In re-checklist-psa.md:
## 6. Representations & Warranties
### Review Points
- [ ] **Check knowledge qualifier** -- ...
  - See: market-standards.md > Representations & Warranties > Knowledge Qualifiers
  - See: clause-library.md > Representations & Warranties > Knowledge Qualifier Language

# In market-standards.md:
## 6. Representations & Warranties
### Knowledge Qualifiers
[TODO: Document market standard for knowledge qualifiers in institutional PSAs]

# In clause-library.md:
## 6. Representations & Warranties
### Knowledge Qualifier Language
[TODO: Add model knowledge qualifier language from negotiated deals]
```

The numbering (1-24) and exact category names must be identical across all three files. This allows Sara to navigate between files by category number and name.

**Confidence:** HIGH. Consistent heading structure across related documents is a basic information architecture pattern.

### Anti-Patterns to Avoid

- **Over-authoring substantive content:** The user explicitly decided these are stubs with `[TODO]` placeholders. Do NOT write substantive legal analysis, risk descriptions, or market standard positions. The structure and labels come from the sample documents; the firm-specific content comes from the user over time.

- **Monolithic checklist file:** At 800-1200 lines, the checklist will be large. Sara should NOT attempt to read the entire file into context at once during a review. Instead, Sara should read the relevant categories for the document being reviewed. The contract-review-workflow.md integration should instruct Sara to load the checklist selectively based on the document's structure identified in Step 2.

- **Hard-coding category numbers:** If a category is added or removed later, hard-coded cross-references break. Use category names as the primary reference, with numbers as navigation aids.

- **Separate buyer/seller checklists:** The user decided on a single representation-adaptive checklist. Do not create separate buyer and seller versions.

- **Populating market standards content:** Market standards format is explicitly deferred (GitHub issue #1). The market-standards.md stub should have section headers and `[TODO]` placeholders only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Checklist category structure | Ad-hoc categories based on Sara's LLM knowledge | Exhaustive merge of all 3 sample documents | The whole point of Phase 2 is grounding Sara's review in structured reference material, not her own knowledge; the sample docs provide real-world category coverage |
| Market standards content | LLM-generated market positions | `[TODO]` placeholders for user to fill | User decision: no substantive legal content authored by this project; market standards come from practitioner experience |
| Clause library model language | LLM-drafted contract clauses | `[TODO]` placeholders for user to add from negotiated deals | Model language must come from actual negotiated transactions, not LLM generation |
| Coverage counting logic | Complex parsing or metadata system | Simple `[TODO]` string search during Sara's read pass | The `[TODO]` format was chosen specifically because it is searchable and countable without tooling |

**Key insight:** Phase 2 builds the filing cabinet, not the files. The structure, labels, and organization come from the sample documents. The substantive content comes from the user over time. Sara's job is to use whatever content is present and be transparent about what is missing.

## Common Pitfalls

### Pitfall 1: Checklist Becomes Too Long for Context Window

**What goes wrong:** The checklist file grows to 1200+ lines with comprehensive sub-items. Sara tries to load it all during Step 3 and it consumes significant context window before the actual document review begins.

**Why it happens:** The user wants "comprehensive sub-items" with "the full rotation of specific concepts." Each of 24 categories may have 15-30 sub-items plus a Key Risks table.

**How to avoid:** Design the Step 3 integration so Sara loads the checklist *selectively* -- read the full table of contents (category list), then read only the categories relevant to the document being reviewed. For a standard PSA, that might be 18-20 of 24 categories. For a simpler transaction, fewer. The workflow instruction should say: "Read the checklist category list first, then load the categories that match the document's structure from your Step 2 initial read." This is important because Sara also loads the full document, concept map, risk map, and delegation briefings -- context budget matters.

**Warning signs:** Sara's Step 3 output includes the phrase "I loaded the full checklist" and the session starts running into context limits during Step 5 paragraph review.

### Pitfall 2: Sub-Items Are Too Generic to Be Useful

**What goes wrong:** Checklist sub-items read like generic legal advice ("Review the indemnification provisions") rather than specific, actionable review points ("Check whether the indemnification cap applies to breaches of environmental representations or only general representations").

**Why it happens:** The temptation to write generic sub-items that apply to any PSA, rather than specific sub-items derived from what the three sample documents actually cover.

**How to avoid:** Source every sub-item from a specific provision or concept that appears in at least one of the three sample documents. The NY Checklist is especially valuable here because it is already framed as practitioner guidance. For example, under Title Review, the NY Checklist says "Include the right to object to any new title matter raised by the title company at any time before the closing" -- that is a specific, actionable review point. Use that level of specificity.

**Warning signs:** More than half of the sub-items in a category could apply to any contract type (lease, APA, merger agreement), not specifically to a PSA.

### Pitfall 3: Representation-Adaptive Structure Becomes Confusing

**What goes wrong:** The dual buyer/seller perspective makes the checklist hard to read. Sara reads the wrong column. The user cannot tell which perspective a sub-item is written from.

**Why it happens:** Trying to serve two audiences (buyer and seller) in one document creates ambiguity in framing.

**How to avoid:** Keep review points neutral ("Check whether the deposit goes hard immediately"). Put perspective-specific risk assessments ONLY in the Key Risks table's buyer/seller columns. Sara reads the review points (neutral) regardless of representation, then reads only her representation's risk column. The review points tell Sara *what to look for*; the risk columns tell her *how to assess it* from her client's perspective.

**Warning signs:** Review points contain phrases like "negotiate for the buyer" or "ensure the seller" -- those belong in the risk columns, not the review points.

### Pitfall 4: Missing Provisions Report Becomes Noise

**What goes wrong:** Sara reports 40 "missing" provisions on every PSA because the checklist is exhaustive and most PSAs do not address every conceivable topic (e.g., mortgage assignment is uncommon, tax proceedings are deal-specific).

**Why it happens:** The checklist has 24 categories with comprehensive sub-items. A typical PSA has 10-15 substantive articles. Many checklist items will not apply.

**How to avoid:** The missing provisions report should distinguish between (1) provisions that are commonly expected in a PSA of this type but absent (genuine gaps) and (2) provisions that are specialized and may not apply to every deal. The checklist should include a `[Common/Specialized]` tag on each category so Sara can filter the missing provisions report. For example, "Definitions & Key Defined Terms" is Common (always expected), while "Mortgage Assignment" is Specialized (only when applicable). Sara reports missing Common items as potential gaps and missing Specialized items only when the deal context suggests they should be present.

**Warning signs:** The missing provisions report is longer than the disposition table. The partner starts ignoring it because it is full of inapplicable items.

### Pitfall 5: Workflow Integration Creates a Rigid Gate

**What goes wrong:** Sara refuses to proceed with a review because she cannot load a reference file, or she blocks on the coverage report step even when the partner wants to move quickly.

**Why it happens:** Adding a "Load reference files" step to the workflow creates a new gate. If the files are missing, corrupted, or not yet created, Sara may halt.

**How to avoid:** The reference file loading should be a best-effort step, not a hard gate. If a file is not found, Sara proceeds without it and notes the absence. The coverage report is informational, not a decision point. Sara should present it as part of the Step 3d framework presentation and proceed unless the partner redirects. The contract-review-workflow.md update should say: "Load reference files if available. If a file is not found, proceed with LLM knowledge only and note the absence in the framework presentation."

**Warning signs:** Sara's Step 3 output includes "I cannot proceed because the clause library file is missing" when the partner just wants a review done.

## Code Examples

Since this phase is entirely markdown file creation, the "code examples" are file format examples.

### Example 1: Checklist Category Structure (re-checklist-psa.md)

```markdown
# RE PSA Review Checklist

> **Usage:** Sara loads this file during Step 3 (framework building) of a PSA review. Read the category list first, then load categories matching the document's structure.
>
> **Populating this file:** Replace `[TODO: ...]` placeholders with firm-specific content as deals are completed. Each placeholder describes what to add.
>
> **Representation:** Review points are neutral. Key Risks tables have separate buyer/seller columns -- read the column matching your representation.

## Categories

1. Definitions & Key Defined Terms
2. Property Description & Conveyance
3. Purchase Price & Deposit Mechanics
4. Due Diligence / Investigation Period
5. Title & Survey
6. Representations & Warranties
7. Seller's Pre-Closing Covenants
8. Conditions Precedent to Closing
9. Closing Mechanics
10. Closing Deliveries
11. Costs, Prorations & Adjustments
12. Casualty & Condemnation
13. Default & Remedies
14. AS-IS / Disclaimers & Waivers
15. Indemnification
16. Assignment & Transfer Rights
17. Tenant Estoppels & SNDAs
18. Escrow Provisions
19. Brokerage & Commissions
20. Confidentiality & Press Releases
21. Tax Proceedings
22. Assumption of Contracts
23. Mortgage Assignment
24. Miscellaneous / General Provisions

---

## 1. Definitions & Key Defined Terms [Common]

### Review Points

- [ ] **Catalog all defined terms** -- Extract every defined term and its definition. Verify consistent capitalization throughout the document.

- [ ] **Check "Knowledge" definition** -- How is the knowledge qualifier defined? Is it "actual knowledge" or "actual and constructive knowledge"? Who are the named knowledge parties? Are they the right people (decision-makers with day-to-day property operations knowledge)?
  - See: market-standards.md > 1. Definitions & Key Defined Terms > Knowledge Qualifier
  - [TODO: Add firm's standard position on knowledge qualifier scope for institutional sellers]

- [ ] **Check "Material Adverse Effect" or "Material Adverse Change" definition** -- Does the MAE/MAC definition exist? What are the carve-outs? Are industry-wide changes, economy, pandemic, and acts of God excluded?
  - See: market-standards.md > 1. Definitions & Key Defined Terms > MAE/MAC

- [ ] **Check "Permitted Exceptions" definition** -- What title exceptions are pre-approved as permitted? Is the definition overly broad (permitting any exception existing as of the effective date)?

- [ ] **Check "Property" definition scope** -- Does it include personal property, intangible property, contract rights, leases, and warranties in addition to the real property?

- [ ] **Verify "Business Day" definition** -- Does the definition include or exclude specific holidays? Is it consistent with the governing law jurisdiction?

- [ ] **Check "Seller Parties" or exculpation definition** -- Does the definition of protected parties extend beyond the seller entity to include officers, directors, shareholders, agents? How broad is the exculpation?

### Key Risks

| Risk | Buyer Perspective | Seller Perspective |
|------|-------------------|-------------------|
| Narrow knowledge qualifier (actual knowledge only, limited named parties) | High -- seller can disclaim knowledge of property defects known to property managers but not named parties | Favorable -- limits exposure from property-level issues not known to principals |
| No MAE/MAC definition | Medium -- buyer loses termination right for material adverse changes between signing and closing | Favorable -- eliminates buyer walk-away right |
| Overly broad Permitted Exceptions | High -- buyer may take title subject to unknown encumbrances | Favorable -- reduces title cure obligations |
| [TODO: Add additional risks from firm experience] | | |

---

## 2. Property Description & Conveyance [Common]

...
```

### Example 2: Clause Library Stub (clause-library.md)

```markdown
# RE PSA Clause Library

> **Usage:** Sara loads this file during Step 3 for model language reference. Clauses are organized by the same 24 categories as the PSA review checklist.
>
> **Populating this file:** Add model language from negotiated deals. Each entry should include the clause text, source deal (anonymized), and notes on when to use it.
>
> **Entry format:**
> ```
> ### [Clause Name]
> **Source:** [Deal type, approximate date, anonymized]
> **When to use:** [Circumstances where this clause is appropriate]
> **Language:**
> > [Exact clause text]
> **Notes:** [Any caveats, modifications needed for different deal types]
> ```

## Categories

[Same 24 categories as re-checklist-psa.md]

---

## 1. Definitions & Key Defined Terms

### Knowledge Qualifier -- Broad (Buyer-Favorable)
[TODO: Add model knowledge qualifier language that includes actual and constructive knowledge with broad named party list]

### Knowledge Qualifier -- Standard
[TODO: Add model knowledge qualifier language with actual knowledge and standard named party list]

### MAE/MAC Definition -- Standard
[TODO: Add model MAE/MAC definition with standard carve-outs]

---

## 2. Property Description & Conveyance

[TODO: Add model conveyance clause language]

---
```

### Example 3: Market Standards Stub (market-standards.md)

```markdown
# RE PSA Market Standards

> **Usage:** Sara loads this file during Step 3 for market data reference. Standards are organized by the same 24 categories as the PSA review checklist.
>
> **Populating this file:** Add market standard data from deal experience, surveys, and industry resources. Each entry should note the source and date.
>
> **Note:** The format for memorializing market standards is being refined (see GitHub issue #1). For now, use the simple entry format below.

## Categories

[Same 24 categories as re-checklist-psa.md]

---

## 1. Definitions & Key Defined Terms

### Knowledge Qualifier
[TODO: Document market standard for knowledge qualifiers in institutional CRE PSAs -- typical scope (actual vs constructive), typical named parties, regional variations]

### MAE/MAC
[TODO: Document market standard for MAE/MAC definitions -- whether typically included, standard carve-outs, recent trends]

---

## 3. Purchase Price & Deposit Mechanics

### Deposit Amount
[TODO: Document market standard deposit amounts by deal size and type -- typical ranges, institutional vs non-institutional]

### Deposit Structure
[TODO: Document market standard for deposit timing -- when deposits typically go hard, standard DD period protections]

---
```

### Example 4: Sara's Step 3 Integration (contract-review-workflow.md addition)

```markdown
### 3-pre: Load Reference Files

Before beginning research, Sara loads the practice-area-specific reference files for this document type.

**For PSA reviews:**
1. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/re-checklist-psa.md` -- PSA review checklist
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/clause-library.md` -- model language reference
3. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/market-standards.md` -- market data reference

If a file is not found, note the absence and proceed with LLM knowledge. Do not halt the review.

**Coverage report [MVP]:** After loading, count populated vs `[TODO]` placeholder categories in each file. Include in the Step 3d framework presentation:
> "Reference files loaded. PSA checklist: [N]/24 categories have firm-specific content, [M] categories using general legal knowledge. Clause library: [X]/24 populated. Market standards: [Y]/24 populated."

**Selective loading:** Read the checklist's category list first. Then load only the categories that match the document's structure from the Step 2 initial read. For a standard PSA, this will typically be 18-22 of 24 categories. Skip categories that clearly do not apply (e.g., skip "Mortgage Assignment" if the PSA has no mortgage assumption provision).
```

### Example 5: LLM Fallback Marker Convention

```markdown
In the disposition table (Section A), when a review point or risk assessment
is sourced from Sara's general knowledge rather than the checklist or market
standards file, append + to the Market Assessment field:

| Para ID | Section Ref | Disposition | Reasoning | Market Assessment | Risk Severity |
|---------|-------------|-------------|-----------|-------------------|---------------|
| p_15 | 3.1(a) | Revise | Deposit goes hard Day 1 | Below market+ | High |

The + indicates: "Market assessment based on general legal knowledge --
no firm-specific reference data for this item."

In the transmittal memo, append + to any recommendation under Key Changes
or Open Items that is not backed by the checklist or market standards file.
```

## State of the Art

| Current (No Knowledge Layer) | After Phase 2 | Impact |
|------------------------------|---------------|--------|
| Sara builds analysis framework purely from LLM knowledge and ad-hoc research during Step 3 | Sara starts from a structured checklist with 24 categories and comprehensive sub-items, then supplements with research | Consistent coverage across reviews; no categories accidentally missed |
| No firm-specific reference data | `[TODO]` placeholders that the user fills over time with deal experience | Growing institutional knowledge base; Sara improves as files are populated |
| No market standards reference | Market standards stub with cross-references from checklist items | Sara can cite market standards from firm experience (once populated) instead of generic LLM assertions |
| No model language library | Clause library stub with entries for model language from negotiated deals | Sara can reference actual negotiated language (once populated) when proposing alternatives |
| Sara's review coverage varies by session | Checklist ensures systematic coverage of all provision categories | Reduces risk of missing entire categories (the "19 of 170" problem) |
| No transparency about knowledge source | `+` marker distinguishes checklist-backed vs LLM-backed assessments | Partner knows which assessments are grounded in firm data vs Sara's general knowledge |
| No gap analysis | Missing provisions report identifies PSA omissions against the checklist | Partner sees not just what the PSA says, but what it does NOT say |

## Source Document Analysis

### Document 1: PSA form (extremely detailed, seller side).docx

**Structure:** 531 paragraphs, 63 sections, 11 articles, 86 defined terms, 13 exhibits
**Key categories covered:**
- Art 1: Definitions (extensive -- 86 defined terms)
- Art 2: Purchase and Sale / Purchase Price
- Art 3: Deposit (initial + additional deposit)
- Art 4: Title and Survey (detailed objection/cure process)
- Art 5: Investigation / Study Period / Confidentiality / Assumption of Contracts
- Art 6: Conditions Precedent / Casualty / Condemnation / Leasing Activities
- Art 7: Representations & Warranties (buyer + seller, with anti-sandbagging, knowledge qualifiers, bring-down)
- Art 8: Closing / Deliveries / Costs & Prorations / Tenant Notices
- Art 9: Brokerage Commissions
- Art 10: Default & Remedies (purchaser default, seller default, breach of reps)
- Art 11: Miscellaneous (assignment, governing law, time of essence, liability limitations, escrow)

**Unique provisions not in other docs:** Anti-sandbagging (Sec 7.4), Seller's Estoppel Certificate (Exhibit B-1), detailed prorations methodology (Sec 8.4), leasing activities covenant (Sec 6.6), 1031 exchange provisions, Seller's Additional Title Election Period, Restricted Period for deposit

### Document 2: PSA - (Pro-Buyer Long Form) (IL).doc

**Structure:** 21 articles, 90+ sections, 85 pages
**Key categories covered (mapped to 24-category list):**
- Art I: Definitions
- Art II: Purchase and Sale (property description)
- Art III: Purchase Price and Deposit (including financing contingency -- Sec 3.04)
- Art IV: Investigation (DD materials, DD extension period, purchaser access, inspection rights, seller indemnification)
- Art V: Escrow (escrow terms, no liability)
- Art VI: Closing (closing date, adjournment rights)
- Art VII: Title Matters (title objection, unable to convey, title as seller can convey, violations, liens, judgment affidavit)
- Art VIII: Closing Deliveries (seller's + purchaser's)
- Art IX: Closing Costs (allocated by party)
- Art X: Apportionments (taxes, security deposits, operating costs, insurance, post-closing adjustments)
- Art XI: Tax Proceedings (at seller's initiative, at purchaser's request, refunds)
- Art XII: Seller's Covenants
- Art XIII: Representations & Warranties (seller + purchaser, with survival, no-representations clause, bring-down certificate)
- Art XIV: Conditions to Closing (seller + purchaser conditions, failure of conditions)
- Art XV: Brokerage Commissions
- Art XVI: AS-IS (as-is where-is, no warranty, survival)
- Art XVII: Casualty & Condemnation (uninsured loss, underinsured loss, waiver of law)
- Art XVIII: Default (purchaser's default, seller's default, exculpation)
- Art XIX: Confidentiality and Press Release
- Art XX: General Provisions (notices, complete agreement, assignment, 1031 exchange, further assurances, interpretation, time of essence, governing law, jury waiver, attorneys' fees)
- Art XXI: Estoppel Certificates (tenant estoppels, seller estoppels)

**Unique provisions not in other docs:** Financing contingency (Sec 3.04), DD extension period (Sec 4.04), separate tax proceedings article (Art XI), seller indemnification for purchaser's inspections (Sec 4.07), detailed violations cure obligations (Sec 7.06), judgment affidavit (Sec 7.07), exculpation clause (Sec 18.03), no-representations provision (Sec 13.05)

### Document 3: PSA Negotiation Checklist (Commercial Real Estate) (Purchaser) (NY).doc

**Structure:** 20 categories, practitioner-framed guidance, NY-specific references
**Key categories covered:**
1. Parties to the PSA
2. Enforceability
3. Property Identification (real + additional property)
4. Financial Terms
5. Due Diligence Review
6. Title Review
7. Assignment of Seller's Existing Mortgage
8. Risk of Loss
9. Closing
10. Seller Covenants
11. Purchaser's Closing Conditions
12. Tenant Estoppels and SNDAs
13. Right to Assume Contracts
14. Seller's Required Closing Documents (deed, bill of sale, assignments, tax forms, other)
15. Representations and Warranties from the Seller
16. Purchaser's Right to Assign
17. Default Remedies
18. Confidentiality and Press Releases
19. Brokerage Provisions
20. Escrow Agent Provisions

**Special value:** Already framed as practitioner guidance ("The purchaser should negotiate for...", "Ensure that...", "Negotiate that..."). Sub-items are at the right level of specificity for checklist review points. Includes cross-references to Practical Law standard documents and drafting notes.

**Unique items not in the PSA texts:** Enforceability / statute of frauds requirements, bulk sales considerations, mortgage recording tax (MRT) considerations for mortgage assignment, specific estoppel timing requirements (dated within 30 days, delivered 5-10 business days before closing), seller solvency representations, security for post-closing rep breaches (escrow, letter of credit, parent guarantee)

### Mapping: 24 Categories to Source Documents

| # | Category | Seller PSA | Buyer PSA (IL) | NY Checklist |
|---|----------|-----------|----------------|--------------|
| 1 | Definitions & Key Defined Terms | Art 1 (86 terms) | Art I | -- |
| 2 | Property Description & Conveyance | Art 2 | Art II | Property ID |
| 3 | Purchase Price & Deposit Mechanics | Art 2-3 | Art III | Financial Terms |
| 4 | Due Diligence / Investigation Period | Art 5 | Art IV | DD Review |
| 5 | Title & Survey | Art 4 | Art VII | Title Review |
| 6 | Representations & Warranties | Art 7 | Art XIII | Reps |
| 7 | Seller's Pre-Closing Covenants | Art 6 (6.6) | Art XII | Seller Covenants |
| 8 | Conditions Precedent to Closing | Art 6 (6.1-6.2) | Art XIV | Closing Conditions |
| 9 | Closing Mechanics | Art 8 (8.1) | Art VI | Closing |
| 10 | Closing Deliveries | Art 8 (8.2-8.3) | Art VIII | Seller Deliveries |
| 11 | Costs, Prorations & Adjustments | Art 8 (8.4) | Art IX-X | -- |
| 12 | Casualty & Condemnation | Art 6 (6.3-6.5) | Art XVII | Risk of Loss |
| 13 | Default & Remedies | Art 10 | Art XVIII | Default |
| 14 | AS-IS / Disclaimers & Waivers | -- (embedded) | Art XVI | -- |
| 15 | Indemnification | -- (scattered) | Sec 4.07 | -- |
| 16 | Assignment & Transfer Rights | Art 11 (11.2-11.3) | Sec 20.03 | Assignment |
| 17 | Tenant Estoppels & SNDAs | Art 8 (8.5) | Art XXI | Estoppels |
| 18 | Escrow Provisions | Art 11 (11.21) | Art V | Escrow |
| 19 | Brokerage & Commissions | Art 9 | Art XV | Brokerage |
| 20 | Confidentiality & Press Releases | Art 5 (5.3) | Art XIX | Confidentiality |
| 21 | Tax Proceedings | -- | Art XI | -- |
| 22 | Assumption of Contracts | Art 5 (5.5) | -- | Contracts |
| 23 | Mortgage Assignment | -- | -- | Mortgage Assignment |
| 24 | Miscellaneous / General Provisions | Art 11 | Art XX | Enforceability, Parties |

**Coverage analysis:** Every category is covered by at least one source document. Categories 1-13 have the deepest coverage (all three documents address them in some form). Categories 14-24 are more specialized and may have coverage from only one or two sources. The NY Checklist is the most valuable single source for sub-item framing because it is already written as practitioner guidance.

## Open Questions

1. **Checklist file size vs context window budget**
   - What we know: 24 categories x ~20 sub-items = ~480 review points. With Key Risks tables, formatting, and instructions, the file will be 800-1200 lines. Sara also needs to hold the document being reviewed (potentially 170+ paragraphs) plus delegation briefings.
   - What's unclear: Whether Sara should read the entire checklist or only relevant categories during a single review session.
   - Recommendation: Instruct Sara to read the checklist selectively -- table of contents first, then relevant categories. This is reflected in the Step 3-pre pattern above. The planner should design the checklist with a clear table of contents that enables selective reading.

2. **Common vs Specialized category tagging**
   - What we know: Some categories apply to every PSA (Definitions, Purchase Price, DD, Title, Reps, Default). Others are specialized (Tax Proceedings, Mortgage Assignment, Assumption of Contracts).
   - What's unclear: The exact Common/Specialized classification for each of the 24 categories.
   - Recommendation: Tag each category in the checklist header (e.g., `## 21. Tax Proceedings [Specialized]`). Sara uses this tag to filter the missing provisions report. Proposed classification: Categories 1-13 are Common; 14-24 are Specialized. The planner should verify this with the user or adjust based on practice.

3. **Integration with `references/` symlink directory**
   - What we know: The project has two reference directories -- `skills/sara/references/` (authoritative) and `references/` (symlinked/copied for easier access). Phase 1 created reference files in both locations.
   - What's unclear: Should the new files go in both directories? The STRUCTURE.md says they are "Symlinked/copied" but git status shows the `references/` files were modified/deleted separately from `skills/sara/references/`.
   - Recommendation: Create the authoritative files in `skills/sara/references/` only. The `references/` directory can be updated separately (or symlinked) as a housekeeping task. Sara references files via `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/`.

4. **Checklist sub-item count per category**
   - What we know: The user wants "comprehensive sub-items" covering "the full rotation of specific concepts." The NY Checklist alone has dozens of sub-items per major category.
   - What's unclear: How many sub-items per category is "comprehensive" without being exhaustive to the point of noise?
   - Recommendation: Target 10-25 sub-items per Common category (categories 1-13) and 5-15 per Specialized category (categories 14-24). Source every sub-item from a specific provision or concept in one of the three sample documents. The NY Checklist's practitioner-framed sub-items are the best source for appropriate granularity.

## Sources

### Primary (HIGH confidence)
- `/home/david/projects/AI-Associate/.sample-docs/PSA form (extremely detailed, seller side).docx` -- extracted via `extract_structure` tool: 531 paragraphs, 63 sections, 86 defined terms, 11 articles
- `/home/david/projects/AI-Associate/.sample-docs/PSA - (Pro-Buyer Long Form) (IL).doc` -- extracted article/section headings via binary parsing: 21 articles, 90+ sections
- `/home/david/projects/AI-Associate/.sample-docs/PSA Negotiation Checklist (Commercial Real Estate) (Purchaser) (NY).doc` -- full text extracted via RTF reader: 20 categories with practitioner-framed sub-items
- `/home/david/projects/AI-Associate/skills/sara/SKILL.md` -- current Sara behavioral framework including reference file loading pattern, Step 3 workflow, quality standards
- `/home/david/projects/AI-Associate/skills/sara/references/contract-review-workflow.md` -- current Step 3 framework building process and target list format
- `/home/david/projects/AI-Associate/agents/document-reviewer.md` -- current Section A disposition table format including Market Assessment column
- `/home/david/projects/AI-Associate/agents/document-drafter.md` -- current transmittal package assembly format
- `/home/david/projects/AI-Associate/.planning/phases/02-knowledge-layer/02-CONTEXT.md` -- user decisions and locked constraints
- `/home/david/projects/AI-Associate/.planning/REQUIREMENTS.md` -- KNOW-01 and KNOW-02 requirement definitions
- `/home/david/projects/AI-Associate/.planning/ROADMAP.md` -- phase description and success criteria

### Secondary (MEDIUM confidence)
- `/home/david/projects/AI-Associate/.planning/phases/01-behavioral-foundation/01-RESEARCH.md` -- Phase 1 research showing the prompt engineering patterns and quality gate design that Phase 2 reference files must integrate with
- `/home/david/projects/AI-Associate/.planning/codebase/ARCHITECTURE.md` -- system architecture showing data flow through Step 3 framework building
- `/home/david/projects/AI-Associate/.planning/codebase/STRUCTURE.md` -- file organization patterns and naming conventions

### Tertiary (LOW confidence)
- None -- all findings sourced from codebase analysis and sample documents

## Metadata

**Confidence breakdown:**
- Checklist category structure: HIGH -- derived directly from exhaustive analysis of all 3 sample documents, with the 24-category list locked by user decision
- Checklist sub-item format: HIGH -- design follows standard markdown patterns verified against Sara's existing file loading and reading behavior
- Graceful degradation behavior: HIGH -- behavioral specification with clear implementation (string matching for `[TODO]`, `+` marker in disposition table)
- Clause library and market standards stubs: HIGH -- straightforward stub files with matching category structure; substantive content explicitly out of scope
- Step 3 integration: HIGH -- clear integration point identified in existing contract-review-workflow.md; follows established pattern of Sara loading reference files via `${CLAUDE_PLUGIN_ROOT}` path
- Context window management: MEDIUM -- selective loading recommendation is sound but exact thresholds need empirical validation during actual reviews

**Research date:** 2026-02-18
**Valid until:** 2026-04-18 (60 days -- stable domain; markdown reference files and behavioral specifications do not change with external dependencies)
