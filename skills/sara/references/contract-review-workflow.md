# Contract Review Workflow

Structured process for reviewing and redlining opposing counsel's paper. Sara follows this workflow for any contract review assignment, regardless of practice area or document type.

## Overview

Every contract review produces three deliverables:

1. **Risk Map** — every provision that could harm the client, with severity, relationships, and recommended action
2. **Concept Map** — the document's key commercial and structural terms extracted into a structured summary
3. **Transmittal Package** — redline, transmittal memo, and open items list (never a naked redline)

The review is driven by a **dynamically built analysis framework** — Sara determines what to look for based on an initial read and targeted research, not a static checklist.

All work is saved to `Sara-Work-Product/[matter-name]/` and logged in `prompt-log.md`. See the **Work Product** section in the Sara skill for the full directory structure.

## Step 1: Intake and Framing

Sara reads the document and infers context before responding. She presents her assumptions and asks the partner to confirm or correct -- demonstrating competence, not running a questionnaire.

**What Sara infers from the document and partner's framing:**

- **Representation** — who is the client? (buyer, seller, tenant, landlord, borrower, lender, licensor, licensee, employer, employee, acquirer, target, etc.)
- **Document type** — what kind of agreement? (PSA, lease, APA, merger agreement, credit agreement, license, employment agreement, services agreement, etc.)
- **Practice area** — Sara's current specialty (real estate, M&A, finance, IP, employment, etc.)
- **Commercial context** — what is the business objective? (quick close, competitive bid, long-term relationship, etc.)
- **Aggressiveness** — default Level 3 unless context suggests otherwise (1 = conservative/accept market terms, 3 = balanced, 5 = aggressive/maximize client position). See SKILL.md Aggressiveness Levels for scope and coverage requirements at each level.

**Smart defaults interaction:** Sara infers these from the document and partner's framing, presents her assumptions, and asks for confirmation or correction:

> "Based on my read, we're representing [X] in this [type]. The document is [drafted-by], roughly [N] paragraphs, [structure]. I'd suggest Level [N] aggressiveness given [reason]. Does that match, or should I adjust?"

After confirmation, Sara presents a detailed review plan (steps, focus areas, delegation strategy, expected deliverables) and offers to discuss before proceeding.

**Save to:** `analysis/intake-notes.md` — record all framing decisions, assumptions, and the partner's instructions.
**Log:** Append intake summary to `prompt-log.md`.

## Step 2: Initial Read

Read the entire document using `read_docx` or `extract_structure`. This is a **quick orientation pass** — understand the document before analyzing it.

Capture:

1. **Parties and structure** — who the parties are, effective date, organizational structure (article/section numbering)
2. **Deal shape** — what is being exchanged, by whom, under what conditions, what is the economic deal
3. **Defined terms** — catalog all defined terms and their definitions
4. **Document type confirmation** — confirm or correct the document type from Step 1 (e.g., what was described as a "lease" might actually be a sublease, ground lease, or license agreement — the distinction matters)
5. **Initial impressions** — note anything that jumps out as unusual, missing, or heavily one-sided. Do not start systematic issue-spotting yet.

**Save to:** `analysis/initial-read.md` — all observations from the first pass.
**Log:** Append initial read summary to `prompt-log.md`.

## Step 3: Research Phase — Build the Analysis Framework

This is the critical step that makes Sara's review comprehensive and practice-aware. Before doing the detailed review, Sara builds her **target list** — the specific concepts and risks she will analyze for.

### 3-pre: Load Reference Files

Before beginning research, Sara loads the practice-area-specific reference files for this document type.

**For PSA reviews:**
1. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/re-checklist-psa.md` -- PSA review checklist
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/clause-library.md` -- model language reference
3. Read `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/market-standards.md` -- market data reference

**Best-effort loading:** If a file is not found, note the absence and proceed with LLM knowledge. Do not halt the review.

**Selective loading:** Read the checklist's category list first. Then load only the categories that match the document's structure from the Step 2 initial read. For a standard PSA, this will typically be 18-22 of 24 categories. Skip categories that clearly do not apply (e.g., skip "Mortgage Assignment" if the PSA has no mortgage assumption provision).

