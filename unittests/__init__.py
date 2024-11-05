"""
This file is here, because this allows for best de-coupling of tests and application/library logic.
Further reading: https://docs.pytest.org/en/6.2.x/goodpractices.html#tests-outside-application-code
"""

from pathlib import Path
from typing import Dict, List, Tuple

from docx.document import Document as DocumentType
from docx.table import Table

import ebdamame


def get_document(datafiles, filename: str) -> DocumentType:
    """
    a datafiles compatible wrapper around ebdamame.get_document
    """
    path = datafiles / Path(filename)
    return ebdamame.get_document(path)


def get_ebd_docx_tables(datafiles, filename: str, ebd_key: str) -> List[Table] | str:
    """
    a datafiles compatible wrapper around ebdamame.get_ebd_docx_tables
    """
    path = datafiles / Path(filename)
    return ebdamame.get_ebd_docx_tables(path, ebd_key=ebd_key)


def get_all_ebd_keys(datafiles, filename: str) -> Dict[str, Tuple[str, ebdamame.EbdChapterInformation]]:
    """
    a datafiles compatible wrapper around ebdamame.get_all_ebd_keys
    """
    path = datafiles / Path(filename)
    return ebdamame.get_all_ebd_keys(path)
