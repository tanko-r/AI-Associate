# Architecture

**Analysis Date:** 2026-02-17

## Pattern Overview

**Overall:** Multi-agent hierarchical system with specialization layers

**Key Characteristics:**
- Command-driven entry point (`/sara`) that activates a persona-based skill system
- Hierarchical delegation model: senior associate (Sara) directs junior associates (specialized subagents)
- Structured work product generation organized in matter-specific directories
- Document processing pipeline: parsing, analysis, extraction, redlining, comparison
- MCP server exposing document tools + CLI fallback for flexible integration

## Layers

**Command Interface:**
- Purpose: Entry point for user interaction
- Location: `commands/sara.md`
- Contains: Slash command definition that loads the Sara skill
- Depends on: Sara skill (loaded on activation)
- Used by: Claude Code plugin system

**Sara Skill (Behavioral Framework):**
- Purpose: Define persona, decision-making patterns, quality standards, delegation protocols
- Location: `skills/sara/SKILL.md`
- Contains: Identity and voice, practice area handling, work product standards, delegation patterns, document tool usage, quality requirements
- Depends on: Junior associate agents, document tools (via MCP or CLI)
- Used by: Command invocation; orchestrates all downstream work

**Junior Associate Agents:**
- Purpose: Specialized task execution under Sara's direction
- Location: `agents/legal-researcher.md`, `agents/document-drafter.md`, `agents/document-reviewer.md`, `agents/contract-reviser.md`
- Contains: Role definition, task-specific execution patterns, output formats, quality standards
- Depends on: Sara's instructions, available tools (file read/write, web search, bash)
- Used by: Sara delegates via Task tool; work saved to `Sara-Work-Product/[matter]/junior-work/`

**Reference Guides:**
- Purpose: Detailed patterns and workflows for specific operations
- Location: `skills/sara/references/` — `contract-review-workflow.md`, `delegation-model.md`, `work-product-standards.md`
- Contains: Step-by-step processes, output format specifications, quality checklists
- Depends on: Nothing
- Used by: Sara consults during work; defines the contract review 5-step process, document type conventions, document-to-file mappings

**Document Processing Core:**
- Purpose: Parse, analyze, manipulate Word documents (.docx)
- Location: `docx-tools/core/` — reader.py, writer.py, redliner.py, analyzer.py, extractor.py, comparer.py
- Contains: Core document operations with no external AI calls
- Depends on: python-docx (native Word support), lxml, diff-match-patch
- Used by: MCP server and CLI scripts; invoked by Sara for document work

**Tool Exposure Layer:**
- Purpose: Expose document tools to Sara via two interfaces
- Location: `docx-tools/mcp_server.py` (MCP mode), `docx-tools/cli/` (CLI mode)
- Contains: Tool wrappers, argument parsing, output formatting for display
- Depends on: Document processing core
- Used by: Sara calls via appropriate mode (MCP native tools or bash CLI invocation)

## Data Flow

**Contract Review Workflow (Levels 1-5 Aggressiveness):**

1. **Intake** → Sara captures representation, document type, practice area, commercial context, aggressiveness level
2. **Initial Read** → `read_docx` or `extract_structure` parses document into structured form
3. **Framework Building** → Legal research (delegate to `legal-researcher` or self-research) identifies target concepts and risks
4. **Concept Extraction** → Sara builds document concept map (what the deal says) — may delegate to `document-reviewer`
5. **Risk Mapping** → Sara identifies risk items per provision; at level 4-5, every paragraph gets a disposition
6. **Revision** → Batch paragraphs with identified risks to `contract-reviser` junior for proposed language; returns revised JSON
7. **Redlining** → `redline_docx` converts revision JSON into .docx with native Word track changes and comment bubbles
8. **Deliverables** → Transmittal memo + redline .docx + open items list (never naked redline)

**Document Drafting Workflow:**

1. Sara provides instructions to `document-drafter` junior
2. Junior drafts in markdown with clear structure
3. Sara reviews draft
4. If approval, Sara converts to .docx via `write_docx` with optional template
5. Document written to `Sara-Work-Product/[matter]/final/draft-[name].docx`

**Document Comparison:**

1. Sara provides two .docx files
2. `compare_docx` parses both, performs diff-match-patch line comparison
3. Returns structured change list (modified, added, deleted)
4. Optionally generates redlined .docx showing all differences

**State Management:**

