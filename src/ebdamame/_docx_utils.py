"""
Private helper functions and constants for docx processing.

This module is internal - do not import directly from external code.
"""

import itertools
import logging
import re
from datetime import date
from typing import Generator, Iterable, Optional, Union

from docx.document import Document as DocumentType
from docx.oxml.document import CT_Body
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from rebdhuhn.models.ebd_table import EbdDocumentReleaseInformation

from .models import EbdChapterInformation

_logger = logging.getLogger(__name__)

# Regex patterns for EBD key detection
EBD_KEY_PATTERN = re.compile(r"^E_\d{4}$")
EBD_KEY_WITH_HEADING_PATTERN = re.compile(r"^(?P<key>E_\d{4})_?(?P<title>.*)\s*$")

EBD_CELL_PATTERN = re.compile(r"^(?:ja|nein)\s*(?:Ende|\d+)$")
"""
Any EBD table shall contain at least one cell that matches this pattern.
"""

DOCX_ARROW_CHAR = "\uf0e0"
"""
U+F0E0: Private Use Area character representing a right arrow in DOCX documents.
This character is used by MS Word to render arrows (e.g., "ja → 5") in EBD tables.
It appears in cells like "ja  5" to indicate the subsequent step number.
"""


def get_tables_and_paragraphs(document: DocumentType) -> Generator[Union[Table, Paragraph], None, None]:
    """
    Yields tables and paragraphs from the given document in the order in which they occur in the document.
    This is helpful because document.tables and document.paragraphs are de-coupled and give you no information which
    paragraph follows which table.
    """
    parent_elements = document.element.body
    for item in parent_elements.iterchildren():
        if isinstance(item, CT_P):
            yield Paragraph(item, document)
        elif isinstance(item, CT_Tbl):
            yield Table(item, document)
        else:
            _logger.debug("Item %s is neither Paragraph nor Table", str(item))


def cell_is_probably_from_an_ebd_cell(cell: _Cell) -> bool:
    """Check if a cell likely belongs to an EBD table based on its content."""
    if DOCX_ARROW_CHAR in cell.text:
        return True
    if cell.text in {"ja", "nein"}:
        return True
    if "à" in cell.text:
        # the rightarrow in wrong encoding
        return True
    if EBD_CELL_PATTERN.match(cell.text):
        return True
    if cell.text.strip().startswith("Cluster:") or cell.text.startswith("Hinweis:"):
        return True
    return False


def table_is_an_ebd_table(table: Table) -> bool:
    """
    Returns true iff the table "looks like" an EB-Table.
    This is to distinguish between tables that are inside the same subsection that describes an EBD but are not part
    of the decision tree at all (e.g. in E_0406 the tables about Artikel-IDs).
    """
    if table_is_first_ebd_table(table):
        return True
    for row in table.rows:
        try:
            for cell in row.cells:
                if cell_is_probably_from_an_ebd_cell(cell):
                    return True
        except IndexError:  # don't ask me why this happens; It's the internals of python-docx
            continue
    return False


def table_is_first_ebd_table(table: Table) -> bool:
    """
    Returns true if the first row of a table contains "Prüfende Rolle".
    We assume that each EBD table has a header row with
    "Prüfende Rolle" in the first column.
    """
    return "prüfende rolle" in table.rows[0].cells[0].text.lower()


def is_heading(paragraph: Paragraph) -> bool:
    """
    Returns True if the paragraph is a heading.
    """
    return paragraph.style is not None and paragraph.style.style_id in {
        "berschrift1",
        "berschrift2",
        "berschrift3",
    }


def enrich_paragraphs_with_sections(
    paragraphs: Iterable[Paragraph],
) -> Generator[tuple[Paragraph, EbdChapterInformation], None, None]:
    """
    Yield each paragraph + the "Kapitel" in which it is found.
    """
    chapter_counter = itertools.count(start=1)
    chapter = 1
    chapter_title: Optional[str] = None
    section_counter = itertools.count(start=1)
    section = 1
    section_title: Optional[str] = None
    subsection_counter = itertools.count(start=1)
    subsection = 1
    subsection_title: Optional[str] = None
    for paragraph in paragraphs:
        # since pyton-docx 1.1.2 there are type hints; seems like the style is not guaranteed to be not None
        match paragraph.style.style_id:  # type:ignore[union-attr]
            case "berschrift1":
                chapter = next(chapter_counter)
                chapter_title = paragraph.text.strip()
                section_counter = itertools.count(start=1)
                section_title = None
                subsection_counter = itertools.count(start=1)
                subsection_title = None
            case "berschrift2":
                section = next(section_counter)
                section_title = paragraph.text.strip()
                subsection_counter = itertools.count(start=1)
                subsection_title = None
            case "berschrift3":
                subsection = next(subsection_counter)
                subsection_title = paragraph.text.strip()
        location = EbdChapterInformation(
            chapter=chapter,
            section=section,
            subsection=subsection,
            chapter_title=chapter_title,
            section_title=section_title,
            subsection_title=subsection_title,
        )
        _logger.debug("Handling Paragraph %i.%i.%i", chapter, section, subsection)
        yield paragraph, location


