# Coding Conventions

**Analysis Date:** 2026-02-17

## Naming Patterns

**Files:**
- Module files use lowercase with underscores: `reader.py`, `redliner.py`, `comparer.py`, `extractor.py`, `analyzer.py`, `writer.py`
- Test files follow pattern `test_<module>.py`: `test_reader.py`, `test_redliner.py`, `test_comparer.py`, etc.
- CLI scripts in `cli/` directory use lowercase module names: `read.py`, `write.py`, `redline.py`, `analyze.py`
- All test and CLI files are executable (shebang `#!/usr/bin/env python3`)

**Functions:**
- Regular functions use snake_case: `read_docx()`, `write_docx()`, `redline_docx()`, `extract_structure()`
- Private/internal functions prefixed with underscore: `_iter_block_items()`, `_apply_track_changes()`, `_add_comment()`, `_apply_default_styles()`, `_render_markdown_to_docx()`, `_add_inline_markdown()`
- Helper functions for formatting follow pattern `format_for_display()` - returns human-readable string representation

**Variables:**
- Local variables use snake_case: `para_id`, `para_text`, `section_num`, `original_text`, `revised_text`
- Private class attributes prefixed with underscore: `self._p`, `self.abstract_nums`, `self.counters`
- Constants in UPPERCASE with underscores: `RISK_CATEGORIES`, `CATEGORY_SIGNALS`, `PROVISION_PATTERNS`, `DEFINITION_PATTERN`, `PAREN_DEFINITION_PATTERN`
- Dictionary keys use snake_case: `"section_number"`, `"section_hierarchy"`, `"defined_terms"`, `"is_heading"`, `"numbering_level"`

**Types:**
- All function signatures use type hints from `typing` module: `Dict[str, Any]`, `List[Dict]`, `Optional[str]`, `Tuple[Optional[str], str, Optional[str]]`
- Classes use PascalCase: `SectionTracker`, `NumberingResolver`

## Code Style

**Formatting:**
- Python 3.10+ (specified in `pyproject.toml`: `requires-python = ">=3.10"`)
- Lines follow implicit 100-120 character soft limit (no explicit formatter configured)
- Indentation: 4 spaces
- Blank lines: 2 between top-level functions/classes, 1 between methods
- Imports organized with blank lines separating groups

**Linting:**
- No explicit linter configured (no .eslintrc, .flake8, or pylint config)
- Code follows PEP 8 conventions implicitly
- Type hints required on public function signatures

**Docstring Style:**
- Google-style docstrings on public functions and classes
- Module docstrings at file head explain purpose
- Function docstrings include Args, Returns, and optional Raises sections
- Example from `reader.py`:
  ```python
  def read_docx(docx_path: str) -> Dict[str, Any]:
      """
      Parse a .docx file and extract structured content.

      Args:
          docx_path: Path to the .docx file.

      Returns:
          Dict with keys: source_file, metadata, content, defined_terms, sections, exhibits.

      Raises:
          FileNotFoundError: If the file does not exist.
      """
  ```

## Import Organization

**Order:**
1. Standard library imports (pathlib, datetime, sys, etc.)
2. Third-party imports (docx, diff_match_patch, mcp, pytest, etc.)
3. Relative local imports from `core` module

**Path Aliases:**
- No path aliases configured
- Relative imports used within module: `from core.reader import read_docx`
- CLI scripts add parent to sys.path: `sys.path.insert(0, str(Path(__file__).parent.parent))`

**Import Style:**
- Use `from module import Class, function` for specific items
- Use `import module as alias` for third-party with long names (e.g., `import diff_match_patch as dmp_module`)
- Avoid wildcard imports

## Error Handling

**Patterns:**
- Explicit exception handling with try/except blocks for optional features
- Example from `reader.py` - gracefully handle missing numbering:
  ```python
  try:
      numbering_resolver = NumberingResolver(doc)
  except Exception:
      numbering_resolver = None
  ```
- FileNotFoundError explicitly raised with descriptive message: `raise FileNotFoundError(f"File not found: {docx_path}")`
- Parser silently continues on malformed sections (defensive parsing)

**Return values on error:**
- Functions return `None` on failed optional operations
- Invalid regex patterns return `(None, text, None)` instead of raising
- Core I/O operations (read, write) raise exceptions; analysis operations return structured dicts with null/empty values

## Logging

**Framework:** `print()` via stdout (no logging module configured)

**Patterns:**
- CLI scripts print results via `print(format_for_display(result))`
- Informational messages via `print()`: `print(f"Document written to: {path}")`
- No debug logging infrastructure; CLI scripts designed for direct output

## Comments

**When to Comment:**
- Explain non-obvious regex patterns and their purpose
- Document complex algorithms like roman numeral conversion
- Clarify Word XML namespace interactions (qn() usage)
- Example from `reader.py`:
  ```python
  # Patterns for classifying provisions
  PROVISION_PATTERNS = {
      "obligation": [
          r'\bshall\b(?!\s+not)',
          ...
      ]
  }
  ```

**Docstring Usage:**
- All public modules have file-level docstrings explaining purpose
- All public functions/classes require docstrings with Args/Returns
- Private functions get inline docstrings (one-line or short block)
- Example from `redliner.py`:
  ```python
  def _add_comment(doc: Document, paragraph: Paragraph, text: str, author: str):
      """Add a Word comment bubble anchored to a paragraph."""
  ```

## Function Design

**Size:**
- Core parsing functions range 50-100 lines with clear loop structure
- Utility functions stay under 30 lines
- Complex logic broken into `_` prefixed helpers

**Parameters:**
- Max 4-5 parameters; additional config passes via dicts
- Type hints required for all parameters
- Default parameters used for optional features: `author: str = "Sara"`, `template_path: Optional[str] = None`

**Return Values:**
- Public functions return consistent Dict[str, Any] structures for composability
- Private helpers return component pieces (strings, lists, individual items)
- `format_for_display()` always returns `str` for human consumption
- Path functions return `str` of the created/modified file path

## Module Design

**Exports:**
- Public functions exposed at module level (no internal __all__)
- Private functions prefixed with underscore
- Classes (SectionTracker, NumberingResolver) are internal to `reader.py`
- MCP server in `mcp_server.py` imports and wraps core functions

**Barrel Files:**
- No barrel files (no `__init__.py` pattern used for re-exports)
- Each module imports directly from specific submodule: `from core.reader import read_docx`
- Core module (`core/`) treated as flat namespace, not hierarchical

**Composition Pattern:**
- Small focused modules (one tool per file: reader, writer, redliner, comparer, extractor, analyzer)
- Shared utilities extracted to helpers (section tracking, numbering resolution)
- MCP server composes all six tools and provides consistent interface

---

*Convention analysis: 2026-02-17*
