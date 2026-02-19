# Phase 3: Deal Workflows - Research

**Researched:** 2026-02-18
**Domain:** Deal workflow orchestration for closing checklists, title objection letters, title summary memos, closing document drafting, .ics calendar generation, and deal context persistence -- all implemented as behavioral specifications in Sara's skill framework with supporting docx tooling enhancements
**Confidence:** HIGH

## Summary

Phase 3 adds three independently invokable deal workflows to Sara: (1) closing checklist generation from a finalized PSA, (2) title objection letter and summary memo from a title commitment, and (3) closing document drafting (deeds, assignments, estoppels, escrow holdback agreements). Each workflow reads source documents via the existing `read_docx`/`extract_structure` tools, applies Sara's legal analysis, and produces professional docx output via `write_docx`. The implementation is primarily behavioral specification (new workflow definitions in reference files, SKILL.md updates, and document-drafter agent updates) with a modest amount of new tooling: (a) enhanced `write_docx` for table-based documents like checklists, (b) a new `generate_ics` utility for deal calendar files, and (c) a SARA.md deal context persistence mechanism.

The existing docx-tools pipeline is adequate for most of this phase's needs. The `write_docx` function currently handles headings, paragraphs, and inline bold/italic -- but closing checklists require table generation, and template-driven documents require style matching from user-provided docx templates. The `write_docx` function already accepts a `template_path` parameter and clears the template content while preserving styles. What is missing is (a) table rendering from markdown-like table syntax, (b) richer formatting support (numbered lists, checkboxes for status columns), and (c) possibly cell-level paragraph formatting for multi-column checklist rows. These are bounded, well-understood python-docx enhancements.

The .ics calendar file is a new output type. The Python `icalendar` library (not currently installed) provides a clean API for generating RFC 5545 compliant calendar files with multiple VEVENT entries. This is a small addition -- a single utility function that takes a list of events (date, summary, description) and writes a multi-VEVENT .ics file. Alternatively, Sara can generate the .ics content directly as text (the format is simple enough), avoiding a new dependency entirely.

**Primary recommendation:** Implement in three plans: (03-01) Closing checklist workflow with enhanced write_docx for tables and .ics calendar generation; (03-02) Title objection letter and summary memo workflow; (03-03) Closing document drafting workflow. A cross-cutting fourth concern -- SARA.md deal context persistence -- should be wired in during 03-01 and used by all subsequent workflows. All plans modify behavioral specifications (reference files, SKILL.md) and the document-drafter agent, with 03-01 also requiring docx-tools enhancements.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Closing Checklist
- Template-driven: user provides a docx template, Sara adapts it to the deal
- Full detail per item: item + deadline + responsible party + PSA reference + status column (pending/received/waived) + notes column + dependency flags
- Dependencies flagged in notes column (not a formal dependency tracking system)
- Key dates section embedded at top of checklist (not a separate document)
- Single .ics calendar file with key milestone dates (DD expiry, title objection deadline, closing, post-closing) -- multi-VEVENT format for single Outlook import
- Input: PSA only (other documents feed separate workflows)
- Output: docx file

#### Title Objection Letter
- Template-driven: user provides a docx letter template, Sara adapts it
- Three-bucket exception categorization: Accept / Object / Review (needs partner attention)
- For objected exceptions, Sara specifies exact cure action required (e.g., "Release this mortgage," "Obtain subordination agreement")
- Input: title commitment required; PSA, survey, and other docs optional but Sara uses them if provided to cross-reference
- Objection deadline extracted from PSA when available
- Standard/boilerplate exceptions accepted in the letter, discussed briefly in the client memo
- Output: docx letter file

#### Title Summary Memo
- Client-facing title summary memo produced alongside the objection letter
- Covers: insured amount, policy type, vesting, all exceptions with Accept/Object/Review categorization, recommended actions
- Standard exceptions discussed briefly here (even though accepted in the letter)
- Output: separate docx file

#### Closing Documents
- Document types: deed, assignment and assumption, estoppel certificate, escrow holdback agreement -- all to the extent called for in the PSA
- Sara drafts from scratch (no template required)
- State-specific if the user specifies the jurisdiction; Sara adjusts for that state's requirements (deed formalities, transfer tax language, etc.)
- Cover note flags: provisions requiring partner review, deal-specific insertions needing verification, provisions Sara couldn't populate from available documents
- Separate files per document type (deed.docx, assignment.docx, etc.)
- Estoppels batched -- all tenants produced in one pass
- Deal-specific file naming (e.g., deed-123-main-st.docx, estoppel-tenant-abc.docx)

#### Workflow Interaction Model
- Simpler interaction than PSA reviews -- Sara asks only what she can't infer from documents (representation, state/jurisdiction)
- Representation: Sara infers from context, confirms only if ambiguous
- Milestone check-ins at natural checkpoints (e.g., "I've extracted these deadlines -- correct?") before generating final docs
- Gaps: Sara flags and continues with placeholders (e.g., [CLOSING DATE]) rather than blocking on missing info; gaps listed in cover note
- Proactive issue flagging: Sara notes concerning provisions she spots while extracting deal terms, included in cover note
- Document styling: match input document style (fonts, formatting) rather than imposing Sara's own style
- Subagent delegation: Claude's discretion on whether delegation improves quality for these workflows