- **Work product saved to filesystem** — Sara writes all deliverables to `Sara-Work-Product/[matter]/` subdirectories (final/, analysis/, research/, junior-work/)
- **Audit trail in prompt-log.md** — Every delegation and major analytical step logged in markdown for partner review
- **Paragraph IDs as state keys** — Document parsing assigns unique IDs (`p_1`, `p_2`, etc.); revision JSON keys map to these IDs
- **Matter context maintained in directory structure** — Separating final/, analysis/, research/, junior-work/ keeps work organized and queryable

## Key Abstractions

**Paragraph ID System:**

- Purpose: Enable precise targeting of revisions without full-document diffing
- Examples: `read_docx` output includes `"id": "p_15"` for each paragraph; `redline_docx` takes `{"p_15": {"original": "...", "revised": "..."}}`
- Pattern: Paragraphs numbered sequentially during parse; IDs stable across multiple reads if document structure unchanged

**Revision JSON:**

- Purpose: Structured way to encode paragraph-level changes for redlining
- Pattern: `{"p_N": {"action": "revise", "original": "...", "revised": "..."}, "p_M": {"action": "delete"}, "insert_after_p_K": {"action": "insert", "text": "..."}}`
- Optional comment field anchors Word comment bubbles: `{"p_N": {..., "comment": "Proposed language addresses deposit exposure"}}`

**Risk Map Entry:**

- Purpose: Document all identified risks with severity, location, recommendation
- Pattern: Every paragraph at aggressiveness 4-5 must have a disposition (Accept/Revise/Delete/Insert/Comment); lower levels only flag identified risks
- Used for: Cross-referencing during revision, tracking conforming changes, audit trail

**Concept Map:**

- Purpose: Extract what the deal says (commercial terms, structural provisions, defined terms)
- Categories: Universal (Consideration, Conditions, Reps, Covenants, Indemnification, Termination, Default, Liability Limits, Knowledge Standards, Assignment, Dispute Resolution, Defined Terms)
- Plus practice-area-specific categories identified during Step 3 of contract review
- Used for: Understanding document structure, ensuring revision consistency, cross-reference validation

## Entry Points

**Command Entry:**
- Location: `/sara [practice-area]`
- Triggers: User invokes slash command in Claude Code
- Responsibilities: Load Sara skill, initialize session with practice area, accept work assignments

**Skill Activation:**
- Location: `commands/sara.md` loaded by `/sara` invocation
- Triggers: Command execution
- Responsibilities: Establish persona context, make Sara available for tasks, set expectations for work product format

**Document Tool MCP:**
- Location: `docx-tools/mcp_server.py`
- Triggers: FastMCP stdio transport when configured in .claude-plugin/
- Responsibilities: Expose read_docx, write_docx, redline_docx, compare_docx, extract_structure, analyze_contract as native tools
- Used by: Sara calls tools directly by name when in MCP mode

**Document Tool CLI:**
- Location: `docx-tools/cli/read.py`, `write.py`, `redline.py`, etc.
- Triggers: Sara invokes `python ${CLAUDE_PLUGIN_ROOT}/docx-tools/cli/[operation].py` via bash
- Responsibilities: Parse arguments, invoke core logic, return formatted output
- Used by: Sara calls via bash when in CLI mode (fallback if MCP unavailable)

## Error Handling

**Strategy:** Structural parsing is defensive; document analysis is explicit

**Patterns:**

- **Reader robustness** — Paragraph extraction handles missing styles, malformed numbering, skips unreadable tables gracefully
- **No external AI in core tools** — All parsing is pattern-matching and structural (no LLM calls in reader.py, writer.py, redliner.py, comparer.py, extractor.py)
- **Explicit conforming-change tracking** — Contract-reviser outputs "Conforming Changes Needed" for each revision; Sara validates before applying
- **Audit trail for revision decisions** — prompt-log.md records which junior revised which paragraphs, enabling traceability if changes need reversal

## Cross-Cutting Concerns

**Logging:** Maintained in `Sara-Work-Product/[matter]/prompt-log.md` — markdown audit trail of delegations, analytical decisions, output files

**Validation:**
- `legal-researcher` validates case citations and distinguishes binding vs. persuasive authority
- `document-reviewer` compares against market standards and flags non-standard language
- `contract-reviser` preserves document voice and validates cross-references before proposing changes
- Sara validates junior work and sends back if below standard

**Authentication:** None at tool level — Sara operates under authenticated Claude Code session; document tools do not require additional auth

**Practice Area Context:** Set at session start (`/sara [area]`); informs research direction, terminology, provision interpretation throughout the session

---

*Architecture analysis: 2026-02-17*