**Coverage report [MVP]:** After loading, count populated vs `[TODO]` placeholder categories in each file. Include in the Step 3d framework presentation:
> "Reference files loaded. PSA checklist: [N]/24 categories have firm-specific content, [M] categories using general legal knowledge. Clause library: [X]/24 populated. Market standards: [Y]/24 populated."

### 3a: Identify What to Research

Based on the initial read, Sara formulates research questions:

- "What are the key issues and negotiation points in a [document type] from a [representation]'s perspective?"
- "What provisions are standard/market for this type of agreement, and what is considered aggressive or unusual?"
- "What are the major risk areas for a [representation] in a [document type] in [jurisdiction if known]?"
- "What recent developments in [practice area] law affect how this type of agreement should be reviewed?"

### 3b: Conduct Research

Sara delegates research to the `legal-researcher` subagent or conducts it herself using web search. Sources to consult:

- **Practice guides and treatises** — what do practitioners in this area say are the critical provisions?
- **Market surveys and deal studies** — what terms are currently market for this type of transaction?
- **Recent case law** — any recent decisions that highlight risks in this type of agreement?
- **Regulatory developments** — new rules or guidance affecting this contract type?

The depth of research depends on the assignment. For a routine NDA review, Sara may rely on her own knowledge. For a complex development agreement in an unfamiliar submarket, she researches more thoroughly.

**Save to:** `research/` — all research assignments and findings. When delegating to `legal-researcher`, instruct the subagent to save output to `junior-work/researcher/`.
**Log:** Append every research delegation (full Task prompt) and Sara's research questions to `prompt-log.md`.

### 3c: Build the Target List

Sara synthesizes her initial read, practice knowledge, and research into two lists. **Merge checklist review points with research-derived target lists.** Checklist items from re-checklist-psa.md provide the structured baseline; research items add document-specific and deal-specific additions. The final target list should include both sources.

**Target Concept Categories** — the specific concepts Sara will extract from the document into the concept map. These always include the universal categories (see Step 4) plus practice-area-specific categories Sara identified through research.

Format:
```
Target Concept: [Category Name]
What to extract: [Specific elements to find in the document]
Why it matters: [Why this is important for this representation in this document type]
```

**Target Risk Categories** — the specific risk patterns Sara will watch for during the detailed review. These always include the universal risk categories (see Step 5) plus document-specific risk patterns.

Format:
```
Target Risk: [Risk Pattern]
What to look for: [Specific language or structural patterns that indicate this risk]
Why it matters: [What could go wrong for the client]
Typical market position: [What this provision normally looks like in a balanced deal]
```

### 3d: Present the Framework -- Milestone Check-In

Before proceeding to the detailed review, Sara pauses for a structured check-in. This is the **Analysis Framework Gate** -- Sara cannot proceed to Step 4 without a written `analysis-framework.md`.

Sara presents to the partner:

- **Reference file coverage [MVP]:** Coverage report from Step 3-pre (populated vs [TODO] counts for each reference file)
- **Framework summary:** N target concept categories, M target risk patterns identified (including checklist-derived and research-derived items)
- **Key focus areas:** The 3-5 most important risk patterns and why they matter for this representation
- **Research highlights:** Any notable findings from Step 3b that shape the analysis
- **What's next:** Overview of Steps 4-7 and estimated delegation strategy

> "I've done an initial read and researched the key issues for [document type] from [representation]'s perspective. I've identified [N] concept categories and [M] risk patterns to analyze for. The key focus areas are [top 3-5]. Here's my framework -- want to discuss anything before I proceed with the detailed review?"

Sara proceeds unless the partner redirects. This is a status update with an invitation to adjust, not a gate requiring explicit approval.

**Save to:** `analysis/analysis-framework.md` — the full target concept and risk lists.
**Log:** Append the framework summary to `prompt-log.md`.

## Step 4: Build the Concept Map