#### Deal Context Persistence (SARA.md)
- Sara saves deal context to a SARA.md file in the project directory
- Contains: deal summary, key terms, parties, property, purchase price, key dates, representation, extracted provisions
- Also contains: full work product log -- what Sara has produced (checklist on X date, title letter on Y date) and issues flagged
- Sara reads SARA.md on subsequent workflows to understand background without re-reading source documents
- Accumulates across the deal lifecycle (PSA review -> title objection -> closing docs)

### Claude's Discretion
- Whether to delegate deal workflow tasks to subagents or handle directly
- Internal structure of SARA.md
- Exact milestone check-in points
- How to handle documents Sara encounters but wasn't specifically asked about

### Deferred Ideas (OUT OF SCOPE)
- Feedback/calibration mode -- user can enter feedback mode, tell Sara how to adjust her work, and the feedback persists to Sara's system instructions. Applies to all Sara workflows, not just deal workflows. Capture as a separate enhancement phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DEAL-01 | Sara can generate a closing checklist and deal calendar from a finalized PSA | Closing checklist workflow defined with PSA-to-checklist extraction pattern, responsible-party categorization (buyer/seller/escrow/lender), deadline population from contract provisions, template-driven docx output with table support, .ics calendar generation for key milestones; enhanced write_docx provides table rendering; SARA.md captures extracted deal context for reuse |
| DEAL-02 | Sara can draft title objection letters based on title commitment review | Title objection letter workflow defined with Schedule B-II exception analysis, three-bucket categorization (Accept/Object/Review), cure action specification for objections, template-driven docx letter output; title summary memo as companion deliverable with insured amount, policy type, vesting, and exception analysis; cross-references to PSA/survey when provided |
| DEAL-03 | Sara can draft standard closing and deal documents from a finalized PSA -- including deeds, assignments, estoppels, escrow holdback agreements, and other closing deliverables a senior RE associate would prepare | Closing document drafting workflow defined with document type templates (deed, assignment and assumption, estoppel certificate, escrow holdback agreement), deal-term extraction from PSA/SARA.md, jurisdiction-specific adjustments, cover note with partner review flags, placeholder handling for missing information; separate files per document with deal-specific naming |
</phase_requirements>

## Standard Stack

### Core (Existing -- No Changes)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| python-docx | 1.2.0 | Read, write, and manipulate Word documents | Installed; used by all 6 docx tools |
| diff-match-patch | 20200713+ | Text diffing for redline generation | Installed; used by redliner.py |
| lxml | (bundled) | XML manipulation for Word document internals | Installed; used by reader.py and redliner.py |
| mcp | 1.0.0+ | FastMCP server for tool exposure | Installed; used by mcp_server.py |

### Core (Enhancements Needed)

| Component | Current | Enhancement | Why |
|-----------|---------|-------------|-----|
| `docx-tools/core/writer.py` | Handles headings, paragraphs, bold/italic | Add table rendering from structured data; add numbered/bulleted list support; improve template style matching | Closing checklists require multi-column tables with header rows; closing documents require numbered provisions |
| `docx-tools/mcp_server.py` | 6 tools exposed | Add `generate_ics` tool (or keep as utility Sara calls via bash) | Deal calendar requires .ics output |

### New (Small Additions)

| Component | Purpose | Complexity |
|-----------|---------|------------|
| `docx-tools/core/calendar_writer.py` | Generate .ics files with multi-VEVENT format | ~50-80 lines; pure text generation conforming to RFC 5545 |

### Dependency Decision: icalendar Library

**Option A: Add `icalendar` library (pip install icalendar)**
- Pros: Well-maintained Python library, handles edge cases (timezones, escaping), RFC 5545 compliant
- Cons: New dependency for a simple task; library is ~6.1.x currently

**Option B: Generate .ics text directly (no new dependency)**
- Pros: Zero dependencies; .ics format for date-only events (no timezone complexity) is trivially simple; the multi-VEVENT format is just concatenated VEVENT blocks within a VCALENDAR wrapper
- Cons: Must handle text escaping manually; no library support for edge cases

**Recommendation: Option B.** The deal calendar contains 4-8 date-only milestone events (DD expiry, title objection deadline, closing date, post-closing deadlines). The .ics format for this use case is:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sara AI Associate//Deal Calendar//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260415
DTEND;VALUE=DATE:20260416
SUMMARY:Due Diligence Period Expires
DESCRIPTION:PSA Section 4.1 -- 45-day DD period from effective date
UID:sara-deal-dd-expiry-20260415@ai-associate
END:VEVENT
BEGIN:VEVENT
...
END:VEVENT
END:VCALENDAR
```

This is simple enough to generate without a library. A `calendar_writer.py` utility of ~50-80 lines handles it cleanly. If timezone-aware events or recurring events are needed later, the library can be added.

**Confidence:** HIGH. The .ics format is well-documented (RFC 5545) and the use case is simple date-only events. Verified against Outlook import requirements.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Enhanced write_docx for tables | python-docx-template (Jinja2 templates in docx) | More powerful templating but adds a dependency and changes the workflow pattern; write_docx enhancement is simpler and consistent with existing architecture |
| Direct .ics text generation | icalendar library | Library handles edge cases automatically but adds a dependency for a trivial use case |
| Separate calendar utility | Inline .ics generation in Sara's workflow | Separate utility is testable and reusable; inline generation is simpler but untestable |

## Architecture Patterns

### Recommended Project Structure After Phase 3

```
skills/sara/
├── SKILL.md                           # MODIFIED: deal workflow references, SARA.md persistence, simpler interaction model for deal workflows
└── references/
    ├── contract-review-workflow.md     # UNCHANGED
    ├── delegation-model.md            # UNCHANGED (or minor: drafter template additions)
    ├── work-product-standards.md      # MODIFIED: closing checklist, title letter, closing document standards
    ├── deal-workflows.md              # NEW: closing checklist, title objection, closing document workflows
    ├── re-checklist-psa.md            # UNCHANGED
    ├── clause-library.md              # UNCHANGED
    └── market-standards.md            # UNCHANGED

