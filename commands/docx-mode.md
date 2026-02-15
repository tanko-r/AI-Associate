---
description: Toggle between MCP and CLI for docx tools
argument-hint: [mcp|cli]
---

Set the docx tools integration mode for this session.

Mode requested: $ARGUMENTS

If the argument is "mcp":
- Write the following to `.claude/ai-associate.local.md` (create if it doesn't exist), setting the YAML frontmatter `docx_mode` to `mcp`:
  ```yaml
  ---
  docx_mode: mcp
  ---
  ```
- Confirm: "Docx tools mode set to **MCP**. I'll use the docx-tools MCP server for all document operations."

If the argument is "cli":
- Write the following to `.claude/ai-associate.local.md` (create if it doesn't exist), setting the YAML frontmatter `docx_mode` to `cli`:
  ```yaml
  ---
  docx_mode: cli
  ---
  ```
- Confirm: "Docx tools mode set to **CLI**. I'll use Bash scripts in `docx-tools/cli/` for all document operations."

If no argument was provided (i.e., $ARGUMENTS is empty or blank):
- Read `.claude/ai-associate.local.md` if it exists and check the `docx_mode` value
- Report the current mode: "Current docx tools mode: **[mode]**" (default is `mcp` if no file exists)
