# Extract Private Helpers to `_docx_utils.py`

## Goal

Reduce `__init__.py` bloat by moving private helper functions and constants to a dedicated internal module.

## New Module: `_docx_utils.py`

### Functions (no underscore prefix - module is already private)

| From `__init__.py` | To `_docx_utils.py` |
|--------------------|---------------------|
| `_get_tables_and_paragraphs()` | `get_tables_and_paragraphs()` |
| `_cell_is_probably_from_an_ebd_cell()` | `cell_is_probably_from_an_ebd_cell()` |
| `_table_is_an_ebd_table()` | `table_is_an_ebd_table()` |
| `_table_is_first_ebd_table()` | `table_is_first_ebd_table()` |
| `_enrich_paragraphs_with_sections()` | `enrich_paragraphs_with_sections()` |
| `is_heading()` | `is_heading()` |

### Constants (UPPER_CASE per PEP8)

| From `__init__.py` | To `_docx_utils.py` |
|--------------------|---------------------|
| `_ebd_key_pattern` | `EBD_KEY_PATTERN` |
| `_ebd_key_with_heading_pattern` | `EBD_KEY_WITH_HEADING_PATTERN` |
| `_ebd_cell_pattern` | `EBD_CELL_PATTERN` |
| `_DOCX_ARROW_CHAR` | `DOCX_ARROW_CHAR` |

## Updated `__init__.py`

### Stays in `__init__.py`

- `get_document()` - public API
- `get_ebd_docx_tables()` - public API
- `get_all_ebd_keys()` - public API
- `_logger` - module-specific logger
- `_is_python_version_314` / `_is_manually_triggered_garbage_collection_required` - Python 3.14 GC workaround

### Updated `__all__`

```python
__all__ = [
    "EbdTableNotConvertibleError",
    "StepNumberNotFoundError",
    "TableNotFoundError",
    "EbdChapterInformation",
    "EbdNoTableSection",
    "get_all_ebd_keys",
    "get_document",
    "get_ebd_docx_tables",
]
```

Note: `is_heading` removed from public API (now internal).

## File Structure After

```
src/ebdamame/
├── __init__.py           # ~120 lines (was ~330)
├── _docx_utils.py        # ~120 lines (NEW)
├── exceptions.py
├── models.py
└── docxtableconverter.py
```

## Breaking Changes

- `is_heading()` no longer exported (was in `__all__`, now internal)
- No other breaking changes - all other public API unchanged