_STAND_PATTERN = re.compile(r"^Stand:\s*(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})\s*$")
"""Pattern to match 'Stand: DD.MM.YYYY' paragraphs on the title page."""

_DATE_PATTERN = re.compile(r"^(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})$")
"""Pattern to match German date format DD.MM.YYYY."""


def _parse_german_date(date_str: str) -> Optional[date]:
    """
    Parse a German date string (DD.MM.YYYY) into a date object.
    Returns None if the string doesn't match the expected format or contains invalid date values.
    """
    match = _DATE_PATTERN.match(date_str.strip())
    if match:
        day = int(match.group("day"))
        month = int(match.group("month"))
        year = int(match.group("year"))
        try:
            return date(year, month, day)
        except ValueError:
            # Invalid date values (e.g., February 30)
            _logger.warning("Invalid date values in '%s': day=%d, month=%d, year=%d", date_str, day, month, year)
            return None
    return None


def _get_table_cell_texts(table_element: CT_Tbl) -> list[list[str]]:
    """
    Extract cell texts from a table element using low-level XML API.

    The python-docx Table class doesn't handle merged cells or structured document tags (SDT)
    correctly in all cases, so we use the underlying lxml API with recursive searches to
    reliably extract cell contents.

    Note: We use iter() with the namespace-qualified tag to find all descendant elements,
    which correctly handles cells nested inside SDT elements (common in Word's title pages).

    Returns a list of rows, where each row is a list of cell text strings.
    """
    rows_data: list[list[str]] = []
    for row in table_element.findall(qn("w:tr")):
        # Use iter to find ALL w:tc elements recursively, including those inside w:sdt elements
        # This is needed because the title page table uses SDT elements for dropdowns
        cell_texts = [
            "".join(t_elem.text for t_elem in cell.iter(qn("w:t")) if t_elem.text) for cell in row.iter(qn("w:tc"))
        ]
        rows_data.append(cell_texts)
    return rows_data


def _extract_stand_date_from_body(body: CT_Body) -> Optional[date]:
    """Extract the 'Stand:' date from the document body."""
    for para_elem in body.iter(qn("w:p")):
        para_text = "".join(t_elem.text for t_elem in para_elem.iter(qn("w:t")) if t_elem.text).strip()
        match = _STAND_PATTERN.match(para_text)
        if match:
            day, month, year = int(match.group("day")), int(match.group("month")), int(match.group("year"))
            try:
                result = date(year, month, day)
                _logger.debug("Found Stand date: %s", result)
                return result
            except ValueError:
                _logger.warning("Invalid Stand date values: day=%d, month=%d, year=%d", day, month, year)
                return None
    return None


def _extract_version_info_from_body(body: CT_Body) -> tuple[Optional[str], Optional[date]]:
    """Extract version and original release date from the metadata table in the document body."""
    for item in body.iterchildren():
        if not isinstance(item, CT_Tbl):
            continue
        rows_data = _get_table_cell_texts(item)
        if len(rows_data) < 2 or len(rows_data[0]) < 2:
            continue
        if rows_data[0][0].strip() != "Version:":
            continue
        version = rows_data[0][1].strip()
        _logger.debug("Found Version: %s", version)
        original_release_date = None
        if len(rows_data[1]) >= 2 and "Publikationsdatum" in rows_data[1][0].strip():
            original_release_date = _parse_german_date(rows_data[1][1].strip())
            _logger.debug("Found original release date: %s", original_release_date)
        return version, original_release_date
    return None, None


def get_ebd_document_release_information(document: DocumentType) -> Optional[EbdDocumentReleaseInformation]:
    """
    Extract release information from the title page of an EBD document.

    The title page of EDI@Energy EBD documents contains:
    - A 'Stand: DD.MM.YYYY' paragraph indicating the current release/correction date
    - A table with 'Version:' and either 'Publikationsdatum:' or 'Ursprüngliches Publikationsdatum:'

    Args:
        document: A python-docx Document object

    Returns:
        EbdDocumentReleaseInformation with version and dates extracted from the title page,
        or None if the information could not be extracted (logs a warning in this case).
    """
    return get_ebd_document_release_information_from_body(document.element.body)


def get_ebd_document_release_information_from_body(
    body: CT_Body,
) -> Optional[EbdDocumentReleaseInformation]:
    """
    Extract release information from the body element of an EBD document.

    This is an internal function that allows extracting release information
    from a document body element directly, which is useful when you only have
    access to tables (which reference their parent document via table.part.element.body).

    Args:
        body: The document body element (CT_Body)

    Returns:
        EbdDocumentReleaseInformation with version and dates extracted from the title page,
        or None if the information could not be extracted (logs a warning in this case).
    """
    try:
        release_date = _extract_stand_date_from_body(body)
        version, original_release_date = _extract_version_info_from_body(body)

        if version is None:
            _logger.warning("Could not find Version information in the document title page")
            return None

        return EbdDocumentReleaseInformation(
            version=version,
            release_date=release_date,
            original_release_date=original_release_date,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        _logger.warning("Failed to extract release information from document: %s", e)
        return None
