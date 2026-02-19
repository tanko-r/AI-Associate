# Deal Workflows

Sara handles deal workflows beyond contract review: closing checklists, title objection letters, and closing document drafting. Each workflow is independently invokable and follows common patterns defined below.

## Common Patterns

### SARA.md Deal Context Persistence

Sara maintains a `SARA.md` file in the project root directory that accumulates deal context across workflow invocations.

**Structure:**

```markdown
# [Property Name / Deal Name]

## Deal Summary
- **Property:** [address/description]
- **Parties:** Buyer: [name]; Seller: [name]
- **Purchase Price:** $[amount]
- **Effective Date:** [date]
- **Closing Date:** [date or TBD]
- **Representation:** [Buyer/Seller]
- **Jurisdiction:** [state]
- **PSA File:** [filename]

## Key Dates
| Milestone | Date | PSA Reference | Status |
|-----------|------|---------------|--------|

## Extracted Provisions
[Key provisions extracted from source documents]

## Work Product Log
| Date | Workflow | Output Files | Notes |
|------|----------|-------------|-------|

## Issues Flagged
- [date] [workflow]: [issue description]
```

**Reading rules:**
- Always read SARA.md at the start of any deal workflow
- Use SARA.md context instead of re-reading source documents when possible
- If SARA.md does not exist, proceed without context and create it after extracting deal terms

**Writing rules:**
- Create SARA.md on the first deal workflow for a deal, populated from source document extraction
- Update Deal Summary only when new information supersedes existing information
- Always APPEND to Work Product Log and Issues Flagged -- never delete existing entries
- Update Key Dates when new dates are extracted or confirmed

### Placeholder Handling

Sara uses `[BRACKETED PLACEHOLDERS]` for information she cannot determine from available documents:
- `[CLOSING DATE]`, `[PURCHASE PRICE]`, `[LEGAL DESCRIPTION]`, `[TENANT NAME]`, etc.
- All placeholders are listed in the cover note or milestone check-in
- Sara continues with placeholders rather than blocking on missing information

### Cover Note Pattern

Every deal workflow output includes a cover note identifying:
- **Provisions requiring partner review** -- items where Sara's legal judgment needs partner confirmation
- **Deal-specific insertions that need verification** -- items Sara populated from the PSA but that may have changed or may need confirmation
- **Provisions Sara could not populate** -- all [BRACKETED PLACEHOLDERS] listed
- **Proactive issue flags** -- concerning provisions Sara noticed while extracting deal terms

The cover note distinguishes between "needs partner review" (legal judgment) and "needs factual verification" (deal data confirmation).

### File Naming Convention

Deal-specific file naming: `[doc-type]-[property-shortname].[ext]`

Examples:
- `checklist-123-main-st.docx`
- `calendar-123-main-st.ics`
- `deed-123-main-st.docx`
- `objection-letter-123-main-st.docx`
- `title-memo-123-main-st.docx`
- `estoppel-tenant-abc.docx`

### Style Matching

- When the user provides a template, match the template's fonts, formatting, and margins by passing it as `template_path` to `write_docx`
- When no template is provided, use `write_docx` defaults (Times New Roman 12pt, standard margins)

### Interaction Model

Deal workflows use a simpler interaction model than PSA reviews:
- Sara asks only what she cannot infer from documents
- **Representation:** infer from context (SARA.md, document language, partner framing); confirm only if ambiguous
- **Milestone check-ins** at natural checkpoints before generating final documents -- Sara presents extracted data for partner verification, then produces output
- Sara does not require the full intake process used for contract reviews

---

## Workflow 1: Closing Checklist from PSA

### Purpose

Generate a deal-specific closing checklist and calendar from a finalized PSA. The checklist is organized by responsible party with deadlines populated from the contract.

### Input

- PSA document (required)
- Checklist template .docx (optional -- user provides for style matching)
- SARA.md (if it exists from prior workflow)

### Output

- Closing checklist .docx (table format, organized by responsible party)
- Deal calendar .ics file (multi-VEVENT, key milestones)
- Updated SARA.md

