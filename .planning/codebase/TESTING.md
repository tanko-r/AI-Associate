# Testing Patterns

**Analysis Date:** 2026-02-17

## Test Framework

**Runner:**
- pytest 7.0.0+ (specified in `pyproject.toml`: `pytest>=7.0.0`)
- Config: No explicit pytest.ini or setup.cfg; uses pyproject.toml `[project.optional-dependencies]`

**Assertion Library:**
- Built-in `assert` statements (no additional assertion library)

**Run Commands:**
```bash
pytest                      # Run all tests in tests/ directory
pytest -v                   # Verbose output with test names
pytest -k test_name         # Run specific test by name pattern
pytest --tb=short           # Shorter traceback format
pytest tests/test_reader.py # Run single test file
```

## Test File Organization

**Location:**
- Co-located in `docx-tools/tests/` directory (separate from source, not co-located with modules)
- Import core modules via relative sys.path insertion:
  ```python
  sys.path.insert(0, str(Path(__file__).parent.parent))
  from core.reader import read_docx
  ```

**Naming:**
- Test files: `test_<module>.py` pattern
- Test functions: `test_<feature>` pattern (lowercase)
- Tests are organized by module:
  - `test_reader.py` for `core/reader.py`
  - `test_writer.py` for `core/writer.py`
  - `test_redliner.py` for `core/redliner.py`
  - `test_comparer.py` for `core/comparer.py`
  - `test_analyzer.py` for `core/analyzer.py`
  - `test_extractor.py` for `core/extractor.py`

**Structure:**
```
docx-tools/
├── tests/
│   ├── __init__.py (empty or minimal)
│   ├── test_reader.py
│   ├── test_writer.py
│   ├── test_redliner.py
│   ├── test_comparer.py
│   ├── test_analyzer.py
│   ├── test_extractor.py
│   └── __pycache__/
└── core/
    └── ...
```

## Test Structure

**Suite Organization:**
```python
# Standard pytest fixture pattern with tmp_path (built-in)
@pytest.fixture
def original_docx(tmp_path):
    """Create a test .docx with known content."""
    doc = Document()
    doc.add_paragraph("The Seller shall deliver the Property on the Closing Date.")
    path = tmp_path / "original.docx"
    doc.save(str(path))
    return path


# Test function directly imports and tests
def test_redline_docx_creates_output(original_docx, tmp_path):
    from core.redliner import redline_docx
    revisions = {
        "p_1": {
            "original": "The Seller shall deliver the Property on the Closing Date.",
            "revised": "The Seller shall deliver the Property on or before the Closing Date."
        }
    }
    output_path = tmp_path / "redlined.docx"
    result = redline_docx(str(original_docx), revisions, str(output_path))
    assert Path(result).exists()
```