agents/
├── document-reviewer.md              # UNCHANGED
├── document-drafter.md               # MODIFIED: deal document drafting patterns (closing docs, letters)
├── contract-reviser.md               # UNCHANGED
└── legal-researcher.md               # UNCHANGED (or minor: title research patterns)

docx-tools/
├── core/
│   ├── writer.py                     # MODIFIED: table rendering, list support
│   ├── calendar_writer.py            # NEW: .ics file generation
│   ├── reader.py                     # UNCHANGED
│   ├── redliner.py                   # UNCHANGED
│   ├── comparer.py                   # UNCHANGED
│   ├── extractor.py                  # UNCHANGED
│   └── analyzer.py                   # UNCHANGED
├── cli/
│   └── calendar.py                   # NEW: CLI wrapper for calendar_writer
├── mcp_server.py                     # MODIFIED: expose generate_ics tool (optional)
└── tests/
    ├── test_writer.py                # MODIFIED: table rendering tests
    └── test_calendar_writer.py       # NEW: calendar generation tests
```

### Pattern 1: Deal Workflow Reference File (deal-workflows.md)

**What:** A single reference file defining all three deal workflows (closing checklist, title objection, closing documents) that Sara loads when she receives a deal workflow assignment. Analogous to how `contract-review-workflow.md` defines the PSA review process.

**Design rationale:** Each workflow is simpler than the contract review workflow (fewer steps, less delegation). They share common patterns: read source documents, extract deal terms, check-in with partner, generate output documents. A single reference file keeps them together since they operate on the same deal.

**Structure:**

```markdown
# Deal Workflows

## Common Patterns
- Reading SARA.md for deal context
- Placeholder handling ([CLOSING DATE], [PURCHASE PRICE])
- Cover note generation
- File naming conventions
- Style matching from templates

## Workflow 1: Closing Checklist from PSA
### Step 1: Read PSA and Extract Deal Terms
### Step 2: Build Checklist Items by Responsible Party
### Step 3: Milestone Check-in (deadline verification)
### Step 4: Generate Checklist Docx and Calendar .ics
### Step 5: Update SARA.md

## Workflow 2: Title Objection Letter from Title Commitment
### Step 1: Read Title Commitment and Extract Exceptions
### Step 2: Categorize Exceptions (Accept / Object / Review)
### Step 3: Cross-Reference with PSA/Survey (if available)
### Step 4: Milestone Check-in (exception categorization review)
### Step 5: Generate Objection Letter and Summary Memo
### Step 6: Update SARA.md

## Workflow 3: Closing Documents from PSA
### Step 1: Read PSA/SARA.md and Identify Required Documents
### Step 2: Extract Deal Terms for Each Document
### Step 3: Milestone Check-in (document list and key terms)
### Step 4: Draft Each Document
### Step 5: Generate Cover Note
### Step 6: Update SARA.md
```

**Confidence:** HIGH. This follows the same reference file pattern established in Phase 1 with contract-review-workflow.md.

### Pattern 2: SARA.md Deal Context Persistence

**What:** Sara reads and writes a `SARA.md` file in the project directory that accumulates deal context across workflow invocations.

**Recommended structure:**

```markdown
# [Property Name / Deal Name]

## Deal Summary
- **Property:** [Address/description]
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
| Effective Date | [date] | Preamble | -- |
| DD Period Expiry | [date] | Section 4.1 | Pending |
| Title Objection Deadline | [date] | Section 5.2 | Pending |
| Closing Date | [date] | Section 6.1 | Pending |

## Extracted Provisions
### Deposit
- Amount: $[amount]
- Escrow agent: [name]
- Goes hard: [trigger]
### [Other key provisions as extracted]

## Work Product Log
| Date | Workflow | Output Files | Notes |
|------|----------|-------------|-------|
| [date] | PSA Review | redline-psa.docx, transmittal-package.md | Level 4, 42 revisions |
| [date] | Closing Checklist | checklist-123-main.docx, calendar-123-main.ics | 28 items, 4 milestones |
| [date] | Title Objection | objection-letter.docx, title-memo.docx | 3 objections, 5 accepted, 2 review |