Extract the document's key commercial and structural terms into categories. The concept map captures **what the deal says** — the risk map (Step 5) captures **what could go wrong**.

### Universal Categories (all contract types)

Every contract review extracts these:

| Category | What to Extract |
|----------|----------------|
| **Consideration** | What each party gives and receives — price, payment terms, earnest money/deposits, milestones |
| **Conditions** | Conditions precedent to closing/performance/effectiveness — what must happen before obligations kick in |
| **Representations & Warranties** | What each party is certifying as true — scope, knowledge qualifiers, materiality qualifiers, bring-down standards |
| **Covenants** | Ongoing obligations — affirmative (must do) and negative (must not do), interim and post-closing |
| **Indemnification** | Who indemnifies whom, for what, baskets, caps, deductibles, survival periods, exclusive remedy provisions |
| **Termination** | How the agreement ends — termination triggers, consequences, survival of provisions, breakup fees |
| **Default & Remedies** | What constitutes default, notice requirements, cure periods, available remedies (damages, specific performance, acceleration) |
| **Liability Limitations** | Caps on liability, exclusion of consequential damages, limitation of remedies |
| **Knowledge Standards** | How "knowledge" is defined, who bears the knowledge qualifier, actual vs. constructive knowledge |
| **Assignment & Transfer** | Restrictions on assignment, change of control provisions, permitted transfers |
| **Dispute Resolution** | Governing law, jurisdiction, arbitration vs. litigation, jury waiver, attorney's fees |
| **Key Defined Terms** | Terms that allocate risk — Material Adverse Effect/Change, Permitted Exceptions, Ordinary Course of Business, etc. |

### Practice-Area Categories

In addition to the universal categories, Sara extracts the target concept categories she identified in Step 3c. These are specific to the practice area, document type, and representation.

For each concept extracted, record:

- **The term or provision** — what the document says
- **Section reference** — where it appears
- **Assessment** — whether it is market, favorable, or unfavorable for the client
- **Interplay** — how it connects to other provisions (e.g., "the indemnification cap in 8.3 applies to breaches of the reps in Article 5")

**Save to:** `analysis/concept-map.md` — the full extracted concept map.
**Log:** When delegating concept extraction to `document-reviewer`, append the full Task prompt to `prompt-log.md`. Instruct the subagent to save output to `junior-work/reviewer/`.

## Step 5: Build the Risk Map

Review each provision and identify risks to the client, guided by the target risk categories from Step 3c.

### Risk Fields

| Field | Description |
|-------|-------------|
| **Section reference** | The specific section/paragraph where the risk appears |
| **Risk type** | Category — either a universal category or one from the target list |
| **Severity** | `high` (deal-breaker or significant exposure), `medium` (important, negotiable), `info` (minor, flag for awareness) |
| **Title** | 3-6 word description |
| **Description** | Why this is a risk — what could go wrong, what exposure it creates |
| **Problematic text** | The exact quoted language that creates the risk |
| **Recommendation** | Specific suggested change or negotiation position |

### Universal Risk Categories

These apply to all contract types:

- **Liability Exposure** — uncapped indemnities, broad reps, unlimited damages, joint and several liability
- **Timing Risks** — short deadlines, strict time-is-of-essence, inflexible schedules, inadequate cure periods
- **Discretionary Language** — "sole discretion", "reasonable" without standards, subjective conditions, consent not to be unreasonably withheld (vs. sole discretion)
- **One-Sided Terms** — asymmetric obligations, unilateral amendment rights, non-mutual provisions
- **Missing Protections** — no caps, no cure periods, missing knowledge qualifiers, no materiality thresholds
- **Default Traps** — hair-trigger defaults, cross-defaults, automatic acceleration, loss of deposit/earnest money
- **Survival Issues** — unlimited or overly long survival periods, too-short survival for key reps
- **Assignment Risks** — unrestricted assignment, change of control triggers, no consent requirement
- **Boilerplate Traps** — integration clause undermining side letters, no-waiver clauses, jury waiver, attorney's fees shifting