**Patterns:**
- **Setup:** Fixtures create temporary documents in `tmp_path` (pytest's built-in temp directory)
- **Teardown:** Automatic cleanup via tmp_path (no explicit cleanup needed)
- **Assertion:** Direct `assert` statements on return values and side effects (file existence, content)

## Mocking

**Framework:** No mocking framework configured (no unittest.mock, pytest-mock imports observed)

**Patterns:**
- Real document fixtures used instead of mocks
- Example: `test_reader.py` creates actual .docx files with `Document()` and verifies parsing
- Word document XML manipulated directly via python-docx library, not mocked
- File I/O tested against real files in `tmp_path`

**What to Mock:**
- Not needed; codebase designed to test against real document objects

**What NOT to Mock:**
- python-docx Document objects (test against real instances)
- Filesystem operations (use tmp_path fixture)
- Regex and text processing (test with real strings)

## Fixtures and Factories

**Test Data:**
- Fixtures create minimal valid .docx documents with representative content
- From `test_reader.py`:
  ```python
  @pytest.fixture
  def sample_docx(tmp_path):
      """Create a minimal test .docx file."""
      doc = Document()
      doc.add_heading("PURCHASE AND SALE AGREEMENT", level=1)
      doc.add_paragraph("This Purchase and Sale Agreement...")
      doc.add_heading("Article I: Definitions", level=2)
      doc.add_paragraph("1.1 \"Property\" means the real property...")
      path = tmp_path / "test_contract.docx"
      doc.save(str(path))
      return path
  ```

- From `test_comparer.py` - multiple versions for diff testing:
  ```python
  @pytest.fixture
  def two_versions(tmp_path):
      """Create two versions of a document."""
      doc1 = Document()
      doc1.add_paragraph("The Seller shall deliver...")
      path1 = tmp_path / "v1.docx"
      doc1.save(str(path1))

      doc2 = Document()
      doc2.add_paragraph("The Seller shall deliver on or before...")
      path2 = tmp_path / "v2.docx"
      doc2.save(str(path2))
      return path1, path2
  ```

**Location:**
- Fixtures defined at top of each test file
- Shared fixture pattern: each test file has its own fixtures (no conftest.py for sharing)

## Coverage

**Requirements:** No coverage requirements enforced (no coverage configuration in pyproject.toml)

**View Coverage:** Not configured; manual testing approach

## Test Types

**Unit Tests:**
- **Scope:** Individual function behavior with real inputs/outputs
- **Approach:**
  - Test successful operation paths (happy path)
  - Test edge cases (empty documents, no changes, malformed content)
  - Test return value structure and content
- **Example from `test_reader.py`:**
  ```python
  def test_read_docx_returns_dict(sample_docx):
      from core.reader import read_docx
      result = read_docx(str(sample_docx))
      assert isinstance(result, dict)
      assert "content" in result
      assert "metadata" in result
  ```

**Integration Tests:**
- **Scope:** Multiple modules working together (reader → analyzer, comparer → redliner)
- **Approach:**
  - Read document, verify structure extraction works
  - Compare two documents, optionally generate redlined output
  - Verify transitive dependencies work
- **Example from `test_comparer.py`:**
  ```python
  def test_compare_with_redline_output(two_versions, tmp_path):
      from core.comparer import compare_docx
      path1, path2 = two_versions
      redline_path = tmp_path / "comparison.docx"
      result = compare_docx(str(path1), str(path2), redline_output=str(redline_path))
      assert redline_path.exists()
      assert "redline_path" in result
  ```

**E2E Tests:**
- Not present; no separate E2E test suite
- Integration tests serve this role (full document processing)

## Common Patterns

**Async Testing:**
- Not applicable; no async operations in codebase

**Error Testing:**
```python
def test_read_docx_raises_on_missing_file():
    from core.reader import read_docx
    with pytest.raises(FileNotFoundError):
        read_docx("/nonexistent/path.docx")
```

Note: Explicit error tests not shown in existing test files but pattern would follow above.

## Test Execution Order

**Dependency handling:**
- Tests are independent; no shared state or ordering dependencies
- Each test creates fresh tmp_path fixtures
- Tests can run in any order or in parallel (pytest -n)

## Notable Test Patterns

**Paragraph ID Verification:**
- Tests verify paragraph numbering is sequential: `assert p["id"].startswith("p_")`
- Used across reader, analyzer, extractor tests
- Example from `test_reader.py`:
  ```python
  for p in paragraphs:
      assert p["id"].startswith("p_")
      assert "text" in p
  ```

**Structural Validation:**
- Tests check that parsed output contains expected keys
- Example from `test_analyzer.py`:
  ```python
  assert "risk_categories" in result
  assert "provisions_by_concept" in result
  assert "representation" in result
  ```

**File Creation Verification:**
- Tests assert output files exist and are readable
- Example from `test_redliner.py`:
  ```python
  result = redline_docx(str(original_docx), revisions, str(output_path))
  assert Path(result).exists()
  ```

**Document Content Preservation:**
- Tests verify unchanged paragraphs remain untouched
- Example from `test_redliner.py`:
  ```python
  doc = Document(str(output_path))
  assert "Purchase Price" in doc.paragraphs[1].text
  ```

---

*Testing analysis: 2026-02-17*
