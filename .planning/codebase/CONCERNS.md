# Codebase Concerns

**Analysis Date:** 2026-02-17

## Tech Debt

**Redliner revision ID generation is non-deterministic:**
- Issue: `redliner.py` line 145 and 153 use `abs(hash(text)) % 100000` to generate Word revision IDs
- Files: `docx-tools/core/redliner.py`
- Impact: Hash collisions possible; identical text segments may share revision IDs, causing Word markup errors. Multiple runs of the same revision produce different IDs (breaks caching/comparison).
- Fix approach: Switch to deterministic ID generation using SHA256 hash prefix or paragraph+operation-based sequential IDs. Ensures consistent revision tracking across runs.

**Section numbering state management in reader.py is fragile:**
- Issue: `SectionTracker` class (lines 97-177) maintains implicit state through counters and hierarchy, with complex level-inference logic
- Files: `docx-tools/core/reader.py`
- Impact: Reordering paragraphs or parsing documents with non-standard numbering schemas may produce incorrect section references. The pattern matching is extensive (18 regex patterns) but doesn't handle all legal document styles.
- Fix approach: Add explicit validation that inferred levels match explicit section numbers in document. Introduce fallback to "unknown structure" rather than guessing. Add test cases for edge-case numbering.

**Markdown-to-DOCX rendering is simplistic:**
- Issue: `writer.py` line 102 uses regex pattern `r'(\*\*(.+?)\*\*|\*(.+?)\*|([^*]+))'` which doesn't handle nested formatting, escaped asterisks, or cross-paragraph formatting
- Files: `docx-tools/core/writer.py`
- Impact: Complex markdown (nested bold/italic, code blocks, tables) silently fails or renders incorrectly. No error reporting to user.
- Fix approach: Use a dedicated markdown parser (like `markdown2` or `mistune`) instead of regex. Add validation that input markdown is structurally sound before processing.

**Paragraph ID allocation is position-dependent:**
- Issue: Paragraph IDs (`p_1`, `p_2`, etc.) are assigned sequentially as document is parsed in `read_docx` (lines 54-81 in redliner.py)
- Files: `docx-tools/core/redliner.py`, `docx-tools/core/reader.py`
- Impact: If document structure changes (e.g., deleted paragraph, inserted section), paragraph IDs shift, breaking revision maps and causing wrong paragraphs to be redlined. Redline JSON keyed on old `p_N` IDs becomes invalid.
- Fix approach: Implement stable paragraph identifiers using combination of section reference + ordinal within section, or hash-based content identifiers. Add validation in redliner that revision keys match actual paragraph IDs in document.

---

## Known Bugs

**Comparer produces incorrect para_id for added paragraphs:**
- Symptoms: When comparing two documents where the second has more paragraphs, added paragraphs get assigned IDs like `new_42`, which don't correspond to actual paragraph numbers
- Files: `docx-tools/core/comparer.py` line 75
- Trigger: Run `compare_docx(original.docx, longer_version.docx)`
- Workaround: Manually map `new_N` IDs to actual section references when reviewing additions. Not critical for comparison view, but problematic if comparison output is used to generate revisions.

**Reader fails gracefully on documents without numbering.xml:**
- Symptoms: `NumberingResolver` silently catches all exceptions (line 189), may silently skip numbering resolution
- Files: `docx-tools/core/reader.py` lines 187-192
- Trigger: Open a .docx created without standard numbering metadata
- Workaround: Log warnings when numbering resolution fails. Current silent failure makes it hard to debug section reference issues.

---

## Security Considerations

**JSON input to redline_docx is not validated:**
- Risk: `redline_docx` MCP tool (mcp_server.py line 45) calls `json.loads()` on user input with no schema validation. Malformed or oversized JSON could cause memory exhaustion or injection issues.
- Files: `docx-tools/mcp_server.py` line 45
- Current mitigation: Python's json.loads will raise exception on invalid JSON (caught by MCP framework)
- Recommendations: Add explicit schema validation using `pydantic` models. Set size limits on JSON payloads. Validate revision keys match actual paragraph IDs before applying changes.

