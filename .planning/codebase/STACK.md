# Technology Stack

**Analysis Date:** 2026-02-17

## Languages

**Primary:**
- Python 3.10+ - Document processing tools, contract analysis, redlining engines, MCP server
- Markdown - Skill definitions, agent instructions, command specifications, documentation

**Secondary:**
- JSON - Configuration, plugin metadata, revision data structures

## Runtime

**Environment:**
- Python 3.12.3 (detected in environment; pyproject.toml requires 3.10+)
- Virtual environment: `docx-tools/.venv/`

**Package Manager:**
- `uv` - Python package manager with lock file support
- Lockfile: `docx-tools/uv.lock` (present)

## Frameworks

**Core:**
- **Model Context Protocol (MCP)** - Integration framework for Claude Code extensions
  - Version: `>=1.0.0`
  - Purpose: Exposes docx-tools as serverless tools to Claude
  - Implementation: `docx-tools/mcp_server.py` uses FastMCP

**Document Processing:**
- **python-docx** `>=0.8.11` - Read, write, manipulate .docx files
  - Provides native Word comment support via `doc.add_comment()`
  - Used by reader, writer, redliner, comparer modules

**Diff/Comparison:**
- **diff-match-patch** `>=20200713` - Text diffing algorithm for track changes
- **redlines** `>=0.4.0` - Highlighting and redline generation

**Testing:**
- **pytest** `>=7.0.0` - Test runner (dev dependency)

**Build/Dev:**
- **FastMCP** - Lightweight MCP server framework (included with `mcp>=1.0.0`)

## Key Dependencies

**Critical:**
- `python-docx>=0.8.11` - Core document manipulation; enables native Word track changes and comment bubbles
- `mcp>=1.0.0` - Protocol implementation for Claude Code integration
- `diff-match-patch>=20200713` - Enables paragraph-level redlining with diff-based revisions

**Infrastructure:**
- `redlines>=0.4.0` - Generates human-readable redline summaries

## Configuration

**Environment:**
- `COURT_LISTENER_API_KEY` - Optional API key for CourtListener legal database (free tier: 5,000 requests/day)
- `COURT_LISTENER_MCP_PATH` - Optional custom path to court-listener MCP server (defaults to `/opt/court-listener-mcp`)
- Docx mode configuration: `.claude/ai-associate.local.md` (YAML frontmatter `docx_mode: mcp` or `mcp`)

**Build:**
- `docx-tools/pyproject.toml` - Project metadata, dependencies, optional dev tools
- `docx-tools/requirements.txt` - Pinned dependency list

**Plugin:**
- `.claude-plugin/plugin.json` - Registers Sara plugin (name: "sara", version 0.6.0)
- `.claude/settings.local.json` - MCP server permissions and enablement configuration

## Platform Requirements

**Development:**
- Python 3.10+
- `uv` package manager
- Virtual environment (`docx-tools/.venv/`)
- File system access for reading/writing .docx files

**Production/Claude Code:**
- Python 3.10+ available in execution environment
- MCP server accessible via stdio transport (FastMCP default)
- Word document templates for style inheritance (optional)
- CourtListener MCP server at `/opt/court-listener-mcp` (optional for legal research)

**Plugin System:**
- Claude Code plugin infrastructure for slash command registration
- Sara skill loaded as complete behavioral framework for session
- Subagent delegation via Task tool to: legal-researcher, document-drafter, document-reviewer

---

*Stack analysis: 2026-02-17*
