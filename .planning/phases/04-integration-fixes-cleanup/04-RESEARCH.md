# Phase 4: Integration Fixes & Cleanup - Research

**Researched:** 2026-02-19
**Domain:** Documentation integration, cross-reference consistency, tech debt cleanup
**Confidence:** HIGH

## Summary

Phase 4 is a gap closure phase -- no new features, no library changes, no architectural work. It addresses 3 integration gaps (INT-01, INT-02, INT-03) and 3 tech debt items identified by the v1.0 milestone audit. All 6 items are precise, surgical edits to existing markdown and Python files with clearly defined before/after states.

The integration gaps stem from cross-phase wiring issues: Phase 2 introduced the source marker convention (the `dagger` marker for reference file coverage) that requires subagents to know which reference files are populated vs placeholder, but the Phase 1 delegation briefing templates in `delegation-model.md` never added a field for Sara to communicate this information. Meanwhile, `work-product-standards.md` still references a stale root-level path for `contract-review-workflow.md`, and `deal-workflows.md` Workflow 3 mentions delegation without pointing to the specific briefing template.

The tech debt items are cosmetic: a stale untracked directory, a docstring filename typo, and a README skill name drift. All are trivial to fix but important for preventing confusion during future development.

**Primary recommendation:** Execute all 6 fixes in a single plan. Each fix is independent (no ordering dependencies), well-scoped (1-5 lines changed per fix), and has a clear verification condition. Total effort is approximately 30 minutes of editing.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DLGT-01 | Every subagent delegation includes representation, aggressiveness, target risk list, paragraph IDs, defined terms, and explicit output format | INT-01 fix adds "Reference File Coverage" field to Document-Reviewer and Contract-Reviser briefing templates, completing the briefing template's alignment with what agents expect |
| KNOW-01 | RE-specific PSA review checklist stub that Sara loads during framework building | INT-01 fix ensures the delegation briefing communicates checklist coverage status to subagents so they can apply source markers correctly |
| KNOW-02 | Clause library and market-standards stubs with correct structure | INT-01 fix ensures the delegation briefing communicates clause library and market standards coverage status to subagents |
| REVQ-05 | Sara delivers complete transmittal package for every contract review | INT-02 fix corrects the stale path reference in work-product-standards.md so Sara follows the canonical workflow (with Step 5.5, full delegation templates, transmittal format) |
| DEAL-03 | Sara can draft standard closing and deal documents from a finalized PSA | INT-03 fix adds explicit cross-reference from deal-workflows.md Workflow 3 to the Closing Document Briefing Template in delegation-model.md |
</phase_requirements>

## Standard Stack

Not applicable -- this phase modifies only markdown documentation files and a single Python docstring. No libraries, frameworks, or dependencies are involved.

## Architecture Patterns

### Files to Modify (6 edits across 5 files)

```
skills/sara/references/delegation-model.md     # INT-01: Add Reference File Coverage field (2 templates)
skills/sara/references/work-product-standards.md # INT-02: Fix stale path reference (line 257)
skills/sara/references/deal-workflows.md        # INT-03: Add briefing template cross-reference
docx-tools/cli/gen_calendar.py                  # Tech debt: Fix docstring filename
README.md                                       # Tech debt: Fix skill name
```

### Files/Directories to Delete (1 deletion)

```
references/                                     # Tech debt: Stale untracked directory (3 files)
  contract-review-workflow.md   (405 lines -- canonical is 555 lines)
  delegation-model.md           (94 lines -- canonical is 276 lines)
  work-product-standards.md     (82 lines -- canonical is 492 lines)
```

### Pattern: Cross-Reference Consistency

All integration fixes follow the same pattern: a file references a concept, path, or template that exists elsewhere, but the reference is missing, stale, or indirect. The fix is to add or update the reference so the pointing file correctly links to the pointed-to resource.

**Cross-reference format convention in this codebase:**
- Plugin-rooted paths use `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/...`
- Internal markdown references use relative descriptive text like "see delegation-model.md Closing Document Briefing Template"
- The codebase does NOT use markdown link syntax (`[text](url)`) for internal cross-references; it uses inline backtick paths or descriptive text