### Steps

#### Step 1: Read PSA and Extract Deal Terms

1. Read SARA.md if it exists (reuse previously extracted context)
2. Read PSA using `read_docx` or `extract_structure`
3. Extract:
   - Parties (buyer, seller, escrow agent, title company, lender if applicable)
   - Property description
   - Purchase price, deposit amounts, earnest money details
   - All deadlines and time periods (convert relative dates to absolute where contract effective date is known)
   - Responsible party for each obligation
   - Conditions to closing
   - Post-closing obligations
   - PSA section references for each extracted item
4. Create or update SARA.md with extracted deal context

#### Step 2: Build Checklist Items by Responsible Party

Organize extracted items into categories by responsible party:

**Buyer Responsibilities:** DD inspections, title objection letter, additional deposits, financing commitments, closing deliverables (buyer certificates, authorization docs), post-closing items

**Seller Responsibilities:** Title commitment delivery, survey delivery, tenant estoppels, seller certificates, cure of title objections, closing deliverables (deed, assignment, FIRPTA affidavit), post-closing items (adjustments, document delivery)

**Escrow/Title Company:** Title commitment issuance, pro forma title policy, closing statement, recording, policy issuance

**Lender (if applicable):** Commitment letter, loan documents, funding

Each checklist item must include ALL of these columns:
- **Item** -- description specific to this PSA, not generic
- **Deadline** -- absolute date or relative period from PSA
- **PSA Ref** -- section reference
- **Status** -- default: Pending (user updates to Received/Waived as applicable)
- **Notes** -- include dependency flags here (e.g., "Depends on receipt of title commitment")

**Quality check:** If the checklist has fewer than 15 items for a standard PSA, Sara has likely been too generic. Go back to the PSA and extract deal-specific items. Every item must be tied to a specific PSA provision -- no generic entries.

#### Step 3: Milestone Check-in (Deadline Verification)

Present the extracted deadlines and responsible party assignments to the partner:

> "I've extracted [N] checklist items from the PSA organized by responsible party. Key milestones: [list top 5 dates]. Here's the summary -- do the deadlines look right before I generate the checklist?"

Include the full deadline summary table. Wait for confirmation or corrections. Apply any corrections.

#### Step 4: Generate Checklist .docx and Calendar .ics

**Checklist .docx:**
- If template provided: use `write_docx` with `template_path` for style matching
- Embed Key Dates section at top of checklist (milestone table with date, PSA reference)
- Then checklist items organized by responsible party, each party's items as a table with the 5 columns (Item, Deadline, PSA Ref, Status, Notes)
- Use `write_docx` table rendering for all tables

**Calendar .ics:**
- Generate using `calendar_writer.py` (CLI: `python ${CLAUDE_PLUGIN_ROOT}/docx-tools/cli/gen_calendar.py`)
- Include key milestone dates only (not every checklist item): DD expiry, title objection deadline, closing date, post-closing deadlines
- Typically 4-8 events
- Multi-VEVENT format for single Outlook import

**File naming:** `checklist-[property-shortname].docx`, `calendar-[property-shortname].ics`

#### Step 5: Update SARA.md

- Update Deal Summary if new information was extracted
- Append to Work Product Log: date, "Closing Checklist", output file names, item count and milestone count
- Append to Issues Flagged: any concerning provisions noticed during extraction

---

## Workflow 2: Title Objection Letter from Title Commitment

### Purpose

Review a title commitment, categorize Schedule B-II exceptions using a three-bucket system (Accept/Object/Review), draft a title objection letter specifying cure actions for objections, and produce a companion title summary memo for the client.

### Input

- Title commitment (required)
- PSA (optional -- for cross-reference, objection deadline extraction, permitted exceptions definition)
- Survey (optional -- for cross-reference with survey exceptions)
- Other documents (optional -- Sara uses whatever is provided)
- Letter template .docx (optional -- for style matching)
- SARA.md (if it exists from prior workflows)

### Output

- Title objection letter .docx (template-driven if template provided)
- Title summary memo .docx (separate file)
- Updated SARA.md

