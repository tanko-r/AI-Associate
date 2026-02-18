# External Integrations

**Analysis Date:** 2026-02-17

## APIs & External Services

**Legal Research:**
- **CourtListener** - Case law, court opinions, citations, PACER filings, judge data, eCFR
  - Optional integration; Sara operates without it using web search
  - SDK/Client: Standalone MCP server (`court-listener-mcp`)
  - Auth: `COURT_LISTENER_API_KEY` environment variable
  - Free tier: 5,000 requests/day
  - Documentation: https://www.courtlistener.com/

**Claude Code Integration:**
- **Claude Models** - LLM backend for Sara, legal-researcher, document-drafter, document-reviewer agents
  - Model: Sonnet (specified in agent configurations)
  - Auth: Handled by Claude Code runtime

## Data Storage

**Databases:**
- None - Project operates entirely with file-based documents (.docx files)

**File Storage:**
- **Local filesystem only**
  - Document read/write operations: `docx-tools/core/reader.py`, `docx-tools/core/writer.py`
  - Working directory: Task directory in Claude Code session (relative paths resolved at runtime)
  - Supported formats: .docx (Word documents), markdown (for content input)

**Caching:**
- None - Stateless tool execution per Claude Code call

## Authentication & Identity

**Auth Provider:**
- **Custom per integration** - No centralized auth service
  - CourtListener: API key-based (COURT_LISTENER_API_KEY)
  - Claude Code: Integrated authentication via plugin system
  - MCP: Stdio transport (no separate auth; runs in same process)

**Implementation:**
- Environment variables for external API credentials
- MCP server runs as subprocess with inherited environment
- Plugin permissions configured in `.claude/settings.local.json` (allows specific MCP tools and Python execution)

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service configured

**Logs:**
- Console/stdio output from MCP server
- Test output via pytest (dev environment only)
- No persistent logging infrastructure

## CI/CD & Deployment

**Hosting:**
- **Claude Code plugin system** - Serves as execution environment
- `.claude-plugin/plugin.json` registers Sara as a Claude Code plugin
- Command `/sara [practice-area]` activates Sara skill for the session

**CI Pipeline:**
- None detected - Repository is plugin/skill definition, not a deployed service
- Local testing via pytest in `docx-tools/tests/`

## Environment Configuration

**Required env vars:**
- None - All core functionality works without external services
- Optional for legal research:
  - `COURT_LISTENER_API_KEY` - CourtListener API token
  - `COURT_LISTENER_MCP_PATH` - Custom path to court-listener MCP (defaults to `/opt/court-listener-mcp`)

**Secrets location:**
- Environment variables (set at shell or Claude Code session level)
- No credentials stored in codebase (`.env` file not included in repository)
- CourtListener MCP server at `/opt/court-listener-mcp` (external repository)

**Configuration files:**
- `.claude/settings.local.json` - MCP server permissions (contains no secrets)
- `.claude-plugin/plugin.json` - Plugin metadata (contains no secrets)
- `.claude/ai-associate.local.md` - Docx mode preference (no secrets)

## Webhooks & Callbacks

**Incoming:**
- None - Plugin receives commands via `/sara` slash command from user in Claude Code

**Outgoing:**
- None - No webhook callbacks to external services
- Redlined documents output locally as .docx files (no external transmission)

## MCP Server Configuration

**Registered Servers:**
- `docx-tools` - Local MCP server in `/home/david/projects/AI-Associate/docx-tools/mcp_server.py`
  - Transport: stdio
  - Enabled in `.claude/settings.local.json`
  - Tools exposed:
    - `read_docx` - Parse .docx files with structure and metadata
    - `write_docx` - Create .docx files from markdown content
    - `redline_docx` - Generate tracked-changes .docx with revisions JSON
    - `compare_docx` - Diff two .docx files, optionally produce redlined output
    - `extract_structure` - Extract sections, defined terms, provision types, exhibits
    - `analyze_contract` - Risk category analysis with provision mapping

- `court-listener` - External MCP server (optional)
  - Must be cloned to `/opt/court-listener-mcp`
  - Requires `COURT_LISTENER_API_KEY` environment variable
  - Enabled in `.claude/settings.local.json` if available

**Python Execution:**
- `.claude/settings.local.json` permits: `Bash(/home/david/projects/AI-Associate/docx-tools/.venv/bin/python:*)`
- Enables CLI tool invocation as alternative to MCP server

## Agent Integration

**Subagents (via Claude Code Task tool):**
- `legal-researcher` - Delegates research tasks; uses WebSearch, WebFetch, Read, Write, Grep, Glob tools
- `document-drafter` - Delegates document drafting; uses Write, Read, Glob tools
- `document-reviewer` - Delegates document review; uses Read, Write, Glob tools

**No inter-agent APIs** - Agents communicate through Claude Code task delegation; results returned as text/files

---

*Integration audit: 2026-02-17*
