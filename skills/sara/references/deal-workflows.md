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

[STUB -- completed in Plan 03-02]

### Purpose

Review a title commitment, categorize exceptions, and produce a title objection letter with a companion title summary memo.

### Input

- Title commitment (required)
- PSA (optional -- for cross-reference and objection deadline)
- Survey (optional -- for cross-reference)
- Letter template .docx (optional)
- SARA.md (if it exists)

### Output

- Title objection letter .docx
- Title summary memo .docx
- Updated SARA.md

### Steps

[To be defined in Plan 03-02]

---

## Workflow 3: Closing Documents from PSA

[STUB -- completed in Plan 03-03]

### Purpose

Draft standard closing documents from a finalized PSA: deed, assignment and assumption, estoppel certificates, escrow holdback agreement.

### Input

- PSA (required)
- SARA.md (if it exists)
- Jurisdiction/state (optional -- Sara asks if not provided and cannot be inferred)

### Output

- Individual document files (deed.docx, assignment.docx, estoppel-[tenant].docx, holdback.docx)
- Cover note
- Updated SARA.md

### Steps

[To be defined in Plan 03-03]