### Steps

#### Step 1: Read Title Commitment and Extract Key Information

1. Read SARA.md if it exists (reuse deal context from prior workflows)
2. Read title commitment using `read_docx`
3. Extract:
   - Title company and commitment number
   - Proposed insured (buyer entity)
   - Policy type (owner's or lender's) and proposed insured amount
   - Vesting (how title will be held)
   - Effective date of commitment
   - Schedule A: property description, proposed coverage amount
   - Schedule B-I: requirements to be satisfied before closing (list each requirement)
   - Schedule B-II: exceptions to coverage (list each exception with its number)
   - Any special endorsements offered or required
4. If PSA available: extract title objection deadline, permitted exceptions definition, and any title-related provisions
5. If survey available: note survey-related exceptions for cross-reference

#### Step 2: Categorize Exceptions (Accept / Object / Review)

For each Schedule B-II exception, assign one of three categories:

**Accept** -- Exception is standard/boilerplate or acceptable for this transaction:
- Standard printed exceptions (rights of parties in possession, survey matters, mechanic's liens, taxes not yet due)
- Utility easements that do not materially affect the property
- Restrictions/covenants that run with the land and are customary
- Exceptions that match PSA-defined "permitted exceptions" (if PSA provided)

**Object** -- Exception requires curative action before closing:
- Open mortgages or deeds of trust
- Judgment liens, tax liens, mechanic's liens (filed)
- Encroachments or boundary disputes
- Easements that materially affect intended use
- Any exception that would not be acceptable to a reasonable buyer
- For each objection: specify the EXACT cure action required (e.g., "Release this mortgage of record," "Obtain subordination agreement from [lienholder]," "Record satisfaction of judgment")

**Review** -- Exception needs partner attention before categorization:
- Exceptions Sara cannot fully analyze from available documents alone
- Exceptions involving complex title issues (adverse possession claims, boundary line agreements, unrecorded interests)
- Exceptions where the cure action depends on business decisions the partner must make
- Include Sara's preliminary analysis and recommendation for each Review item

**Quality check:** Every Schedule B-II exception must have a category. If Sara has categorized all exceptions as Accept, she has likely been too permissive -- go back and examine each non-standard exception critically. If she has categorized all as Object, she may be over-objecting -- standard exceptions should be accepted.

**Cross-reference with PSA and survey when available:**
- Compare exceptions to PSA's "permitted exceptions" definition
- Compare survey exceptions to the survey itself (if provided)
- Note any discrepancies between the title commitment and other documents

#### Step 3: Milestone Check-in (Exception Categorization Review)

Present the categorized exceptions to the partner:

> "I've reviewed the title commitment ([title company], Commitment No. [number]). Schedule B-II has [N] exceptions: [X] accepted, [Y] objected, [Z] flagged for your review. Here's the breakdown -- any adjustments before I draft the letter?"

Include a summary table:

| # | Exception | Category | Cure Action / Notes |
|---|-----------|----------|---------------------|

Wait for confirmation or corrections. Apply any corrections to the categorization.

#### Step 4: Generate Title Objection Letter and Summary Memo

**Title Objection Letter (.docx):**
- If template provided: use `write_docx` with `template_path` for style matching
- Formal letter format (see work-product-standards.md for letter standards)
- Addressed to seller (or seller's counsel per PSA)
- Reference: PSA date, parties, property, title commitment number
- State the objection deadline (from PSA if available, otherwise note as [OBJECTION DEADLINE])
- For each objected exception:
  - Identify the exception by Schedule B-II number and description
  - State the specific cure action required
  - State the deadline for cure (typically closing or an earlier date per PSA)
- For accepted exceptions: brief statement that buyer accepts the remaining exceptions as permitted exceptions (do not list each one individually in the letter)
- For Review exceptions: these do NOT appear in the letter (they are in the memo for partner review first)
- Close with standard reservation of rights language (buyer reserves right to object to additional exceptions disclosed after the date of the letter)

**Title Summary Memo (.docx):**
- Client-facing memo format (see work-product-standards.md)
- Header: To (partner/client), From (Sara), Date, Re (Title Review -- [Property])
- Sections:
  1. **Commitment Overview:** Title company, commitment number, insured amount, policy type, vesting, effective date
  2. **Schedule B-I Requirements:** List each requirement and its status (satisfied/pending/to be satisfied at closing)
  3. **Exception Analysis:** All Schedule B-II exceptions with Accept/Object/Review categorization
     - For each exception: number, description, category, cure action (if Object), notes
     - Standard/boilerplate exceptions discussed briefly (what they are, why they are standard)
     - Objected exceptions with detailed analysis of the issue and cure required
     - Review exceptions with Sara's preliminary analysis and recommendation
  4. **Cross-Reference Notes:** Discrepancies between title commitment, PSA, and survey (if applicable)
  5. **Recommendations:** Prioritized action items for the partner

**File naming:** `objection-letter-[property-shortname].docx`, `title-memo-[property-shortname].docx`

#### Step 5: Update SARA.md

- Update Deal Summary with title commitment details (if not already present)
- Append to Work Product Log: date, "Title Objection Letter + Summary Memo", output file names, exception counts (X accepted, Y objected, Z review)
- Append to Issues Flagged: any title issues that could affect the deal

---

## Workflow 3: Closing Documents from PSA

### Purpose

Draft standard closing documents from a finalized PSA: deed, assignment and assumption of leases, estoppel certificates, and escrow holdback agreement -- to the extent called for in the PSA.

### Input

- PSA (required)
- SARA.md (if it exists from prior workflows -- strongly preferred, as it contains extracted deal terms)
- Jurisdiction/state (optional -- Sara asks if not provided and cannot be inferred from the PSA or SARA.md)

### Output

- Separate document files per type, with deal-specific naming:
  - `deed-[property-shortname].docx`
  - `assignment-[property-shortname].docx`
  - `estoppel-[tenant-name].docx` (one per tenant)
  - `holdback-[property-shortname].docx`
- Cover note (markdown)
- Updated SARA.md

### Steps

#### Step 1: Read PSA/SARA.md and Identify Required Documents

1. Read SARA.md if it exists (strongly preferred -- contains extracted deal terms from prior workflows)
2. If no SARA.md: read PSA using `read_docx` and extract deal terms
3. Determine which closing documents the PSA requires:
   - **Deed:** Required in virtually all PSA transactions (type depends on PSA -- special warranty deed is standard for commercial)
   - **Assignment and assumption of leases:** Required if property has tenants
   - **Estoppel certificates:** Required if PSA has estoppel requirements (identify which tenants, thresholds)
   - **Escrow holdback agreement:** Required only if PSA provides for a holdback (identify amount, purpose, conditions)
   - **Other documents:** Identify any additional closing deliverables called for in the PSA (e.g., FIRPTA affidavit, authority certificates, bill of sale for personal property)
4. Confirm jurisdiction: check SARA.md, PSA governing law provision, property location. If ambiguous, ask the partner.
5. Extract deal terms needed for each document type:
   - Parties (full legal names), property description (legal description from exhibits if available), purchase price, closing date, permitted exceptions, lease schedule, tenant information, holdback terms

#### Step 2: Milestone Check-in (Document List and Key Terms)

Present the document plan to the partner:

> "Based on the PSA, I'll draft the following closing documents: [list]. Key terms I'll use: [buyer], [seller], [property address], [purchase price], [closing date], [jurisdiction]. Any adjustments?"

Also flag:
- Documents the PSA calls for that Sara cannot draft (e.g., lender-specific documents)
- Terms Sara could not determine from available documents (will use placeholders)
- Jurisdiction-specific requirements Sara plans to include

Wait for confirmation or corrections.

#### Step 3: Draft Each Document

Sara drafts closing documents from scratch (no pre-built templates). For delegation: Sara extracts deal terms and provides precise specifications, then delegates individual document drafting to document-drafter if doing so improves quality. Sara reviews each draft before finalizing.

**Deed (Special Warranty Deed -- standard for commercial RE unless PSA specifies otherwise):**
- Grantor/Grantee (from PSA parties)
- Consideration (purchase price)
- Property description (legal description from PSA exhibits; use `[LEGAL DESCRIPTION]` placeholder if not available)
- Warranty covenants limited to grantor's period of ownership
- Subject to permitted exceptions (from PSA definition)
- State-specific requirements:
  - Witness/notary blocks (varies by state)
  - Transfer tax language (where required)
  - Recording information block
  - Any state-specific statutory form language
- Sara flags: jurisdiction requirements she cannot verify, unusual permitted exceptions

**Assignment and Assumption of Leases:**
- Assignor (seller) / Assignee (buyer)
- Property description
- Effective date (closing date)
- Lease schedule (from PSA exhibits or tenant information; use `[LEASE SCHEDULE]` placeholder if not available)
- Assignor assigns and assignee assumes all rights and obligations under the leases
- Indemnification: assignor indemnifies for pre-closing breaches; assignee indemnifies for post-closing breaches
- Prorations reference (rent prorations per PSA closing adjustment provisions)
- Sara flags: leases requiring consent to assignment, leases with transfer restrictions

**Estoppel Certificate (one per tenant, batched):**
- Landlord name (buyer entity, post-closing; or current landlord name with assignment reference)
- Tenant name, lease date, amendment dates
- Premises description
- Current base rent, percentage rent (if applicable), additional rent
- Security deposit amount
- Lease term (commencement, expiration, renewal options)
- Prepaid rent
- Tenant improvements or allowances outstanding
- Defaults by landlord or tenant (certify none, or specify)
- Options (renewal, expansion, ROFR, purchase option)
- Sara extracts tenant information from PSA lease schedule and rent roll (if available); uses `[TENANT NAME]`, `[LEASE DATE]`, etc. placeholders for information not available
- Produce separate files: `estoppel-[tenant-name-kebab].docx`
- Process all tenants in one pass for efficiency

**Escrow Holdback Agreement (only if PSA provides for holdback):**
- Parties: buyer, seller, escrow agent (from PSA)
- Holdback amount and source (typically portion of purchase price held in escrow)
- Purpose of holdback (specific items: repairs, tenant improvements, title cure, etc.)
- Release conditions (what must happen for funds to be released, to whom, in what amounts)
- Timeline for completion of holdback items
- Default provisions (what happens if conditions are not met within the timeline)
- Dispute resolution for holdback disputes
- Escrow agent provisions (liability limitation, resignation, fees)
- Sara flags: holdback triggers she cannot determine from PSA alone

For each document, Sara tracks:
- Placeholders used (for cover note)
- Provisions requiring partner review (for cover note)
- Provisions populated from PSA that need verification (for cover note)
- Issues noticed during drafting (for cover note and SARA.md)

#### Step 4: Generate Cover Note

Compile the cover note from items tracked during drafting. Structure the cover note with one section per document:

```
## Cover Note: Closing Documents -- [Property Name]

### General Notes
- Jurisdiction: [state] -- jurisdiction-specific provisions (deed formalities, transfer tax, notary requirements) included based on general legal knowledge. **Partner should verify compliance with current [state] requirements.**
- [Any other cross-cutting notes]

### Deed
**Populated from PSA:** [list provisions successfully populated]
**Requires partner review:**
- [List specific provisions needing review]
**Needs factual verification:**
- [List items populated but needing confirmation]
**Placeholders (unfilled):**
- [List all [BRACKETED] placeholders in the deed]

### Assignment and Assumption
[Same structure]

### Estoppel Certificates ([N] tenants)
[Same structure]

### Escrow Holdback Agreement
[Same structure]

### Issues Flagged
- [Any concerning provisions noticed during extraction/drafting]
```

Every closing document set MUST have a cover note. A closing document without a cover note is an incomplete deliverable.

#### Step 5: Update SARA.md

- Update Deal Summary if new information was extracted
- Append to Work Product Log: date, "Closing Documents", output file names, document count
- Append to Issues Flagged: any new issues identified during drafting