## Issues Flagged
- [date] [workflow]: [issue description]
```

**How Sara uses it:**
1. **On first workflow:** Sara creates SARA.md from the PSA (or whatever is the first source document)
2. **On subsequent workflows:** Sara reads SARA.md first, then reads any new source documents. SARA.md provides background without re-reading the full PSA
3. **After each workflow:** Sara appends to the Work Product Log and Issues Flagged sections
4. **Accumulation:** The file grows across the deal lifecycle. By closing, it is a complete record of everything Sara has done on the deal

**Confidence:** HIGH. This is a simple markdown file read/write pattern. Sara already reads and writes markdown files extensively during contract review.

### Pattern 3: Template-Driven Document Generation

**What:** For the closing checklist and title objection letter, Sara uses a user-provided docx template to match the output style (fonts, formatting, margins) to the user's preferences.

**Implementation approach:**

The existing `write_docx` function already supports this:
```python
write_docx(content, output_path, template_path="user-template.docx")
```

When a template is provided, `write_docx` opens the template, clears its content (preserving styles), and renders new content using the template's style definitions. This means:
- Font family, size, and spacing come from the template's Normal style
- Heading styles come from the template's Heading 1/2/3 styles
- Table styles come from the template's default table style
- Margins and page layout come from the template's section properties

**For checklist tables specifically:** The enhanced `write_docx` needs to:
1. Accept structured table data (headers + rows)
2. Render using python-docx `document.add_table()` with the template's table style
3. Apply header row formatting (bold, background shading)
4. Set column widths appropriate to content type

**For closing documents (no template):** Sara drafts from scratch using `write_docx` with no template. The default styles (Times New Roman 12pt, standard margins) are appropriate for legal documents. If the user specifies a jurisdiction, Sara adjusts the deed formalities (e.g., different witness/notary blocks for different states).

**Confidence:** HIGH. python-docx 1.2.0 has robust table API (add_table, add_row, cell formatting). Template style inheritance via Document(template_path) is well-documented and already implemented in writer.py.

### Pattern 4: Closing Document Drafting from Deal Terms

**What:** Sara extracts deal terms from the PSA (or SARA.md) and populates closing document drafts with those terms, leaving placeholders for information she cannot determine.

**Document type patterns:**

**Deed (Special Warranty Deed -- standard for commercial RE):**
- Grantor/Grantee from PSA parties
- Property description (legal description from PSA exhibits)
- Consideration from purchase price
- Warranty covenants (limited to grantor's period of ownership)
- Subject to permitted exceptions (from PSA definition)
- State-specific: witness blocks, notary jurat, transfer tax language, recording information
- Sara flags: jurisdiction requirements she cannot verify, unusual permitted exceptions

**Assignment and Assumption of Leases:**
- Assignor/Assignee from PSA parties
- Property description
- Effective date (closing date)
- Lease schedule (from PSA exhibits or tenant information)
- Assumption of obligations
- Indemnification for pre/post-closing breaches
- Sara flags: lease schedules that need verification, any leases requiring consent

**Estoppel Certificate:**
- Landlord name (buyer, post-closing)
- Tenant name (from PSA lease schedule)
- Lease date and term
- Current rent, security deposit, prepaid rent
- Defaults and claims
- Options (renewal, expansion, purchase)
- Sara produces one per tenant from PSA lease information, batched into a single pass
- Sara flags: information she cannot extract from available documents

**Escrow Holdback Agreement:**
- Parties (buyer, seller, escrow agent)
- Holdback amount and purpose
- Release conditions
- Timeline for completion
- Default provisions
- Sara flags: holdback triggers she cannot determine from PSA alone

**Confidence:** HIGH for the drafting pattern; MEDIUM for state-specific formalities (Sara must disclose that jurisdiction-specific provisions require partner verification -- this is already a locked decision from the phase context).

### Pattern 5: Subagent Delegation Recommendation

**What:** Claude's discretion item -- whether to delegate deal workflow tasks to subagents.

**Recommendation: Minimal delegation for deal workflows.** Here is the reasoning:

1. **Contract review** benefits from delegation because it involves hundreds of paragraphs with independent dispositions. Batch processing is necessary.
2. **Deal workflows** involve extraction (reading a PSA and pulling out dates, parties, terms) followed by generation (writing a checklist, letter, or document). These are sequential, not parallelizable.
3. **Document-drafter** is useful for assembling multi-section closing documents from Sara's extracted deal terms -- particularly for the closing document workflow (DEAL-03) where Sara needs to produce 4+ separate documents.
4. **Legal-researcher** may be useful for jurisdiction-specific closing document requirements (deed formalities, transfer tax rules) if Sara's knowledge is insufficient.

**Recommended delegation pattern:**
- Closing checklist: Sara handles directly (extraction + generation is one coherent flow)
- Title objection: Sara handles directly (analysis of exceptions requires Sara's judgment throughout)
- Closing documents: Sara extracts deal terms, then delegates individual document drafting to document-drafter with precise specifications; Sara reviews each draft before finalizing

**Confidence:** MEDIUM. This is a judgment call. The planner can adjust based on early testing.

### Anti-Patterns to Avoid

- **Separate reference files per workflow:** All three workflows share deal context patterns (SARA.md, placeholder handling, cover notes). One reference file keeps them cohesive and avoids duplication.

- **Over-engineering the checklist generator:** The checklist is a table in a Word document. Sara reads the PSA, extracts deadlines and responsible parties, and writes a table. Do not build a complex checklist engine -- Sara's legal judgment drives the content, `write_docx` with table support renders the output.

- **Template-dependent workflows:** The user provides templates optionally. If no template is provided, Sara uses sensible defaults. The workflows must work without templates. Template matching is a quality enhancement, not a hard requirement.

- **Blocking on missing information:** The user decided Sara should continue with placeholders rather than blocking. Every workflow must handle incomplete data gracefully -- placeholders in the document, gaps listed in the cover note.

- **Drafting closing documents from templates:** The user decided Sara drafts closing documents from scratch (no template). Do not create pre-built document templates for deeds, assignments, etc. Sara generates these from her legal knowledge plus extracted deal terms.

- **Complex dependency tracking in checklists:** The user decided dependencies are flagged in the notes column, not a formal dependency graph. Do not build dependency tracking logic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Word table generation | Custom XML table construction | python-docx `add_table()` API | python-docx handles all table XML, row/column management, cell merging, and style application |
| .ics calendar format | Ad-hoc string concatenation | Structured `calendar_writer.py` utility with proper RFC 5545 escaping | Even without the icalendar library, the utility should handle text escaping (commas, semicolons, newlines in descriptions) correctly |
| Template style matching | Manual XML style copying | python-docx `Document(template_path)` constructor | Opening a template and clearing content preserves all styles, margins, and page layout automatically |
| Deal term extraction from PSA | Custom PSA parser | Existing `read_docx` + `extract_structure` | The existing tools parse paragraphs with IDs, sections, and defined terms -- exactly what Sara needs to find deadlines and provisions |
| Jurisdiction-specific deed formalities | Hard-coded state templates | Sara's LLM knowledge + cover note disclosure | Sara knows deed formalities for all US states; cover note explicitly flags that jurisdiction-specific provisions require partner verification |

**Key insight:** The deal workflows are primarily behavioral specifications, not infrastructure builds. Sara's legal knowledge drives the analysis; the tools just need to read source documents and write output documents. The most complex new tooling is table rendering in `write_docx` -- everything else is prompt engineering.

## Common Pitfalls

### Pitfall 1: Checklist Items Too Generic

**What goes wrong:** Sara generates checklist items like "Obtain title insurance" or "Complete due diligence" -- generic entries that any Google search would produce. A partner expects deal-specific entries tied to specific PSA provisions.

**Why it happens:** Sara generates from general knowledge rather than extracting from the actual PSA. The checklist becomes a template, not a deal tool.

**How to avoid:** The workflow must explicitly instruct Sara to extract checklist items from specific PSA provisions. Every checklist item must have a PSA section reference. The milestone check-in after extraction should show the partner the specific deadlines and responsible parties Sara found in the PSA, not a generic list.

**Warning signs:** Checklist items do not have PSA section references. Multiple checklist items are identical across different PSAs. The checklist has fewer than 15 items for a standard PSA.

### Pitfall 2: Title Exception Analysis Too Shallow

**What goes wrong:** Sara categorizes all exceptions as either "Accept" or "Object" without analyzing what each exception actually is. Standard exceptions (survey exceptions, rights of tenants, utility easements) get the same treatment as problematic exceptions (open mortgages, judgment liens, tax liens).

**Why it happens:** Title commitments contain many exceptions. Without guidance, Sara may not distinguish between boilerplate Schedule B-I requirements and substantive Schedule B-II exceptions.

**How to avoid:** The workflow must instruct Sara to: (1) separate Schedule B-I (requirements to be satisfied before closing) from Schedule B-II (exceptions to coverage); (2) identify standard/boilerplate exceptions and accept them in the letter while discussing them briefly in the memo; (3) for each non-standard exception, specify the exact cure action required. The three-bucket categorization (Accept/Object/Review) forces Sara to make a judgment call on every exception.

**Warning signs:** All exceptions are categorized identically. No cure actions are specified for objected exceptions. The summary memo does not discuss standard exceptions at all.

### Pitfall 3: Closing Documents Miss Deal-Specific Terms

**What goes wrong:** Sara produces a deed that looks like a form -- correct structure but no deal-specific content. The property description is a placeholder, the consideration is "[PURCHASE PRICE]", and the permitted exceptions reference is generic.

**Why it happens:** Sara generates from a legal knowledge pattern rather than extracting and populating from the actual PSA. The closing documents are disconnected from the deal.

**How to avoid:** The workflow must instruct Sara to populate every deal-specific field from the PSA or SARA.md before generating the document. The cover note must explicitly list every placeholder that could not be populated and every provision that was populated but needs verification. SARA.md provides the bridge -- if Sara did a PSA review first, the key terms are already extracted.

**Warning signs:** Cover note does not list any verification items. Documents contain generic rather than deal-specific language. Property description is a placeholder when the PSA contains a legal description exhibit.

### Pitfall 4: SARA.md Becomes Stale or Inconsistent

**What goes wrong:** Sara writes deal context to SARA.md during the first workflow but never updates it. Later workflows read stale information. Or Sara overwrites SARA.md instead of appending, losing the work product log.

**Why it happens:** No clear protocol for when Sara reads vs. writes SARA.md, or whether she appends vs. overwrites.

**How to avoid:** Define explicit SARA.md update rules in the workflow: (1) Sara always reads SARA.md at the start of any deal workflow; (2) Sara always appends to the Work Product Log and Issues Flagged sections after completing a workflow; (3) Sara updates the Deal Summary and Key Dates sections only when new information supersedes existing information; (4) Sara never deletes existing entries from the Work Product Log.

**Warning signs:** SARA.md has only one Work Product Log entry after multiple workflows. Key Dates section does not match the latest PSA amendment. Sara re-reads the full PSA on every workflow instead of using SARA.md.

### Pitfall 5: Style Mismatch Between Template and Content

**What goes wrong:** Sara generates a closing checklist using the user's template, but the table formatting does not match the template's style. Fonts are wrong, table borders are different, or header formatting is inconsistent.

**Why it happens:** python-docx's template style inheritance works for paragraph and heading styles but requires explicit table style application. If `write_docx` does not apply the template's table style to the generated table, the table uses python-docx defaults.

**How to avoid:** The enhanced `write_docx` must: (1) detect available table styles in the template document; (2) apply the template's default or first table style to generated tables; (3) if no table style exists in the template, use a sensible built-in style ("Table Grid" or "Light Shading"). Test with actual user templates to verify style inheritance works correctly.

**Warning signs:** Tables in the output have no borders when the template uses bordered tables. Font in table cells differs from paragraph font. Header row is not visually distinct.

### Pitfall 6: Closing Document Cover Note is an Afterthought

**What goes wrong:** Sara produces the closing documents but the cover note is a generic "here are the documents" message. It does not identify which provisions need partner review, which insertions need verification, or which fields Sara could not populate.

**Why it happens:** The cover note is generated last, after Sara has moved on to the next document. The connection between "what Sara could not determine" and "what the cover note says" is lost.

**How to avoid:** Sara must track verification items and unfilled fields as she drafts each document, not after. The workflow should instruct Sara to maintain a running list of cover note items during drafting, then compile them into the cover note at the end. The cover note structure should mirror the document list: one section per document with its specific review items.

**Warning signs:** Cover note does not mention any specific provisions by section reference. Cover note is fewer than 10 items for a set of 4+ closing documents. Cover note does not distinguish between "needs partner review" and "needs factual verification."

## Code Examples

### Example 1: Enhanced write_docx with Table Support

```python
# Source: python-docx 1.2.0 documentation (https://python-docx.readthedocs.io)
# Pattern for adding tables to write_docx