**File path traversal in document operations:**
- Risk: `read_docx`, `write_docx`, `redline_docx` accept file paths without validation. Malicious paths could read/write to sensitive locations
- Files: `docx-tools/core/reader.py` line 43, `core/writer.py` line 33, `core/redliner.py` line 43
- Current mitigation: Operating in Claude context, not web-exposed
- Recommendations: Add path canonicalization and restrict operations to a designated working directory. Validate that paths don't contain `..` or absolute references outside safe zone.

**Defined term extraction uses simple regex without bounds:**
- Risk: `extract_defined_terms` (reader.py line 92) uses `r'"([A-Z][^"]+)"'` which matches any quoted string starting with uppercase. Could be fooled by corrupted documents with many false-positive defined terms
- Files: `docx-tools/core/reader.py` line 92
- Current mitigation: False positives are informational only, not used for critical operations
- Recommendations: Add length bounds on extracted terms (`min_length=3, max_length=50`). Filter out common false positives (e.g., quoted names, measurements).

---

## Performance Bottlenecks

**Diff-match-patch is called per-paragraph:**
- Problem: `_apply_track_changes` (redliner.py line 115) instantiates new `diff_match_patch()` object for every paragraph revision. For large documents (100+ revisions), this is redundant.
- Files: `docx-tools/core/redliner.py` lines 115, 51
- Cause: One DMP instance can be reused across all comparisons; creating new instance per-call is wasteful
- Improvement path: Create DMP instance once at module level or as parameter. Benchmarking suggests ~10-15% speedup for documents with 50+ revisions.

**Reader parses every paragraph regardless of use case:**
- Problem: `read_docx` always extracts full text, style info, and section hierarchy for every paragraph (lines 54-81), even when caller only needs defined terms or structure
- Files: `docx-tools/core/reader.py`
- Cause: No lazy evaluation or selective parsing
- Improvement path: Add optional parameters to `read_docx` to skip certain extraction steps (e.g., `extract_styles=False`, `extract_hierarchy=False`). Use this in `extract_structure` to improve speed on large documents.

**Analyzer iterates through all paragraphs for each risk category:**
- Problem: `_map_risk_categories` (analyzer.py lines 157-180) loops through all paragraphs once per risk category. For 170 paragraphs and 15 risk categories, this is 2550 iterations.
- Files: `docx-tools/core/analyzer.py` lines 157-180
- Cause: Category-first loop should be paragraph-first to batch category checks per paragraph
- Improvement path: Reverse loop order: iterate paragraphs once, check all category signals per paragraph. Expected 2-3x speedup.

---

## Fragile Areas

**Concept map and risk map assembly relies on precise paragraph numbering:**
- Files: `skills/sara/references/contract-review-workflow.md` (Step 5-6), `docx-tools/core/redliner.py`
- Why fragile: The workflow assumes paragraph IDs remain stable between steps (initial read in Step 2, risk mapping in Step 5, redline compilation in Step 6). If user modifies the original document between steps, all references break.
- Safe modification: Never re-read the original document after initial extraction. If document must be re-read, regenerate all analysis (risk map, concept map) from the new read. Add checksum validation to detect document changes.
- Test coverage: No tests validate that paragraph IDs remain consistent across sequential operations on the same document.

**Contract-reviser workflow dispatch order is sequential but undocumented:**
- Files: `skills/sara/references/contract-review-workflow.md` Step 6b
- Why fragile: Batch revisions are dispatched sequentially (line 231: "Dispatch sequentially, not in parallel"), but the code doesn't enforce this. If a junior associate accidentally parallelizes or skips a batch, cascading errors in conforming changes go undetected.
- Safe modification: Add explicit validation in prompt-log that all batches were reviewed in order. Flag any batch that references defined terms or provisions from later batches.
- Test coverage: No integration tests for multi-batch revision workflows.

