"""
This file is here, because this allows for best de-coupling of tests and application/library logic.
Further reading: https://docs.pytest.org/en/6.2.x/goodpractices.html#tests-outside-application-code
"""
from pathlib import Path
from typing import Dict, List, Tuple

from docx import Document  # type:ignore[import]
from docx.table import Table  # type:ignore[import]

import ebddocx2table


def get_document(datafiles, filename: str) -> Document:
    """
    a datafiles compatible wrapper around ebddocx2table.get_document
    """
    path = datafiles / Path(filename)
    return ebddocx2table.get_document(path)


def get_ebd_docx_tables(datafiles, filename: str, ebd_key: str) -> List[Table]:
    """
    a datafiles compatible wrapper around ebddocx2table.get_ebd_docx_tables
    """
    path = datafiles / Path(filename)
    return ebddocx2table.get_ebd_docx_tables(path, ebd_key=ebd_key)


def get_all_ebd_keys(datafiles, filename: str) -> Dict[str, Tuple[str, ebddocx2table.EbdChapterInformation]]:
    """
    a datafiles compatible wrapper around ebddocx2table.get_all_ebd_keys
    """
    path = datafiles / Path(filename)
    return ebddocx2table.get_all_ebd_keys(path)