Sara also applies the target risk categories from Step 3c, which are tailored to the specific document type and representation.

### Sentence-Level Analysis -- Mandatory

Every sentence in the document must be individually read and assessed. For each sentence, Sara (or the delegated subagent) determines whether a change is warranted for the client's benefit. Do not skip sentences because they "look standard" or appear to be boilerplate. Standard language frequently contains embedded risks (knowledge qualifiers, deemed-approval provisions, one-sided remedies) that only surface on close reading.

For each sentence, the reviewer must make a deliberate **keep** or **change** decision. At Level 4-5, this decision is recorded in the disposition table. At Level 1-3, the analysis still happens -- it is simply not documented at the same granularity.

### Risk Relationships

For each risk, identify how it connects to other provisions in the document:

- **Mitigated by** — other provisions that reduce this risk's severity. Example: "Indemnification cap of $500K in Section 8.3 limits exposure from this uncapped rep."
- **Amplified by** — other provisions that increase exposure. Example: "Automatic termination on breach in Section 10.4 means this ambiguous default trigger could end the deal."
- **Triggers** — obligations or consequences this risk activates. Example: "Breach of this rep triggers indemnification under Section 8.1."

Risk relationships are what distinguish a mechanical clause-by-clause review from a senior associate's analysis. Sara always maps how provisions interact.

### Severity Calibration

Severity depends on both the provision and the client's position:

- **High** — provisions that create material financial exposure, could terminate the deal, or remove key protections. These go in the redline and the transmittal memo.
- **Medium** — provisions that are unfavorable but negotiable, or that create exposure that can be managed. These go in the redline. Some go in the transmittal memo depending on materiality.
- **Info** — provisions worth noting but not worth spending negotiation capital on. Mentioned in the open items list, usually not in the redline.

Aggressiveness setting shifts the thresholds: at level 1 (conservative), only clear problems are flagged as high; at level 5 (aggressive), anything not maximally favorable is flagged.

**Save to:** `analysis/risk-map.md` — the full risk inventory with relationships and severity.
**Log:** When delegating risk analysis to `document-reviewer`, append the full Task prompt to `prompt-log.md`. Instruct the subagent to save output to `junior-work/reviewer/`.

## Step 5.5: Paragraph-Level Disposition Table (Level 4-5 Only)

At aggressiveness Level 4-5, Sara produces a complete paragraph-level disposition table before proceeding to redline preparation. This is the document-reviewer's primary output at high aggressiveness levels.

### Purpose

The disposition table ensures every paragraph in the document has been examined and given an explicit disposition. This prevents the "19 of 170" problem where only obvious issues get flagged.

### Delegation

Sara delegates the disposition table to the document-reviewer in batches (same batching pattern as Step 6 contract-reviser). Each batch includes:

- Paragraph text with IDs
- The analysis framework (target concepts and risks) from Step 3
- Representation and aggressiveness level
- Defined terms
- Prior batch results (for consistency)

### Output Format

The document-reviewer produces Section A (Disposition Table) and Section B (Thematic Risk Map) per its agent prompt specification.

Section A assigns every paragraph one of: **Accept**, **Revise**, **Delete**, **Insert**, **Comment** -- each with brief reasoning including Accepts (e.g., "Standard mutual jury waiver -- market for institutional transactions").

Section B groups related risks by theme, showing how provisions interact (compound risks).

### Coverage Floor Check

After compiling all batches, Sara checks the coverage floor:

- Level 4: 35+ revision entries for a 150-paragraph PSA
- Level 5: 40+ revision entries for a 150-paragraph PSA
- Scale proportionally for shorter/longer documents

If below the floor, Sara flags to the partner: "My review produced [N] revision entries on a [M]-paragraph document. At Level [X], I'd expect [minimum]+. Should I look deeper, or does this coverage seem right for this document?"

### Milestone Check-In

After completing the disposition table, Sara pauses and presents:

- Coverage summary: X paragraphs reviewed, Y revisions, Z acceptances
- Top 5 risks identified
- Disposition breakdown (how many Accept/Revise/Delete/Insert/Comment)
- Any surprises or items needing partner input

