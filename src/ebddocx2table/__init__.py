"""
Contains high level functions to process .docx files
"""
import re
from io import BytesIO
from pathlib import Path
from typing import Generator, Union

from docx import Document  # type:ignore[import]
from docx.oxml import CT_P, CT_Tbl  # type:ignore[import]
from docx.table import Table  # type:ignore[import]
from docx.text.paragraph import Paragraph  # type:ignore[import]


def get_document(docx_file_path: Path) -> Document:
    """
    opens and returns the document specified in the docx_file_path using python-docx
    """
    # https://python-docx.readthedocs.io/en/latest/user/documents.html#opening-a-file-like-document
    with open(docx_file_path, "rb") as docx_file:
        source_stream = BytesIO(docx_file.read())
        # switched from StringIO to BytesIO because of:
        # UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 605: character maps to <undefined>
    try:
        document = Document(source_stream)
        return document
    finally:
        source_stream.close()


def _get_tables_and_paragaphs(document: Document) -> Generator[Union[Table, Paragraph], None, None]:
    """
    Yields tables and paragraphs from the given document in the order in which they occur in the document.
    This is helpful because document.tables and documents.paragraphs are de-coupled and give you no information which
    paragraph follows which table.
    """
    parent_elements = document.element.body
    for item in parent_elements.iterchildren():
        if isinstance(item, CT_P):
            yield Paragraph(item, document)
        elif isinstance(item, CT_Tbl):
            yield Table(item, document)


_ebd_key_pattern = re.compile(r"^[SE]_\d{4}$")


def get_ebd_docx_table(docx_file_path: Path, ebd_key: str) -> Table:
    """
    Opens the file specified in docx_file_path and returns the table that relates to the given ebd_key.
    Raises an ValueError if the table was not found.
    """
    if _ebd_key_pattern.match(ebd_key) is None:
        raise ValueError(f"The ebd_key '{ebd_key}' does not match {_ebd_key_pattern.pattern}")
    document = get_document(docx_file_path)
    next_table_is_requested_table: bool = False
    for table_or_paragraph in _get_tables_and_paragaphs(document):
        if isinstance(table_or_paragraph, Paragraph):
            paragraph: Paragraph = table_or_paragraph
            # Assumptions:
            # 1. before each EbdTable there is a paragraph whose text starts with the respective EBD key
            # 2. there are no duplicates
            next_table_is_requested_table = paragraph.text.startswith(ebd_key)
        if isinstance(table_or_paragraph, Table) and next_table_is_requested_table:
            table: Table = table_or_paragraph
            return table
    raise ValueError(f"EBD Table '{ebd_key}' was not found.")
