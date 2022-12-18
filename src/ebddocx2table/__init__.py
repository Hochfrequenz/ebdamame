"""
Contains high level functions to process .docx files
"""
import re
from io import BytesIO
from pathlib import Path
from typing import Dict, Generator, List, Union

from docx import Document  # type:ignore[import]
from docx.oxml import CT_P, CT_Tbl  # type:ignore[import]
from docx.table import Table  # type:ignore[import]
from docx.text.paragraph import Paragraph  # type:ignore[import]


def get_document(docx_file_path: Path) -> Document:
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
        document = Document(source_stream)
        return document
    finally:
        source_stream.close()


def _get_tables_and_paragaphs(document: Document) -> Generator[Union[Table, Paragraph], None, None]:
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


_ebd_key_pattern = re.compile(r"^E_\d{4}$")
_ebd_key_with_heading_pattern = re.compile(r"^(?P<key>E_\d{4})_(?P<title>.*)\s*$")


def get_ebd_docx_tables(docx_file_path: Path, ebd_key: str) -> List[Table]:
    """
    Opens the file specified in docx_file_path and returns the table that relates to the given ebd_key.
    Raises an ValueError if the table was not found.
    """
    if _ebd_key_pattern.match(ebd_key) is None:
        raise ValueError(f"The ebd_key '{ebd_key}' does not match {_ebd_key_pattern.pattern}")
    document = get_document(docx_file_path)

    next_table_is_requested_table: bool = False
    tables: List[Table] = []
    tables_and_paragraphs = _get_tables_and_paragaphs(document)
    for table_or_paragraph in tables_and_paragraphs:
        if isinstance(table_or_paragraph, Paragraph):
            paragraph: Paragraph = table_or_paragraph
            # Assumptions:
            # 1. before each EbdTable there is a paragraph whose text starts with the respective EBD key
            # 2. there are no duplicates
            next_table_is_requested_table = paragraph.text.startswith(ebd_key)
        if isinstance(table_or_paragraph, Table) and next_table_is_requested_table:
            table: Table = table_or_paragraph
            tables.append(table)
            # Now we have to check if the EBD table spans multiple pages and _maybe_ we have to collect more tables.
            # The funny thing is: Sometimes the authors create multiple tables split over multiple lines which belong
            # together, sometimes they create 1 proper table that spans multiple pages. This we won't notice here.
            for next_item in tables_and_paragraphs:  # start iterating from where the outer loop paused
                if isinstance(next_item, Table):
                    # this is the case that the authors created multiple single tables on single adjacent pages
                    tables.append(next_item)
                elif isinstance(next_item, Paragraph) and not next_item.text.strip():
                    # sometimes the authors add blank lines before they continue with the next table
                    continue
                else:
                    break  # because if no other table follows, we're done collecting the tables for this EBD key
    if len(tables) == 0:
        raise ValueError(f"EBD Table '{ebd_key}' was not found.")
    return tables


def get_all_ebd_keys(docx_file_path: Path) -> Dict[str, str]:
    """
    Extract all EBD keys from the given file.
    Returns a dictionary with all EBD keys as keys and the respective EBD titles as values.
    E.g. key: "E_0003", value: "Bestellung der Aggregationsebene RZ prüfen"
    """
    document = get_document(docx_file_path)
    result: Dict[str, str] = {}
    for paragraph in document.paragraphs:
        match = _ebd_key_with_heading_pattern.match(paragraph.text)
        if match is None:
            continue
        ebd_key = match.groupdict()["key"]
        title = match.groupdict()["title"]
        result[ebd_key] = title
    return result
