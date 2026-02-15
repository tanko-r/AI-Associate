# Docx Tools Integration — Design Document

**Date:** 2026-02-14
**Status:** Approved

## Summary

Add docx reading, writing, redlining, and comparison capabilities to Sara's plugin via a shared Python core library exposed through two interfaces: an MCP server and CLI scripts. An in-session `/docx-mode` command toggles between them for A/B testing.

## Architecture

Both integration paths share a common core library. The MCP server and CLI scripts are thin wrappers over the same functions.

```
AI-Associate/
├── docx-tools/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── reader.py          # parse docx → structured dict
│   │   ├── writer.py          # structured content → docx
│   │   ├── redliner.py        # original + revised → track changes docx
│   │   ├── comparer.py        # two docx files → diff report
│   │   ├── extractor.py       # docx → sections, defined terms, provisions
│   │   └── analyzer.py        # lightweight risk/issue identification
│   ├── cli/
│   │   ├── read.py
│   │   ├── write.py
│   │   ├── redline.py
│   │   ├── compare.py
│   │   ├── extract.py
│   │   └── analyze.py
│   ├── mcp_server.py
│   └── requirements.txt
├── commands/
│   ├── sara.md
│   └── docx-mode.md
├── .mcp.json                  # Updated with docx-tools server
└── ...existing plugin files
```

## Tools

### 1. `read_docx`
- **Input:** Path to .docx file
- **Output:** Full text content with paragraph IDs, section hierarchy, metadata (parties, date, title if detectable)
- **Source:** Adapted from Ambrose's `parse_document()` — keeps `NumberingResolver`, `SectionTracker`, paragraph extraction; drops Flask/session handling

### 2. `write_docx`
- **Input:** Content (markdown or structured text), output path, optional template .docx
- **Output:** A .docx file at the specified path
- **Notes:** Template provides style inheritance (fonts, headings, numbering). Without one, uses clean professional defaults.

### 3. `redline_docx`
- **Input:** Original .docx path, revised text (keyed by paragraph ID), output path
- **Output:** A .docx with native Word track changes (insertions/deletions)
- **Source:** Adapted from Ambrose's `generate_track_changes_docx()` using the `redlines` library

### 4. `compare_docx`
- **Input:** Two .docx file paths
- **Output:** Structured diff report — additions/deletions/modifications by section. Optionally a redlined .docx showing differences.
- **Source:** `diff-match-patch` on extracted text, mapped back to paragraph structure

### 5. `extract_structure`
- **Input:** Path to .docx file
- **Output:** Sections with hierarchy, defined terms with definitions, provisions by type (obligations, rights, conditions, termination triggers), exhibits list
- **Source:** Adapted from Ambrose's `initial_analyzer.py` parsing logic (non-LLM parts) plus `NumberingResolver`

### 6. `analyze_contract`
- **Input:** Path to .docx file, representation (e.g., buyer/seller/landlord/tenant), optional focus areas
- **Output:** Risk inventory with severity ratings, concept map grouping provisions by legal concept, key findings
- **Notes:** Parses and returns a structured prompt-ready format. Sara processes it with her own judgment — no external AI calls from the tool itself.

## Analysis Depth Testing

Three levels of tool-assisted analysis, all testable:

1. **Full tool analysis** — `analyze_contract` does risk identification, Sara reviews
2. **Structure only** — `extract_structure` returns document anatomy, Sara does the analysis
3. **Raw read** — `read_docx` returns text, Sara handles everything

## MCP Server

Registered in `.mcp.json` alongside CourtListener:

```json
{
  "mcpServers": {
    "court-listener": { "...existing..." },
    "docx-tools": {
      "command": "uv",
      "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}/docx-tools", "mcp_server.py"],
      "env": {}
    }
  }
}
```

Uses MCP Python SDK with stdio transport. Each tool has typed input schemas.

## CLI Scripts

Standalone entry points printing structured text to stdout:

```bash
python docx-tools/cli/read.py /path/to/contract.docx
python docx-tools/cli/write.py --input draft.md --output agreement.docx
python docx-tools/cli/redline.py original.docx --revised-text revised.json --output redlined.docx
python docx-tools/cli/compare.py v1.docx v2.docx
python docx-tools/cli/extract.py contract.docx
python docx-tools/cli/analyze.py contract.docx --representation tenant
```

## In-Session Toggle: `/docx-mode`

**Usage:**
- `/docx-mode mcp` — Sara uses MCP tools
- `/docx-mode cli` — Sara uses Bash + CLI scripts
- `/docx-mode` — shows current mode

**Mechanism:** Writes preference to `.claude/ai-associate.local.md`:

```yaml
---
docx_mode: mcp
---
```

Default is `mcp` if no preference is set. Sara's skill checks this before any docx operation.

## Code Sourced From Ambrose

| Ambrose source | Extracted | Left behind |
|---|---|---|
| `document_service.py` | `parse_document()`, `NumberingResolver`, `SectionTracker`, `extract_section_number()`, `generate_track_changes_docx()` | Flask session handling, upload management |
| `initial_analyzer.py` | Section/defined-term extraction patterns | Gemini API calls |
| `content_filter.py` | `should_analyze()` skip logic | — |
| `html_renderer.py` | Nothing | HTML rendering (not needed) |
| `matching_service.py` | Nothing | TF-IDF matching (possible future addition) |

Estimated ~250-300 lines of adapted code.

## Dependencies

```
python-docx>=0.8.11
redlines>=0.4.0
diff-match-patch>=20200713
mcp>=1.0.0
```

## Skill & Agent Updates

- Sara's `SKILL.md` gets a docx operations section referencing both modes
- `document-drafter` agent gets Write access note for .docx output
- `document-reviewer` agent gets Read access note for .docx input
- `/docx-mode` command added to `commands/`
