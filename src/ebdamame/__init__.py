"""
Contains high level functions to process .docx files
"""

import gc
import logging
import sys
from io import BytesIO
from pathlib import Path

import docx
from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph

from ._docx_utils import (
    EBD_KEY_PATTERN,
    EBD_KEY_WITH_HEADING_PATTERN,
    enrich_paragraphs_with_sections,
    get_ebd_document_release_information,
    get_tables_and_paragraphs,
    is_heading,
    table_is_an_ebd_table,
    table_is_first_ebd_table,
)
from .exceptions import EbdTableNotConvertibleError, StepNumberNotFoundError, TableNotFoundError
from .models import EbdChapterInformation, EbdNoTableSection

__all__ = [
    # Exceptions
    "EbdTableNotConvertibleError",
    "StepNumberNotFoundError",
    "TableNotFoundError",
    # Models
    "EbdChapterInformation",
    "EbdNoTableSection",
    # Functions
    "get_all_ebd_keys",
    "get_document",
    "get_ebd_docx_tables",
    "get_ebd_document_release_information",
]

_logger = logging.getLogger(__name__)

_is_python_version_314 = sys.version_info[0:2] == (3, 14)
_is_manually_triggered_garbage_collection_required = _is_python_version_314

"""
I don't know the reason why, but the CI failed in Python 3.14 with the following message:
"Error: Process completed with exit code 143."
based on the commit https://github.com/Hochfrequenz/ebdamame/pull/363/commits/b6a456345d46a11fe09c6c1c32ff66e62cb1392c

The python-docx repo as of 2025-10-13 mentions one open issue which might be related:
https://github.com/python-openxml/python-docx/issues/1428
Also in the CPython repository there is an open regression bug, that maybe affects ebdamame internally:
https://github.com/python/cpython/issues/139951
So as a workaround, we trigger garbage collection manually after working with a docx file.
"""


def get_document(docx_file_path: Path) -> DocumentType:
    """
    opens and returns the document specified in the docx_file_path using python-docx
    """
    with open(docx_file_path, "rb") as docx_file:
        source_stream = BytesIO(docx_file.read())
        # Originally I tried the recipe from
        # https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-file-like-document
        # but then switched from StringIO to BytesIO (without explicit 'utf-8') because of:
        # UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 605: character maps to <undefined>
    try:
        document = docx.Document(source_stream)
        _logger.info("Successfully read the file '%s'", docx_file_path)
        return document
    finally:
        source_stream.close()