from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT

def _render_table(doc: Document, headers: list, rows: list, style: str = None):
    """Render a table from structured data.

    Args:
        doc: Document object to add table to.
        headers: List of header strings.
        rows: List of row lists (each row is a list of cell strings).
        style: Optional table style name.
    """
    table = doc.add_table(rows=1, cols=len(headers))
    if style:
        table.style = style
    else:
        # Sensible default
        try:
            table.style = 'Table Grid'
        except KeyError:
            pass  # Use document default if Table Grid unavailable

    # Header row
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        # Bold the header text
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.bold = True

    # Data rows
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, cell_text in enumerate(row_data):
            row_cells[i].text = str(cell_text)

    return table
```

**Confidence:** HIGH. Verified against python-docx 1.2.0 documentation.

### Example 2: .ics Calendar Generation (No External Library)

```python
# RFC 5545 compliant .ics generation for deal milestones
# Source: RFC 5545 (https://datatracker.ietf.org/doc/html/rfc5545)

import uuid
from datetime import date
from pathlib import Path
from typing import List, Dict


def generate_ics(
    events: List[Dict[str, str]],
    output_path: str,
    calendar_name: str = "Deal Calendar",
) -> str:
    """
    Generate an .ics file with multiple VEVENT entries.

    Args:
        events: List of dicts with keys: date (YYYY-MM-DD), summary, description.
        output_path: Path for the output .ics file.
        calendar_name: Display name for the calendar.

    Returns:
        The output file path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sara AI Associate//Deal Calendar//EN",
        f"X-WR-CALNAME:{_ics_escape(calendar_name)}",
    ]

    for event in events:
        dt = event["date"].replace("-", "")
        # For all-day events, DTEND is the day after
        dt_end = _next_day(event["date"]).replace("-", "")
        uid = f"sara-{uuid.uuid4().hex[:12]}@ai-associate"

        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt}",
            f"DTEND;VALUE=DATE:{dt_end}",
            f"SUMMARY:{_ics_escape(event['summary'])}",
            f"DESCRIPTION:{_ics_escape(event.get('description', ''))}",
            f"UID:{uid}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")

    return str(output_path)


def _ics_escape(text: str) -> str:
    """Escape special characters per RFC 5545."""
    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def _next_day(date_str: str) -> str:
    """Return the next day for all-day event DTEND."""
    from datetime import datetime, timedelta
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return (dt + timedelta(days=1)).strftime("%Y-%m-%d")
```

**Confidence:** HIGH. The .ics format for all-day events is well-documented. The multi-VEVENT format is standard and imports correctly into Outlook with a single file.

### Example 3: SARA.md Read/Write Pattern

```markdown
# Sara's SARA.md interaction pattern (behavioral specification)

## Reading SARA.md
At the start of any deal workflow:
1. Check if SARA.md exists in the project directory
2. If yes: read it and extract deal context (parties, property, dates, representation)
3. If no: proceed without context; create SARA.md after extracting deal terms from source documents

## Writing SARA.md
After completing any deal workflow:
1. Read current SARA.md (or start fresh if it does not exist)
2. Update Deal Summary section if new information is available
3. Update Key Dates section if new dates were extracted or confirmed
4. Append to Work Product Log: date, workflow type, output files, notes
5. Append to Issues Flagged: any new issues identified during this workflow
6. Write the updated SARA.md back to disk

## SARA.md Location
SARA.md lives in the project root directory (same level as Sara-Work-Product/).
Sara checks for it at: `./SARA.md`
```

**Confidence:** HIGH. This is a behavioral specification using existing Read/Write tools. No new infrastructure needed.

### Example 4: Closing Checklist Table Structure

```markdown
# What Sara generates for the closing checklist
# This is the structured data that feeds into write_docx with table support

## Key Dates (embedded at top of checklist)

| Milestone | Date | PSA Reference |
|-----------|------|---------------|
| Effective Date | March 1, 2026 | Preamble |
| DD Period Expiry | April 15, 2026 | Section 4.1 |
| Title Objection Deadline | April 22, 2026 | Section 5.2 |
| Closing Date | May 30, 2026 | Section 6.1 |
| Post-Closing Adjustment Deadline | July 29, 2026 | Section 8.4(d) |

## Checklist Items by Responsible Party

### Buyer Responsibilities

| # | Item | Deadline | PSA Ref | Status | Notes |
|---|------|----------|---------|--------|-------|
| 1 | Complete physical inspections | Apr 15 | 4.1 | Pending | Depends on property access |
| 2 | Deliver title objection letter | Apr 22 | 5.2 | Pending | Depends on title commitment receipt |
| 3 | Deliver additional deposit | Apr 16 | 3.2 | Pending | $250,000; goes hard after DD period |
| ... | | | | | |

### Seller Responsibilities

| # | Item | Deadline | PSA Ref | Status | Notes |
|---|------|----------|---------|--------|-------|
| 1 | Deliver title commitment | Mar 15 | 5.1 | Pending | |
| 2 | Deliver survey | Mar 15 | 5.1(b) | Pending | |
| 3 | Deliver tenant estoppels | May 15 | 8.5 | Pending | Required from all tenants >5,000 SF |
| ... | | | | | |

### Escrow/Title Company

| # | Item | Deadline | PSA Ref | Status | Notes |
|---|------|----------|---------|--------|-------|
| 1 | Issue title commitment | Mar 15 | 5.1 | Pending | |
| 2 | Issue pro forma title policy | May 25 | 5.4 | Pending | Depends on cure of objections |
| ... | | | | | |
```

**Confidence:** HIGH. This matches the user's locked decision for checklist structure (item + deadline + responsible party + PSA reference + status + notes + dependency flags in notes).

## State of the Art

| Current (No Deal Workflows) | After Phase 3 | Impact |
|------------------------------|---------------|--------|
| Sara can only review contracts (PSA markup) | Sara handles the full closing phase: checklist, title objection, closing documents | Complete deal lifecycle coverage from PSA review through closing |
| No deal context persistence | SARA.md accumulates deal context across workflows | Sara understands deal background without re-reading source documents; work product log tracks everything she has done |
| write_docx produces paragraphs only | write_docx produces paragraphs and tables | Professional checklist output with structured tabular data |
| No calendar output | .ics calendar file with key deal milestones | One-click import into Outlook for deadline tracking |
| Sara requires extensive instruction for each workflow | Simpler interaction model with smart inference from documents | Faster workflow execution; Sara asks only what she cannot determine from the documents |
| No title analysis capability | Title commitment analysis with three-bucket exception categorization | Sara can review Schedule B-II exceptions and draft objection letters with specific cure actions |
| No document drafting from deal terms | Sara drafts deeds, assignments, estoppels, holdbacks from PSA terms | Closing documents populated with deal-specific terms, with cover note flagging items for partner review |

## Open Questions

1. **Table style inheritance from templates**
   - What we know: python-docx `Document(template_path)` preserves styles when content is cleared. Table styles are separate from paragraph styles and must be explicitly applied. The template may or may not contain table styles.
   - What's unclear: Whether the existing `write_docx` template flow correctly propagates table styles, or whether the table will always use the default "Table Grid" regardless of template.
   - Recommendation: During implementation, test with an actual user-provided template. If table styles do not propagate, add explicit table style detection: check `doc.styles` for table styles and apply the first available one. Flag this as a testing item in the plan.

2. **Estoppel batching -- all tenants in one pass**
   - What we know: The user decided estoppels should be batched -- all tenants produced in one pass. Each estoppel is a separate file with deal-specific naming.
   - What's unclear: Whether Sara should produce one combined estoppel document (with page breaks between tenants) or truly separate files per tenant. The decision says "separate files per document type" and "batched" -- these could mean one pass producing multiple files.
   - Recommendation: Produce separate files per tenant (e.g., estoppel-tenant-abc.docx, estoppel-tenant-xyz.docx). "Batched" means Sara processes all tenants together for efficiency, not that they are combined into one file. This matches the "deal-specific file naming" decision.

3. **Closing document drafting quality without templates**
   - What we know: Sara drafts closing documents from scratch (no template required). Sara uses LLM knowledge for document structure and content. State-specific adjustments are based on Sara's legal knowledge.
   - What's unclear: Whether Sara's LLM knowledge of deed formalities, assignment structures, and estoppel formats is sufficient for partner-ready output, or whether the first few iterations will require significant partner corrections.
   - Recommendation: Accept that first-generation closing documents will need partner review. The cover note explicitly flags jurisdiction-specific provisions for verification. Over time, the user may develop templates from Sara's output, creating a feedback loop. This is consistent with the Phase 3 blocker noted in STATE.md: "Closing document templates need jurisdiction-specific review before production use."

4. **write_docx enhancement scope**
   - What we know: The current writer handles headings, paragraphs, bold, and italic. Closing checklists need tables. Closing documents need numbered lists (for deed covenants, contract provisions).
   - What's unclear: Whether to add a full markdown-to-docx parser (handling tables, ordered lists, unordered lists, nested lists) or a more targeted enhancement (table rendering from structured data + basic numbered list support).
   - Recommendation: Targeted enhancement. Add two capabilities: (1) `_render_table()` function that takes structured data (headers + rows) and produces a docx table; (2) recognition of markdown ordered lists (`1. item`) and unordered lists (`- item`) in the existing `_render_markdown_to_docx()` function. Do not attempt full markdown parsing -- it is a rabbit hole. Sara generates the content; the writer renders it. Keep the interface simple.

5. **Whether to expose generate_ics via MCP**
   - What we know: The .ics generator is a simple utility. Sara can call it via bash (CLI) or it could be exposed as an MCP tool.
   - What's unclear: Whether the overhead of MCP tool registration is worth it for a tool that will be called once per deal.
   - Recommendation: Start with CLI only (`python docx-tools/cli/calendar.py`). If Sara's workflow benefits from direct tool access, add MCP exposure later. The tool is simple enough that bash invocation works fine.

## Sources

### Primary (HIGH confidence)
- `/home/david/projects/AI-Associate/skills/sara/SKILL.md` -- Sara's complete behavioral framework; defines interaction model, delegation patterns, and work product standards that deal workflows must integrate with
- `/home/david/projects/AI-Associate/skills/sara/references/contract-review-workflow.md` -- Existing 7-step workflow pattern that deal workflows follow analogously
- `/home/david/projects/AI-Associate/skills/sara/references/work-product-standards.md` -- Document type formatting standards; closing documents, letters, and memos must follow these conventions
- `/home/david/projects/AI-Associate/skills/sara/references/delegation-model.md` -- Delegation briefing templates; document-drafter template used for closing document drafting
- `/home/david/projects/AI-Associate/agents/document-drafter.md` -- Current drafter agent definition; needs enhancement for deal document patterns
- `/home/david/projects/AI-Associate/docx-tools/core/writer.py` -- Current write_docx implementation; confirms template support exists, table rendering is the gap
- `/home/david/projects/AI-Associate/docx-tools/mcp_server.py` -- Current MCP tool exposure; 6 tools, no calendar tool yet
- `/home/david/projects/AI-Associate/docx-tools/pyproject.toml` -- Current dependencies; icalendar is NOT installed, confirming need for custom .ics generation
- `/home/david/projects/AI-Associate/.planning/phases/03-deal-workflows/03-CONTEXT.md` -- User decisions and locked constraints for Phase 3
- `/home/david/projects/AI-Associate/.planning/REQUIREMENTS.md` -- DEAL-01, DEAL-02, DEAL-03 requirement definitions
- `/home/david/projects/AI-Associate/.planning/ROADMAP.md` -- Phase 3 description and success criteria

### Secondary (MEDIUM confidence)
- python-docx 1.2.0 documentation (Context7 verified) -- Table API: `add_table()`, `add_row()`, cell access, style application; template style inheritance via Document constructor
- RFC 5545 iCalendar specification -- .ics format for VCALENDAR/VEVENT; DATE value type for all-day events; text escaping rules
- icalendar Python library documentation (https://icalendar.readthedocs.io/) -- Verified API pattern for multi-VEVENT calendar files; confirmed our custom approach is sufficient for date-only events
- Blog post on creating iCalendar files in Python (https://blog.pesky.moe/posts/2025-01-02-create-icalendar/) -- Verified Calendar/Event creation pattern and Outlook import compatibility
- Commercial real estate closing checklist sources (https://agorareal.com/learn/commercial-real-estate-closing-checklist/, https://asrlawfirm.com/commercial-real-estate-closing-checklist/) -- Closing checklist category structure and responsible party patterns
- Title objection letter practice guides (https://bwpf-law.com/all-about-title-title-commitments-title-objection-letters-and-final-title-policies/) -- Schedule B-I vs B-II distinction, exception categorization patterns, cure action language
- Deed type analysis (https://www.legalnature.com/guides/what-type-of-deed-should-i-use-general-special-or-quit-claim-deed, https://www.reinhartlaw.com/) -- Special warranty deed standard for commercial RE; state formality requirements

### Tertiary (LOW confidence)
- Escrow holdback agreement structure (https://www.lawinsider.com/clause/escrow-holdback, https://www.pulgininorton.com/escrow-holdback-agreements.html) -- General structure confirmed but specific commercial RE provisions may vary by jurisdiction
- Estoppel certificate format -- Based on LLM legal knowledge; no specific authoritative source verified. Format is well-established in practice but may need partner verification for specific jurisdictions.

## Metadata

**Confidence breakdown:**
- Closing checklist workflow: HIGH -- Well-defined PSA-to-checklist extraction; write_docx table enhancement is straightforward python-docx API usage; .ics generation is simple
- Title objection workflow: HIGH -- Three-bucket categorization is a clear behavioral pattern; Schedule B-II analysis is standard title diligence; template-driven output uses existing write_docx
- Closing document workflow: MEDIUM-HIGH -- Document structures are well-known but state-specific formalities rely on Sara's LLM knowledge with explicit partner verification flag; cover note pattern is clear
- SARA.md persistence: HIGH -- Simple markdown read/write with defined update rules; no new infrastructure
- write_docx enhancement: HIGH -- python-docx table API is well-documented (Context7 verified); targeted enhancement scope is bounded
- .ics generation: HIGH -- RFC 5545 format for date-only events is trivial; no external library needed

**Research date:** 2026-02-18
**Valid until:** 2026-04-18 (60 days -- stable domain; behavioral specifications and python-docx API do not change with external dependencies)
