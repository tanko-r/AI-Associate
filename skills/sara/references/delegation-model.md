# Delegation Model -- Managing Subagent Attorneys

## Principles

Sara delegates like a skilled orchestrator: she gives precise instructions, sets explicit expectations, reviews work critically, and provides specific feedback. She does not do work a subagent could handle when her time is better spent on judgment and assembly, but she owns every deliverable that goes to the partner.

Delegation is not about offloading -- it is about leverage. Sara's value is in her analysis, judgment, and quality standards. Subagents handle execution under her direction.

## Mandatory Delegation Briefing Template (DLGT-01)

Every delegation Sara dispatches MUST use the briefing template below. No ad-hoc delegation prompts. The template ensures every subagent receives the context required to produce high-quality work on the first pass.

### Contract-Reviser Briefing Template

```markdown
## Delegation Briefing -- Contract Revision [Batch N of M]

**Matter:** [matter name]
**Representation:** [buyer/seller/tenant/etc.]
**Aggressiveness:** [1-5]
**Batch scope:** Paragraphs [p_X through p_Y] -- [Section description]

### Paragraphs in This Batch
[Full text of each paragraph with paragraph IDs]

### Disposition Table Entries for This Batch
[Reviewer's Section A entries filtered to this batch -- Para ID, Section Ref, Disposition, Reasoning, Market Assessment, Risk Severity for each paragraph]

### Risk Map Entries for This Batch
[Filtered Section B thematic risk entries matching paragraph IDs in this batch]

### Concept Map (Full)
[Complete concept map for cross-reference context]

### Document Outline
[Section headings with paragraph IDs for cross-reference verification]

### Defined Terms
[All defined terms from extract_structure]

### Prior Batch Changes (if batch > 1)
[Summary of revisions from prior batches that may affect this batch]

### Reference File Coverage
[Coverage status from Step 3-pre: which checklist categories have firm-specific content vs [TODO] placeholders, clause library and market standards population status -- enables correct application of † source markers]

### Output Requirements
- Save to: [path]
- Format: per contract-reviser output spec (REVISED/NO CHANGE/FLAG FOR SARA with full replacement paragraphs)
- Every paragraph in this batch must have an entry in your output
- Market rationale required for every REVISED entry
- Defined terms verified against Defined Terms list
- Conforming changes flagged for every revision
```

### Document-Reviewer Briefing Template

```markdown
## Delegation Briefing -- Document Review [Batch N of M]

**Matter:** [matter name]
**Representation:** [buyer/seller/tenant/etc.]
**Aggressiveness:** [1-5]
**Batch scope:** Paragraphs [p_X through p_Y] -- [Section description]

### Paragraphs in This Batch
[Full text of each paragraph with paragraph IDs]

### Analysis Framework
[Target concept list and target risk list from analysis-framework.md]

### Defined Terms
[All defined terms from extract_structure]

### Document Outline
[Section headings with paragraph IDs for cross-reference verification]

### Reference File Coverage
[Coverage status from Step 3-pre: which checklist categories have firm-specific content vs [TODO] placeholders, clause library and market standards population status -- enables correct application of † source markers]

### Output Requirements
- Save to: [path]
- Format: Section A (disposition table) + Section B (thematic risk map) + Section C (conforming changes)
- Every paragraph in this batch must have a row in Section A
- Market assessment required for every substantive provision
- Reasoning required for every disposition including Accept
```

### Legal-Researcher Briefing Template

```markdown
## Delegation Briefing -- Legal Research

**Matter:** [matter name]
**Representation:** [buyer/seller/tenant/etc.]
**Research type:** [framework-building / case-law / statutory / general]

### Research Question
[Specific, precisely framed question]

### Jurisdiction
[Applicable jurisdiction(s)]

### Context
[Relevant background: document type, deal structure, specific provisions at issue]

### Output Requirements
- Save to: [path]
- Format: [framework-building output / Question Presented + Short Answer + Analysis]
- [Any specific focus areas or authorities to address]
```

### Document-Drafter Briefing Template

```markdown
## Delegation Briefing -- Document Drafting

**Matter:** [matter name]
**Document type:** [memo / letter / agreement section / transmittal package]

### Instructions
[Specific instructions: what to draft, structure, audience, tone]

### Source Materials
[Files to reference: intake-notes.md, analysis-framework.md, disposition-table.md, risk-map.md]

### Context
[Relevant background for drafting]

### Output Requirements
- Save to: [path]
- Format: [markdown / docx / both]
- [Document-type-specific requirements]
```

### Closing Document Briefing Template (Document-Drafter)

```markdown
## Delegation Briefing -- Closing Document Drafting

**Matter:** [matter name]
**Document type:** [deed / assignment / estoppel / holdback]
**Jurisdiction:** [state, if applicable]

### Deal Terms
[Extracted deal terms relevant to this document: parties, property, purchase price, closing date, etc.]

### Document-Specific Terms
[Terms specific to this document type: permitted exceptions for deed, lease schedule for assignment, tenant info for estoppel, holdback terms for holdback]

### Jurisdiction Notes
[State-specific requirements Sara has identified, or "Use generic formalities -- jurisdiction TBD"]

### Output Requirements
- Save to: [path]
- File name: [deal-specific name per naming convention]
- Format: docx via write_docx
- Use [BRACKETED] placeholders for any information not provided
- Flag any provisions where you made assumptions: [NOTE: Assumed X because Y]
```

**Adaptation note:** Not every field applies to every delegation. The templates above are type-specific. But the required fields from DLGT-01 are always present where applicable: representation, aggressiveness (when relevant), target risk list or disposition entries (when applicable), paragraph IDs (when applicable), defined terms (when applicable), and explicit output format (always).

