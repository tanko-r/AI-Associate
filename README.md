# AI Associate — Sara

Sara is a senior 9th-year law firm associate who operates within Claude Code. She owns legal work end-to-end, produces clean work product, delegates to junior associates, and manages up with recommendations.

## Quick Start

Invoke Sara with a slash command and specify the practice area in which you expect her to be an expert.  For example:

```
/sara real estate
/sara erisa
/sara corporate
```

If no practice area is specified, Sara will ask.

## Features

- **Practice-agnostic** — set Sara's specialty at session start via command argument
- **Work product** — drafts memos, agreements, briefs, correspondence, and analysis as files
- **Delegation** — spawns junior associate subagents for research, drafting, and review
- **Legal research** — CourtListener integration for case law, citations, and regulatory data
- **Commercial judgment** — assesses materiality, prioritizes issues, and recommends actions

## Components

| Component | Type | Purpose |
|-----------|------|---------|
| `/sara` | Command | Activate Sara with a practice area |
| `sara` | Skill | Core persona and behavioral framework |
| `legal-researcher` | Agent | Junior associate for legal research |
| `document-drafter` | Agent | Junior associate for document drafting |
| `document-reviewer` | Agent | Junior associate for document review |
| `court-listener` | MCP | CourtListener legal database access |

## Prerequisites

### CourtListener (Optional)

For legal database access (case law, citations, regulations):

1. **Clone the CourtListener MCP server:**
   ```bash
   git clone https://github.com/Travis-Prall/court-listener-mcp.git /opt/court-listener-mcp
   cd /opt/court-listener-mcp
   uv sync
   ```

2. **Get a CourtListener API key:**
   - Create a free account at [courtlistener.com](https://www.courtlistener.com)
   - Find your API token in your account profile
   - Free tier: 5,000 requests/day

3. **Set environment variables:**
   ```bash
   export COURT_LISTENER_API_KEY="your-token-here"
   export COURT_LISTENER_MCP_PATH="/opt/court-listener-mcp"  # if not using default path
   ```

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

Sara works without CourtListener — she'll use web search for legal research and let you know if database access would be helpful.

## Usage

### Assign Work

```
> /sara real estate
> Review this lease and flag any issues with the termination provisions.
```

### Sara Produces Files

Substantive work product is written to files in the working directory:
- `memo-lease-termination-rights.md`
- `draft-nda-acme-corp.md`
- `research-non-compete-enforceability.md`

### Sara Delegates

For research, drafting, and review tasks, Sara delegates to junior associates and reviews their work before presenting it to you.

### Sara Recommends

When Sara can't take an action herself (sending emails, making calls, filing documents), she provides a recommendation and draft message.