**Writer doesn't validate that content fits document template:**
- Files: `docx-tools/core/writer.py` lines 36-41
- Why fragile: If template has restrictive styles or margin settings, rendered content may overflow or render unexpectedly. No warnings given.
- Safe modification: After rendering, inspect resulting document for overfull paragraphs or missing styles. Log warnings.
- Test coverage: No tests validate that write_docx with template produces consistent output.

---

## Scaling Limits

**Reader's section hierarchy tracking uses in-memory list:**
- Current capacity: 10,000+ paragraphs can be parsed, but memory usage grows linearly with paragraph count and section depth
- Limit: Documents with deeply nested sections (10+ levels) may cause memory issues due to `SectionTracker.hierarchy` list copying on each update (line 141)
- Scaling path: Use immutable data structures (tuples) instead of lists. Replace hierarchy copying with pointer-based structure.

**Redline JSON revision map grows with document size:**
- Current capacity: ~1000-paragraph document with ~200 revisions = revision JSON ~200KB, manageable
- Limit: If scaling to 5000-paragraph documents with 1000 revisions, revision JSON may exceed MCP message size limits (typically 100MB in Claude, but best to stay under 1MB)
- Scaling path: Add batch mode to redline_docx accepting revisions in chunks. Compress revision map by storing only changed text (not original).

---

## Dependencies at Risk

**python-docx version pinned at 1.2.0:**
- Risk: `python-docx` 1.2.0 (released 2024) has limited feature coverage. Native comment API (`doc.add_comment()`) added recently; may have bugs or breaking changes in future versions.
- Files: `docx-tools/.venv/` (implicit in requirements), `docx-tools/core/redliner.py` line 95
- Impact: If project upgrades python-docx, comment functionality may break. Current implementation assumes specific API behavior.
- Migration plan: Pin to `>=1.2.0,<2.0.0` with explicit testing of comment generation. When 2.0.0 released, review breaking changes and test thoroughly before upgrading.

**diff-match-patch is abandoned:**
- Risk: `diff-match-patch` library receives no updates (last release 2018). No security updates, no bug fixes.
- Files: `docx-tools/core/redliner.py` line 14, `docx-tools/core/comparer.py` line 10
- Impact: Bug or security issue discovered in DMP could not be fixed upstream
- Migration plan: Evaluate alternatives (`rapidfuzz`, `difflib` from stdlib, `pygments.difflib`). `difflib` is built-in but less sophisticated. Test migration path on current redline/compare workflows.

---

## Missing Critical Features

**No undo/rollback for redline operations:**
- Problem: Once `redline_docx` produces a marked-up document, there's no way to revert or regenerate the redline with different parameters
- Blocks: Cannot easily experiment with different aggressiveness levels or risk thresholds during Step 5-6 of contract review workflow
- Solution: Store original document + revision JSON together. Add function to "undo" revisions (regenerate clean document from original + revision subset).

**No cross-reference validation in redline batches:**
- Problem: When `contract-reviser` junior associates modify language, they may introduce broken cross-references to provisions in other batches
- Blocks: Cannot guarantee that compiled redline from Step 6c has valid internal references
- Solution: Add post-compilation validation step that scans all proposed language for section/article references and validates they exist in the document structure extracted in Step 2.

**No tracking of which revisions came from which risk category:**
- Problem: When presenting redline to partner, cannot easily explain "this paragraph was changed because of risk category X from the risk map"
- Blocks: Partner must manually trace each redline back to the risk map to understand reasoning
- Solution: Store metadata in revision JSON: `{"p_5": {"action": "revise", ..., "risk_category": "Liability Exposure", "risk_id": "5.2"}}`

---

## Test Coverage Gaps

**No tests for redliner comment functionality:**
- What's not tested: `_add_comment()` function (redliner.py lines 91-100). No verification that comments attach correctly to paragraphs or survive save/reload.
- Files: `docx-tools/core/redliner.py` lines 91-100, `docx-tools/tests/test_redliner.py`
- Risk: Comment feature (added 2026-02-15) could silently fail or corrupt documents without being caught
- Priority: High