# pylint:disable=too-many-branches
def get_ebd_docx_tables(docx_file_path: Path, ebd_key: str) -> list[Table] | EbdNoTableSection:
    """
    Opens the file specified in `docx_file_path` and returns the tables that relate to the given `ebd_key`.

    This function processes the document to find tables associated with the given `ebd_key`.
    There might be more than one table for a single EBD table due to inconsistencies and manual editing during
    the creation of the documents by EDI@Energy.
    There are sections relating to the EBD key without any tables.
    In this case, the section is identified and the related paragraph is captured as a remark
    (e.g. 'Es ist das EBD E_0556 zu nutzen.' for EBD_0561).

    Args:
        docx_file_path (Path): The path to the .docx file to be processed.
        ebd_key (str): The EBD key to search for in the document.

    Returns:
        list[Table] | EbdNoTableSection: A list of `Table` objects if tables are found, or an `EbdNoTableSection` object
        if no tables are found but the section is identified and are remark is captured.

    Raises:
        TableNotFoundError: If no tables related to the given `ebd_key` are found in the document.
    """
    if EBD_KEY_PATTERN.match(ebd_key) is None:
        raise ValueError(f"The ebd_key '{ebd_key}' does not match {EBD_KEY_PATTERN.pattern}")
    document = get_document(docx_file_path)

    empty_ebd_text: str | None = None  # paragraph text if there is no ebd table
    found_table_in_subsection: bool = False
    is_inside_subsection_of_requested_table: bool = False
    tables: list[Table] = []
    tables_and_paragraphs = get_tables_and_paragraphs(document)
    for table_or_paragraph in tables_and_paragraphs:
        if isinstance(table_or_paragraph, Paragraph):
            paragraph: Paragraph = table_or_paragraph
            # Assumptions:
            # 1. before each EbdTable there is a paragraph whose text starts with the respective EBD key
            # 2. there are no duplicates
            is_ebd_heading_of_requested_ebd_key = paragraph.text.startswith(ebd_key)
            if is_inside_subsection_of_requested_table and is_heading(paragraph):
                _logger.warning("No EBD table found in subsection for: '%s'", ebd_key)
                break
            if is_inside_subsection_of_requested_table and paragraph.text.strip() != "":
                if empty_ebd_text is None:
                    # the first text paragraph after we found the correct section containing the ebd key
                    empty_ebd_text = paragraph.text.strip()
                else:
                    empty_ebd_text += ("\n") + paragraph.text.strip()
            is_inside_subsection_of_requested_table = (
                is_ebd_heading_of_requested_ebd_key or is_inside_subsection_of_requested_table
            )
        if isinstance(table_or_paragraph, Table) and is_inside_subsection_of_requested_table:
            found_table_in_subsection = True
        if (
            isinstance(table_or_paragraph, Table)
            and is_inside_subsection_of_requested_table
            and table_is_an_ebd_table(table_or_paragraph)
            and table_is_first_ebd_table(table_or_paragraph)
        ):
            table: Table = table_or_paragraph
            tables.append(table)
            # Now we have to check if the EBD table spans multiple pages, and _maybe_ we have to collect more tables.
            # The funny thing is: Sometimes the authors create multiple tables split over multiple lines which belong
            # together, sometimes they create 1 proper table that spans multiple pages.
            # The latter case (1 docx table spanning >1 pages) is transparent to the extraction logic; i.e. python-docx
            # treats a single table that spans multiple pages just the same as a table on only 1 page.
            for next_item in tables_and_paragraphs:  # start iterating from where the outer loop paused
                if isinstance(next_item, Table):
                    # this is the case that the authors created multiple single tables on single adjacent pages
                    # if table_is_an_ebd_table(table):
                    if table_is_an_ebd_table(next_item):
                        tables.append(next_item)
                elif isinstance(next_item, Paragraph):
                    if next_item.text.startswith("S_") or next_item.text.startswith("E_"):
                        # this is the case that the authors created 1 table that spans multiple pages
                        # and we're done collecting tables for this EBD key
                        break
                    continue
                else:
                    break  # inner loop because if no other table will follow
                    # we're done collecting the tables for this EBD key
        if is_inside_subsection_of_requested_table and len(tables) > 0:  # this means: we found the table
            # break the outer loop, too; no need to iterate any further
            break
    if not any(tables):
        if not is_inside_subsection_of_requested_table:
            raise TableNotFoundError(ebd_key=ebd_key)
        if empty_ebd_text is None:
            if found_table_in_subsection:
                # probably there is an error while scraping the tables
                raise TableNotFoundError(ebd_key=ebd_key)
            return EbdNoTableSection(ebd_key=ebd_key, remark="")
        return EbdNoTableSection(ebd_key=ebd_key, remark=empty_ebd_text.strip())
    try:
        return tables
    finally:
        if _is_manually_triggered_garbage_collection_required:
            del document
            gc.collect()


def get_all_ebd_keys(docx_file_path: Path) -> dict[str, tuple[str, EbdChapterInformation]]:
    """
    Extract all EBD keys from the given file.
    Returns a dictionary with all EBD keys as keys and the respective EBD titles as values.
    E.g. key: "E_0003", value: "Bestellung der Aggregationsebene RZ prüfen"
    """
    document = get_document(docx_file_path)
    result: dict[str, tuple[str, EbdChapterInformation]] = {}
    for paragraph, ebd_kapitel in enrich_paragraphs_with_sections(document.paragraphs):
        match = EBD_KEY_WITH_HEADING_PATTERN.match(paragraph.text)
        if match is None:
            contains_ebd_number = paragraph.text.lstrip().startswith("E_")
            if contains_ebd_number:
                _logger.warning("Found EBD number but could not match: '%s'", paragraph.text)
            continue
        ebd_key = match.groupdict()["key"]
        title = match.groupdict()["title"]
        result[ebd_key] = (title, ebd_kapitel)
        _logger.debug("Found EBD %s: '%s' (%s)", ebd_key, title, ebd_kapitel)
    _logger.info("%i EBD keys have been found", len(result))
    try:
        return result
    finally:
        if _is_manually_triggered_garbage_collection_required:
            del document
            gc.collect()
