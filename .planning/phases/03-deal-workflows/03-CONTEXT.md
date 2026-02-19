# Phase 3: Deal Workflows - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Sara can handle the full closing phase of a deal: generating a closing checklist from a finalized PSA, drafting title objection letters from a title commitment, and drafting standard closing documents (deeds, assignments, estoppels, escrow holdback agreements). Each workflow is independently invokable and produces professional docx output.

</domain>

<decisions>
## Implementation Decisions

### Closing Checklist
- Template-driven: user provides a docx template, Sara adapts it to the deal
- Full detail per item: item + deadline + responsible party + PSA reference + status column (pending/received/waived) + notes column + dependency flags
- Dependencies flagged in notes column (not a formal dependency tracking system)
- Key dates section embedded at top of checklist (not a separate document)
- Single .ics calendar file with key milestone dates (DD expiry, title objection deadline, closing, post-closing) — multi-VEVENT format for single Outlook import
- Input: PSA only (other documents feed separate workflows)
- Output: docx file

### Title Objection Letter
- Template-driven: user provides a docx letter template, Sara adapts it
- Three-bucket exception categorization: Accept / Object / Review (needs partner attention)
- For objected exceptions, Sara specifies exact cure action required (e.g., "Release this mortgage," "Obtain subordination agreement")
- Input: title commitment required; PSA, survey, and other docs optional but Sara uses them if provided to cross-reference
- Objection deadline extracted from PSA when available
- Standard/boilerplate exceptions accepted in the letter, discussed briefly in the client memo
- Output: docx letter file

### Title Summary Memo
- Client-facing title summary memo produced alongside the objection letter
- Covers: insured amount, policy type, vesting, all exceptions with Accept/Object/Review categorization, recommended actions
- Standard exceptions discussed briefly here (even though accepted in the letter)
- Output: separate docx file

### Closing Documents
- Document types: deed, assignment and assumption, estoppel certificate, escrow holdback agreement — all to the extent called for in the PSA
- Sara drafts from scratch (no template required)
- State-specific if the user specifies the jurisdiction; Sara adjusts for that state's requirements (deed formalities, transfer tax language, etc.)
- Cover note flags: provisions requiring partner review, deal-specific insertions needing verification, provisions Sara couldn't populate from available documents
- Separate files per document type (deed.docx, assignment.docx, etc.)
- Estoppels batched — all tenants produced in one pass
- Deal-specific file naming (e.g., deed-123-main-st.docx, estoppel-tenant-abc.docx)

### Workflow Interaction Model
- Simpler interaction than PSA reviews — Sara asks only what she can't infer from documents (representation, state/jurisdiction)
- Representation: Sara infers from context, confirms only if ambiguous
- Milestone check-ins at natural checkpoints (e.g., "I've extracted these deadlines — correct?") before generating final docs
- Gaps: Sara flags and continues with placeholders (e.g., [CLOSING DATE]) rather than blocking on missing info; gaps listed in cover note
- Proactive issue flagging: Sara notes concerning provisions she spots while extracting deal terms, included in cover note
- Document styling: match input document style (fonts, formatting) rather than imposing Sara's own style
- Subagent delegation: Claude's discretion on whether delegation improves quality for these workflows

### Deal Context Persistence (SARA.md)
- Sara saves deal context to a SARA.md file in the project directory
- Contains: deal summary, key terms, parties, property, purchase price, key dates, representation, extracted provisions
- Also contains: full work product log — what Sara has produced (checklist on X date, title letter on Y date) and issues flagged
- Sara reads SARA.md on subsequent workflows to understand background without re-reading source documents
- Accumulates across the deal lifecycle (PSA review → title objection → closing docs)

### Claude's Discretion
- Whether to delegate deal workflow tasks to subagents or handle directly
- Internal structure of SARA.md
- Exact milestone check-in points
- How to handle documents Sara encounters but wasn't specifically asked about

</decisions>

<specifics>
## Specific Ideas

- .ics calendar file should contain key milestones in a single multi-VEVENT file for one-click Outlook import
- Title objection letter and title summary memo are two separate deliverables from one workflow
- Sara should match the styling of input documents rather than imposing her own formatting
- File naming should be deal-specific and descriptive

</specifics>

<deferred>
## Deferred Ideas

- Feedback/calibration mode — user can enter feedback mode, tell Sara how to adjust her work, and the feedback persists to Sara's system instructions. Applies to all Sara workflows, not just deal workflows. Capture as a separate enhancement phase.

</deferred>

---

*Phase: 03-deal-workflows*
*Context gathered: 2026-02-18*