**Save to:** `analysis/disposition-table.md`
**Log:** Append compilation summary to `prompt-log.md`

## Step 6: Prepare the Redline

Sara builds the redline by dispatching batched revision tasks to the `contract-reviser` subagent, then compiling their output into a single tracked-changes document.

### Milestone Check-In -- Before Redlining

Before dispatching revision batches, Sara pauses and presents her revision plan to the partner:

- **Batch count:** N batches planned, grouped by article/topic
- **Estimated revision count:** Based on risk map and disposition table (at Level 4-5)
- **FLAG-FOR-SARA items:** Any items from Step 5.5 that required Sara's judgment, and how she resolved them
- **Key decisions:** Any significant choices about revision scope or approach

Sara proceeds unless the partner redirects.

### 6a: Assess Document and Plan Batches

Before dispatching, Sara assesses the document:

- **Document length** — total paragraph count from `read_docx` or `extract_structure`
- **Complexity** — how many risk map entries, how interconnected are the provisions
- **Logical groupings** — group paragraphs by article, topic, or functional area (e.g., all reps together, all covenants together, all indemnification provisions together)

**Batch sizing guidelines:**
- **Simple documents** (< 30 paragraphs, < 10 risks): 1-2 batches, or no batching needed
- **Medium documents** (30-80 paragraphs, 10-25 risks): 3-5 batches of ~15-20 paragraphs
- **Complex documents** (80+ paragraphs, 25+ risks): 5-10 batches of ~10-15 paragraphs, grouped by article/topic

Group related provisions together — don't split a set of reps across two batches if they share defined terms and cross-references. Keep indemnification and the provisions it backstops in the same batch when practical.

### 6b: Dispatch Revision Batches

For each batch, Sara dispatches the `contract-reviser` subagent with:

1. **The batch** — the paragraphs (with paragraph IDs and full text) from `read_docx`
2. **Risk map entries** — only the risks relevant to this batch (filtered from the full risk map)
3. **Concept map** — the full concept map for cross-reference context
4. **Research context** — key findings from Step 3 that affect how these provisions should be revised
5. **Client representation and aggressiveness** — from Step 1 intake
6. **Document map** — a condensed outline of the full document (article/section headings with paragraph IDs) for cross-reference verification
7. **Defined terms** — the document's defined terms list for correct usage in proposed language

**Dispatch sequentially, not in parallel** — each batch may surface conforming changes that affect later batches.

After each batch returns, Sara reviews the output before dispatching the next batch:
- Are the revisions consistent with the risk map recommendations?
- Do the proposed changes use defined terms correctly?
- Are any "FLAG FOR SARA" items that need her judgment before proceeding?
- Are there conforming changes that affect upcoming batches?

### 6c: Review and Compile Revisions

After all batches are complete, Sara:

1. **Reviews all batch outputs together** — look for inconsistencies across batches (e.g., Batch 2 changed a defined term that Batch 4 also used)
2. **Resolves conforming changes** — every batch flags sections outside its scope that need updating; Sara ensures all conforming changes are captured
3. **Resolves "FLAG FOR SARA" items** — make the judgment calls that were escalated
4. **Compiles the revision set** — assemble all revised paragraphs (keyed by paragraph ID) into a single revision map
5. **Generates the redline** — pass the original document and the compiled revision map to `redline_docx` to produce a tracked-changes .docx. **File naming:** `[Original Filename] v02 (redline).docx`. Increment version numbers for subsequent rounds (v03, v04, etc.).

### Redlining Principles

- Every change should serve the client's interest — no changes for style or drafting preference alone
- Prioritize: fix high-severity risks first, then medium, then info if the partner wants a thorough markup
- Cross-reference: when changing one provision, check whether related provisions need conforming changes
- Provide alternatives: when deleting unfavorable language, propose replacement language, not just deletions
- Be realistic: propose language the other side might accept, not a wish list they'll reject entirely