## Quality Loop Protocol (DLGT-02, DLGT-03)

The quality loop ensures every piece of subagent work meets Sara's standards before becoming part of a deliverable.

### Protocol Steps

1. **Dispatch**: Sara sends delegation using the briefing template. The delegation is logged to prompt-log.md before dispatching.

2. **Receive**: Subagent produces output and saves to the specified path.

3. **Review**: Sara reviews against the quality gate checklist (6 checks):
   - **Legal reasoning:** Is every revision or analysis legally sound?
   - **Drafting precision:** Is proposed language clean, specific, and properly structured?
   - **Cross-references:** Are all section references accurate? Do conforming changes in Section C cover all affected provisions?
   - **Market rationale:** Does every substantive revision cite market practice? Is the market assessment present for every provision?
   - **Defined terms:** Does proposed language use this agreement's defined terms consistently? No term substitutions?
   - **Coverage:** Are all paragraphs in the batch addressed? No gaps, no skipped paragraphs?

4. **Narrate**: Sara tells the partner what happened (brief summary, not a data dump):
   - "Received [agent]'s work on [batch description]. [Coverage: X of Y paragraphs]. [Key finding or quality assessment]. [Issue if any, or confirmation of quality]."

5. **Decision**:
   - **If deficient:** Send back with specific written feedback identifying each issue and what needs to change. Logged in full to prompt-log.md.
   - **If acceptable:** Incorporate into work product. Sara may make minor self-edits (style, tightening language).
   - **After 2 rounds:** Accept with self-edits or handle the task directly. Do not continue cycling.

6. **Always provide feedback**: Even on good first passes, Sara provides refinement feedback. This satisfies the substantive feedback requirement without artificial rejection. Refinement feedback examples:
   - "Tighten language in p_47 -- the carve-out clause is wordy"
   - "Add market rationale to the deposit change in p_15"
   - "Verify the cross-reference in p_63 -- I think it should be 7.2(b) not 7.2(a)"
   The subagent incorporates the refinements and Sara accepts on the next round.

### Iteration Limits

- **First attempt:** Briefing template with full context -- give the subagent everything needed to succeed
- **Second attempt (if needed):** Send back with specific written feedback referencing exact deficiencies. The feedback must identify each issue, explain what is wrong, and state what the corrected output should look like.
- **After 2 rounds:** Sara accepts with her own edits or handles the task directly. Two rounds of delegation costs less than three; beyond that, Sara's direct handling is more efficient.

## When to Delegate

### Delegate to `legal-researcher`:
- Targeted research on a specific legal question
- Pulling case law or statutory authority on a topic
- Researching the current state of law in a jurisdiction
- Framework-building research for Step 3 (analysis framework)
- Regulatory background research

### Delegate to `document-reviewer`:
- Paragraph-level review with disposition table output (Section A + B + C)
- Initial review of opposing counsel's documents
- Summarizing key terms of an agreement
- Comparing two versions of a document
- Identifying missing standard provisions

### Delegate to `contract-reviser`:
- Batched contract revision during redline preparation (Step 6)
- Receives paragraphs + disposition table entries + risk map entries + defined terms
- Returns full replacement paragraphs with market rationale and conforming changes flagged

### Delegate to `document-drafter`:
- First-pass drafts where Sara has clear instructions to give
- Standard-form documents (NDAs, engagement letters, simple amendments)
- Drafting sections of a larger document Sara is assembling
- Transmittal package assembly from Sara's analysis outputs
- Converting Sara's outline into a full draft
- Closing document drafting from Sara's extracted deal terms (deeds, assignments, estoppels, holdbacks)

### Do NOT delegate:
- High-judgment calls about strategy or risk
- Final review before delivering to the partner
- Communications with the partner
- Decisions about what to prioritize
- Novel or complex legal analysis (Sara handles these herself)
- Resolving conflicting dispositions or FLAG FOR SARA items

## Delegation Logging (DLGT-04)

Every delegation and review cycle is logged to `prompt-log.md`. This provides a complete audit trail of all subagent work.

### Prompt-Log Entry Format

```markdown
---
### [Timestamp] -- [Action Type]
**Direction:** Sara -> [agent name] | Sara reviewing [agent name] output
**Purpose:** [Brief description]

**Briefing sent:** (for delegations)
> [Full briefing text for first delegation of each type]
> [Summary with file reference for subsequent delegations of the same type]

**Output file:** [Path to results]

**Outcome:** (for reviews) SEND BACK | ACCEPTED
**Feedback given:** (for reviews)
> [Specific feedback -- always logged in full]

**Notes:** [Any additional context]
---
```

**Logging rules:**
- Log the full briefing text for the first delegation of each agent type in a matter
- Log a summary with file reference for subsequent delegations of the same type (e.g., "Same template as batch 1; batch scope updated to p_43 through p_84")
- Always log full review feedback, including refinement feedback on good work
- Log the outcome (SEND BACK or ACCEPTED) for every review round

## Assembling Multi-Source Work Product

For complex deliverables, Sara delegates different pieces to different subagents:

1. **Research** -> legal-researcher produces the legal analysis and framework inputs
2. **Review** -> document-reviewer produces the disposition table and risk map
3. **Revision** -> contract-reviser produces revised language in batches
4. **Assembly** -> document-drafter assembles the transmittal package from Sara's analysis outputs

Sara orchestrates the pieces into a coherent, polished deliverable that reflects her own judgment. She reviews every piece individually and layers on her analysis before assembly.

The final deliverable is Sara's -- not a collage of subagent outputs. Sara's cover note, risk calibration, and judgment calls are what make the package partner-ready.
