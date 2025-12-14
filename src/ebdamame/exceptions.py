"""
Exception classes for ebdamame.
"""


class TableNotFoundError(Exception):
    """
    An error that is raised when a requested table was not found.
    """

    def __init__(self, ebd_key: str):
        self.ebd_key = ebd_key


class EbdTableNotConvertibleError(Exception):
    """
    An error that is raised when an EBD table is found but cannot be converted
    to the EbdTable model due to unsupported format.

    Example: E_0060 from EBD v4.2 uses "--" values instead of "ja/nein" outcomes,
    which the current converter does not support.

    See: https://github.com/Hochfrequenz/ebdamame/issues/23
    """

    def __init__(self, ebd_key: str, reason: str):
        self.ebd_key = ebd_key
        self.reason = reason
        super().__init__(f"EBD table '{ebd_key}' cannot be converted: {reason}")


class StepNumberNotFoundError(Exception):
    """
    An error that is raised when no valid step number can be found in the table row.

    This typically indicates a malformed or unsupported table structure where
    the expected step number column (e.g., "1", "2", "3*") is missing or unreadable.

    Root cause analysis (E_1020 in v3.5):
    The EBD section contains a "changelog" table (with columns like "Änd-ID", "Ort",
    "Änderungen", etc.) that is incorrectly identified as an EBD table because it
    contains cells starting with "Hinweis:" which triggers `_cell_is_probably_from_an_ebd_cell`.
    The fix should improve `_table_is_an_ebd_table` detection to exclude changelog tables.
    """

    def __init__(self, ebd_key: str):
        self.ebd_key = ebd_key
        super().__init__(f"No cell containing a valid step number found in EBD table '{ebd_key}'")