**Save to:** `final/redline-[document-name].docx` — the marked-up document. Batch outputs saved to `junior-work/reviser/batch-[N]-revisions.md`.
**Log:** Append every batch dispatch (full Task prompt with batch contents and context) and Sara's inter-batch review notes to `prompt-log.md`.

## Step 6.5: Final Document QC

After generating the redline and before preparing the transmittal package, Sara re-reads the generated redline document and verifies quality. This is a **hard gate** — Sara cannot proceed to Step 7 without completing this checklist.

### QC Checklist

- [ ] **No duplicate content** — search for repeated paragraphs or sentences that appear more than once. Pay special attention to sections where new language was inserted — anchor-based insertion tools can create duplicates when inserted text contains phrases matching the original anchor.
- [ ] **Formatting consistency** — spot-check that inserted text matches the document's base font, size, and spacing. Read the document in HTML format first to confirm styling. Bare `<p>` tags or unstyled insertions indicate a formatting mismatch.
- [ ] **Cross-reference integrity** — verify all section references still point to correct locations. Insertions and deletions can shift numbering.
- [ ] **Defined term consistency** — verify new or modified defined terms are used consistently throughout the document. Check that no orphaned references to old defined terms remain.
- [ ] **Track changes attribution** — confirm all changes show correct author attribution in the tracked changes metadata.
- [ ] **No orphaned text** — check that no text was accidentally placed outside its intended section (e.g., content appearing after a signature block or between articles where it doesn't belong).

### Remediation

If any QC issue is found:
1. Identify the root cause (tool behavior, batch boundary, cross-reference shift)
2. Fix the issue in the redline document
3. Re-run the specific QC check that failed
4. Document the issue and fix in `prompt-log.md`

**Save to:** Append QC results to `prompt-log.md` with pass/fail for each checklist item.

## Step 7: Prepare the Transmittal Package

Never send a naked redline. The transmittal package is THE primary deliverable -- not the redline itself. The transmittal memo tells the partner what to focus on, organized so they can evaluate the markup efficiently.

### Transmittal Memo

Structured memo with formal sections:

**To:** [Partner name]
**From:** Sara
**Date:** [Date]
**Re:** Review of [Document Type] -- [Property/Deal Name]

#### Deal Summary

2-3 sentences: parties, property, transaction type, purchase price, key dates.

#### Review Scope

- **Representation:** [Buyer/Seller/etc.]
- **Aggressiveness Level:** [1-5] -- [brief description]
- **Document:** [filename], [N] paragraphs, [date]
- **Coverage:** [X] paragraphs reviewed, [Y] revisions, [Z] accepted, [W] commented
- **Focus areas:** top 3-5 from analysis framework

#### Key Changes (Top 5-10)

For each:

1. **[Section Ref] -- [Brief Title]** [Severity: HIGH/MEDIUM]
   - **Issue:** What the current language does and why it is a risk
   - **Change:** What was revised and the market rationale
   - **Partner note:** Anything requiring partner judgment or client input

#### Open Items

Organized by contract provision (not by priority alone) so each item maps to where it lives in the document:

##### Due Diligence

| Item | Section | Issue | Severity | Notes |
|------|---------|-------|----------|-------|
| DD period length | 2.3 | 30 days, no extension right | High | Market: 45-60 days with 15-day extension |

##### Representations & Warranties

| Item | Section | Issue | Severity | Notes |
|------|---------|-------|----------|-------|
| ... | ... | ... | ... | ... |

##### Default & Remedies

| Item | Section | Issue | Severity | Notes |
|------|---------|-------|----------|-------|
| ... | ... | ... | ... | ... |

(Continue for each contract provision category with open items.)

#### Disposition Table (Appendix)

Full Section A table from document-reviewer output (at Level 4-5). At Level 1-3, include a summary risk map instead.

### Delivery Format

The transmittal package is delivered as a .msg file for MS Outlook (Windows) plus a markdown summary in chat. The .msg includes:

- **Email body:** The transmittal memo text
- **Attachments:** Clean docx, redline docx, and disposition table appendix

If the .msg utility is not yet available, Sara prepares all components as files and notes the packaging step for the partner.

**Save to:** `final/transmittal-package.md` (the transmittal memo with embedded open items and disposition appendix).
**Log:** Append the final deliverable list to `prompt-log.md` with a closing entry summarizing the matter.

## Delegation During Review

Sara delegates components of the review to subagent attorneys:

- **`legal-researcher`** -- **Step 3 research**: investigate key issues for this document type in this practice area. Also: research specific legal questions that arise during the detailed review.
- **`document-reviewer`** -- **Steps 4-5 first pass**: section-by-section review using Sara's analysis framework (target lists). Produces initial concept map and risk map draft. At Level 4-5, also produces the **Step 5.5 disposition table** (Section A + Section B) in batches -- same batching pattern as contract-reviser. Sara reviews findings and adds judgment.
- **`contract-reviser`** -- **Step 6 batched revision**: receives a batch of paragraphs with risk map entries, concept map, research context, and defined terms. Returns revised language for each paragraph with changes explained and conforming changes flagged. Sara dispatches multiple batches sequentially and reviews between batches.
- **`document-drafter`** -- **Step 7**: draft the transmittal package from Sara's outline.

Sara always reviews subagent work before it becomes part of the final deliverable. See SKILL.md Quality Loop for the review protocol.

## Quality Checklist

Before presenting the transmittal package to the partner:

**Analysis & Coverage:**
- [ ] Analysis framework was built from initial read + research (not just a generic checklist)
- [ ] Concept map is complete -- all universal categories plus research-driven categories populated
- [ ] Risk map covers every material provision -- no sections skipped without justification
- [ ] Risk relationships are mapped -- each risk has mitigated_by/amplified_by/triggers where applicable
- [ ] Disposition table is complete at Level 4-5 (every paragraph has a disposition)
- [ ] Coverage floor met or partner-approved exception

**Redline Quality:**
- [ ] Redline is internally consistent -- conforming changes made where needed
- [ ] Defined terms are used correctly in proposed language
- [ ] Cross-references in proposed language are accurate
- [ ] Final document QC pass completed (Step 6.5) -- no duplicates, formatting consistent, cross-refs valid
- [ ] Generated redline re-read in full before transmittal package preparation

**Transmittal Package:**
- [ ] Transmittal memo has all required sections (Deal Summary, Review Scope, Key Changes, Open Items)
- [ ] Key Changes highlights the 5-10 most important issues with market rationale
- [ ] Open items organized by contract provision
- [ ] Disposition table included as appendix (Level 4-5)
- [ ] Commercial points are flagged for client input (not decided unilaterally)

**Process:**
- [ ] Milestone check-ins were conducted at each gate
- [ ] All subagent work reviewed against quality gate checklist before acceptance

---

## Appendix: Practice-Area Reference Examples

The examples below illustrate the kinds of practice-area-specific concepts and risks Sara might identify during Step 3 (Research Phase). They are **reference material, not checklists** — Sara's actual target list for any given review is built dynamically from the initial read and research.

### Real Estate

**Purchase and Sale Agreement (PSA):**
- Due diligence period — length, extension rights, termination right, deposit going hard
- Title and survey — permitted exceptions, title cure obligations, title company requirements
- Closing mechanics — prorations, transfer taxes, escrow, closing deliverables
- Property condition — as-is vs. representation-based, environmental, physical condition
- Tenant estoppels and SNDAs — required estoppels, form requirements, material variance thresholds
- Financing contingency — if applicable, commitment deadline, rate lock provisions

**Commercial Lease:**
- Rent structure — base rent, percentage rent, CPI escalation, operating expense pass-throughs (NNN vs. gross vs. modified gross)
- Tenant default triggers and landlord remedies — monetary vs. non-monetary default, cure periods, self-help rights, holdover rent
- Landlord access and entry — notice requirements, emergency access, scope of permitted entry
- Use restrictions — permitted use, exclusive use rights, co-tenancy clauses, radius restrictions
- Maintenance and repair — landlord vs. tenant obligations, capital vs. operating expenses, roof/structure/systems
- Insurance — required coverages, limits, waiver of subrogation, additional insured requirements
- Assignment and subletting — consent standard (sole discretion vs. not unreasonably withheld), recapture rights, profit sharing
- Tenant improvements — TI allowance, construction standards, landlord approval, ownership of improvements
- Options — renewal options, expansion rights, ROFO/ROFR, purchase options, termination options

**Construction/Development Agreement:**
- Completion obligations — milestone deadlines, substantial completion definition, punchlist
- Payment mechanics — progress payments, retainage, lien waivers, change order process
- Performance security — bonds, letters of credit, guarantees
- Force majeure — scope of qualifying events, notice requirements, delay extensions
- Approvals — governmental approvals, subjective vs. objective standards, deemed approval

### M&A / Corporate

**Asset Purchase Agreement (APA):**
- Purchased assets — included vs. excluded assets, assumption of liabilities, bulk sales compliance
- Purchase price — allocation, adjustment mechanisms (working capital, earn-out), escrow holdback
- Employee matters — transferred employees, benefit plan assumptions, WARN Act compliance
- Non-compete — scope, duration, geographic limitation, carve-outs
- Third-party consents — required consents, material consents, failure to obtain

**Merger Agreement:**
- Deal protection — no-shop/go-shop, fiduciary out, matching rights, break-up fees, reverse break-up fees
- MAC/MAE definition — carve-outs (industry-wide changes, economy, pandemic), disproportionate impact qualifier
- Interim operating covenants — ordinary course standard, negative covenants, consent requirements
- Closing conditions — regulatory approvals, shareholder approval, minimum condition, financing condition
- Specific performance — availability, conditions, interplay with termination fee

**Stock Purchase Agreement:**
- Securities law compliance — exemptions, investment representations, legends
- Stockholder matters — drag-along, tag-along, preemptive rights, anti-dilution
- Governance — board composition, protective provisions, information rights

### Finance / Lending

**Credit Agreement / Loan Agreement:**
- Interest and fees — rate structure (fixed/floating), benchmark (SOFR, etc.), spread, default rate, commitment fees, unused line fees
- Financial covenants — leverage ratio, fixed charge coverage, minimum liquidity, testing frequency
- Negative covenants — debt incurrence, lien limitations, restricted payments, asset sales, affiliate transactions
- Events of default — payment default, covenant default, cross-default, change of control, judgment default, bankruptcy
- Cure periods — payment cure, covenant cure, MAE qualification
- Remedies — acceleration, sweep rights, cash dominion, blocked account control

**Guaranty:**
- Scope — full recourse vs. carve-out guaranty, payment vs. performance
- Carve-out triggers — bad acts, voluntary bankruptcy, fraud, waste, environmental
- Defenses waived — marshalling, subrogation, contribution
- Cap — if limited, the cap amount and burn-down provisions

### IP / Technology

**License Agreement:**
- Grant scope — exclusive vs. non-exclusive, field of use, territory, sublicense rights
- IP ownership — background IP, foreground IP, improvements, joint ownership
- Royalties — rate, minimum royalties, most-favored-nation, audit rights
- Warranties — non-infringement, title, functionality
- Source code escrow — triggers, verification rights

**SaaS / Services Agreement:**
- SLA — uptime commitment, measurement, credits, termination trigger
- Data rights — ownership, portability, deletion, privacy compliance (GDPR, CCPA)
- Security — standards, breach notification, audit rights, SOC 2 / ISO 27001
- Limitation of liability — cap (typically 12 months fees), carve-outs, consequential damages exclusion

### Employment

**Employment Agreement:**
- Compensation — base, bonus (discretionary vs. formulaic), equity, benefits
- Restrictive covenants — non-compete (scope, duration, geography), non-solicit (customers and employees), non-disparagement, confidentiality
- Termination — for cause definition, good reason definition, severance triggers and amounts, change of control provisions
- IP assignment — scope, pre-existing IP carve-out, moral rights waiver
- Clawback — bonus clawback triggers, equity forfeiture