**No tests for section reference generation edge cases:**
- What's not tested: `extract_section_number()` and `SectionTracker` behavior on documents with mixed numbering schemes (e.g., "Section 2.1" then "Article III" then "3.1"), non-standard outlines, or missing section numbers
- Files: `docx-tools/core/reader.py` lines 39-72, 97-177
- Risk: Real-world documents often have inconsistent numbering; tests only cover standard patterns
- Priority: High

**No integration tests for workflow:**
- What's not tested: Full contract review workflow (Steps 1-7 from workflow.md) using actual .docx files
- Files: None (tests don't exist)
- Risk: Bugs in cross-module interactions (read → extract → analyze → redline) only discovered in production use
- Priority: Medium

**No tests for malformed JSON in MCP redline_docx tool:**
- What's not tested: What happens when MCP redline_docx receives invalid revision JSON, oversized payloads, or revision keys that don't match document paragraphs
- Files: `docx-tools/mcp_server.py` line 45, `docx-tools/tests/test_redliner.py`
- Risk: Unclear error messages if user provides bad revision JSON; potential security issues
- Priority: Medium

**No tests for writer with complex markdown:**
- What's not tested: Nested formatting (e.g., `**bold with *italic* inside**`), escaped asterisks, code blocks, tables, multiline lists
- Files: `docx-tools/core/writer.py`, `docx-tools/tests/test_writer.py`
- Risk: Silent failures on markdown that doesn't match simple pattern
- Priority: Medium

---

## Workflow Concerns

**Contract review batching strategy is not validated:**
- Issue: The workflow documentation (contract-review-workflow.md Step 6b) provides guidelines ("Simple docs: 1-2 batches, Medium: 3-5 batches, Complex: 5-10 batches") but there's no enforcement or validation that batches are sized correctly
- Files: `skills/sara/references/contract-review-workflow.md` lines 212-217
- Impact: Junior associates may batch inconsistently, leading to missed conforming changes or logical inconsistencies in redline
- Fix approach: Add helper in Sara skill that automatically suggests batch boundaries based on document structure and risk map count

**Prompt log audit trail is manual:**
- Issue: The workflow requires Sara to manually append entries to `prompt-log.md` for every delegation and step (SKILL.md lines 79-142)
- Files: `skills/sara/SKILL.md` lines 79-142
- Impact: Easy to forget to log, leading to incomplete audit trail that defeats the purpose
- Fix approach: Create a `LogEntry` helper that automatically timestamps and formats entries. Require all Task delegations to generate log entries automatically.

**No validation that all paragraphs are reviewed in Step 5:**
- Issue: The workflow (contract-review-workflow.md lines 145-198) instructs Sara to review "each provision and identify risks" but doesn't enforce that every material provision is actually reviewed
- Files: `skills/sara/references/contract-review-workflow.md` lines 145-198
- Impact: Short documents with 50-100 paragraphs may get only 10-15 paragraphs reviewed if Sara focuses only on flagged risks
- Fix approach: Add mandatory disposition for every paragraph in Step 5 (Accept/Revise/Delete/Comment/Insert), not just paragraphs with identified risks

---

## Documentation Gaps

**Redliner comment field behavior is not documented:**
- Issue: `redline_docx` accepts optional `"comment"` field in revision JSON (redliner.py line 64), but this feature is not mentioned in SKILL.md or workflow documentation
- Files: `docx-tools/core/redliner.py` line 64, `skills/sara/SKILL.md` lines 179-202
- Impact: Users don't know they can add comment bubbles; feature goes unused
- Fix: Add example to SKILL.md showing comment field usage

**Analyzer risk categories are not exhaustive:**
- Issue: `analyzer.py` defines risk categories for 4 document types (PSA, lease, development, loan), but many practice areas are missing (IP, employment, securities, immigration, etc.)
- Files: `docx-tools/core/analyzer.py` lines 17-63
- Impact: Sara may analyze non-supported contract types with generic PSA risk categories, producing incorrect risk map
- Fix: Either expand risk categories or add explicit warning when contract type is not recognized

---

*Concerns audit: 2026-02-17*