## Don't Hand-Roll

Not applicable -- this phase involves only targeted text edits. No code logic, no tools, no libraries.

## Common Pitfalls

### Pitfall 1: Editing the wrong delegation template
**What goes wrong:** INT-01 requires adding the "Reference File Coverage" field to the Document-Reviewer AND Contract-Reviser briefing templates. The Document-Drafter and Legal-Researcher templates do NOT need this field (they don't apply source markers).
**Why it happens:** delegation-model.md has 5 briefing templates. Only 2 need the new field.
**How to avoid:** Only modify the Contract-Reviser Briefing Template (line 16 heading, code block lines 16-51) and Document-Reviewer Briefing Template (line 53 heading, code block lines 55-81). Leave the other 3 templates untouched.
**Warning signs:** If the edit touches the Legal-Researcher, Document-Drafter, or Closing Document Briefing Template sections, it is wrong.

### Pitfall 2: Using wrong path format for INT-02
**What goes wrong:** The stale path `references/contract-review-workflow.md` gets updated to a relative path instead of the `${CLAUDE_PLUGIN_ROOT}` rooted path.
**Why it happens:** The stale path looks relative, so the fix might also be relative.
**How to avoid:** The canonical path format used throughout the codebase is `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/contract-review-workflow.md`. Check SKILL.md lines 82-84 and lines 390-391 for the established convention.
**Warning signs:** If the replacement path does not start with `${CLAUDE_PLUGIN_ROOT}`, it does not match the codebase convention.

### Pitfall 3: Deleting tracked files instead of untracked directory
**What goes wrong:** Using `git rm` on the `references/` directory when it is untracked.
**Why it happens:** Assumption that the directory is tracked.
**How to avoid:** The `references/` directory is untracked (confirmed: `git ls-files references/` returns empty, `git log -- references/` returns empty). Use `rm -rf references/` not `git rm -rf references/`.
**Warning signs:** `git rm` will fail with "pathspec 'references/' did not match any files."

### Pitfall 4: Incorrect placement of Reference File Coverage field
**What goes wrong:** The new field is placed outside the markdown code block or in the wrong position within the template.
**Why it happens:** The templates are inside fenced code blocks (` ```markdown ... ``` `). The new field must go INSIDE the code block.
**How to avoid:** Place the field logically -- after the existing context fields and before the Output Requirements section, following the same heading/format pattern as adjacent fields.
**Warning signs:** If the field is not inside the code block delimiters, subagents will not see it as part of the template.

### Pitfall 5: Incomplete Workflow 3 cross-reference
**What goes wrong:** Adding a vague cross-reference like "see delegation-model.md" without naming the specific template.
**Why it happens:** The fix description says "add explicit cross-reference" but doesn't mandate the specificity.
**How to avoid:** The cross-reference must name the specific template: "Closing Document Briefing Template in delegation-model.md" -- not just "delegation-model.md" generically.
**Warning signs:** If the added text does not include the words "Closing Document Briefing Template," it is not specific enough.

## Code Examples

### INT-01: Reference File Coverage Field Addition

The field should be added to the Document-Reviewer and Contract-Reviser briefing templates. Based on the source marker convention in `document-reviewer.md` (line 101) and `document-drafter.md` (line 85), and the coverage report format in `contract-review-workflow.md` Step 3-pre (line 70-71), the field should communicate which reference files are populated vs placeholder.

**Add to Contract-Reviser Briefing Template** (inside the code block, between "Prior Batch Changes" and "Output Requirements"):

```markdown
### Reference File Coverage
[Coverage status from Step 3-pre: which checklist categories have firm-specific content vs [TODO] placeholders, clause library and market standards population status -- enables correct application of † source markers]
```

**Add to Document-Reviewer Briefing Template** (inside the code block, between "Document Outline" and "Output Requirements"):

```markdown
### Reference File Coverage
[Coverage status from Step 3-pre: which checklist categories have firm-specific content vs [TODO] placeholders, clause library and market standards population status -- enables correct application of † source markers]
```

**Rationale:** Both `document-reviewer.md` (line 101) and `document-drafter.md` (line 85) state: "Sara provides reference file status in the delegation briefing; apply dagger to any assessment where the corresponding checklist item has a [TODO] placeholder or the market standards file has no entry." The briefing template needs a field where Sara actually provides this data.

### INT-02: Stale Path Fix

**Current (line 257 of work-product-standards.md):**
```
- Follow the contract review workflow in `references/contract-review-workflow.md`
```

**Fixed:**
```
- Follow the contract review workflow in `${CLAUDE_PLUGIN_ROOT}/skills/sara/references/contract-review-workflow.md`
```

### INT-03: Workflow 3 Cross-Reference

**Current (deal-workflows.md, Workflow 3 Step 3, line ~361):**
```
Sara drafts closing documents from scratch (no pre-built templates). For delegation: Sara extracts deal terms and provides precise specifications, then delegates individual document drafting to document-drafter if doing so improves quality. Sara reviews each draft before finalizing.
```

**Fixed (add cross-reference to delegation template):**
```
Sara drafts closing documents from scratch (no pre-built templates). For delegation: Sara extracts deal terms and provides precise specifications using the Closing Document Briefing Template in delegation-model.md, then delegates individual document drafting to document-drafter. Sara reviews each draft before finalizing.
```

### Tech Debt: gen_calendar.py Docstring Fix

**Current (line 5):**
```python
    python docx-tools/cli/calendar.py --events '<json>' --output calendar.ics
```

**Fixed:**
```python
    python docx-tools/cli/gen_calendar.py --events '<json>' --output calendar.ics
```

### Tech Debt: README.md Skill Name Fix

**Current (line 30):**
```
| `sara-associate` | Skill | Core persona and behavioral framework |
```

**Fixed:**
```
| `sara` | Skill | Core persona and behavioral framework |
```

### Tech Debt: Stale References Directory Deletion

```bash
rm -rf references/
```

The directory is untracked (never committed to git). Contains 3 files totaling 581 lines -- all superseded by canonical versions in `skills/sara/references/` totaling 1,323 lines.

## State of the Art

Not applicable -- this is a documentation consistency phase, not a technology adoption phase.

## Open Questions

None. All 6 fixes are well-defined with clear before/after states. The milestone audit specified each issue precisely, and codebase investigation confirms every detail.

## Sources

### Primary (HIGH confidence)
- **v1.0 Milestone Audit** (`.planning/v1.0-MILESTONE-AUDIT.md`) -- defines all 3 integration gaps and 3 tech debt items
- **delegation-model.md** (`skills/sara/references/delegation-model.md`) -- verified 5 briefing templates, identified which 2 need the Reference File Coverage field
- **document-reviewer.md** (`agents/document-reviewer.md`, line 101) -- confirmed "Sara provides reference file status in the delegation briefing" language
- **document-drafter.md** (`agents/document-drafter.md`, line 85) -- confirmed same language for transmittal source markers
- **contract-review-workflow.md** (`skills/sara/references/contract-review-workflow.md`, lines 70-71) -- confirmed Step 3-pre coverage report format
- **work-product-standards.md** (`skills/sara/references/work-product-standards.md`, line 257) -- confirmed stale path reference
- **deal-workflows.md** (`skills/sara/references/deal-workflows.md`, line 361) -- confirmed missing cross-reference in Workflow 3 Step 3
- **gen_calendar.py** (`docx-tools/cli/gen_calendar.py`, line 5) -- confirmed docstring says `calendar.py`
- **README.md** (line 30) -- confirmed `sara-associate` instead of `sara`
- **git status / git log** -- confirmed `references/` directory is untracked, never committed

## Metadata

**Confidence breakdown:**
- All fixes: HIGH -- every issue was verified by direct file inspection against the audit findings. No ambiguity in what needs to change.
- File locations: HIGH -- all files exist at the specified paths with the specified content at the specified line numbers.
- Deletion safety: HIGH -- `references/` is untracked (never committed), confirmed by both `git ls-files` and `git log`.

**Research date:** 2026-02-19
**Valid until:** No expiration -- these are factual findings about the current codebase state. Fixes remain valid until the files are modified.
