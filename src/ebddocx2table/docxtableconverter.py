"""
This a docstring for the module.
"""
import re
from enum import Enum
from itertools import cycle
from typing import Generator, List, Literal, Optional, Tuple, Union

from docx.table import Table, _Cell, _Row  # type:ignore[import]
from ebdtable2graph import EbdTable, EbdTableRow, EbdTableSubRow
from ebdtable2graph.models.ebd_table import EbdCheckResult, EbdTableMetaData


def _is_pruefende_rolle_cell(cell: _Cell) -> bool:
    """ "
    Returns true iff the cell mentions the market role that is responsible for applying this entscheidungsbaum
    """
    return cell.text.startswith("Prüfende Rolle: ")


def _sort_columns_in_row(docx_table_row: _Row) -> Generator[_Cell, None, None]:
    """
    The internal structure of the table rows is not as you'd expect it to be as soon as there are merged columns.
    This problem is described in https://github.com/python-openxml/python-docx/issues/970#issuecomment-877386927 .
    We apply the workaround described in the GithHub issue.
    """
    for table_column in docx_table_row._tr.tc_lst:  # pylint:disable=protected-access
        yield _Cell(table_column, docx_table_row.table)


_subsequent_step_pattern = re.compile(r"^(?P<bool>(?:ja)|(?:nein))\s*(?P<subsequent_step_number>(?:\d)|ende)?")


def _cell_to_bool(cell: _Cell) -> Tuple[bool, Optional[str]]:
    cell_text = cell.text.lower().strip()
    match = _subsequent_step_pattern.match(cell_text)
    if not match:
        raise ValueError(f"The cell content '{cell_text}' does not belong to a ja/nein cell")
    group_dict = match.groupdict()
    boolean = group_dict["bool"] == "ja"
    subsequent_step_number = group_dict["subsequent_step_number"]
    if subsequent_step_number == "ende":
        subsequent_step_number = "Ende"
    return boolean, subsequent_step_number


class _EbdSubRowPosition(Enum):
    """
    describes the position of a subrow in the Docx Table
    """

    UPPER = 1  #: the upper sub row
    LOWER = 2  #: the lower sub row


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class DocxTableConverter:
    """
    converts docx tables to EbdTables
    """

    def __init__(self, docx_table: Table, ebd_key: str, chapter: str, sub_chapter: str):
        """
        the constructor initializes the instance and reads some metadata from the table header
        """
        self._docx_table = docx_table
        self._column_index_step_number: int
        self._column_index_description: int
        self._column_index_check_result: int
        self._column_index_result_code: int
        self._column_index_note: int
        self._row_index_last_header: Literal[0, 1]  # either 0  or 1
        for row_index in range(0, 2):  # just check the first two rows in the constructor
            for column_index, table_cell in enumerate(docx_table.row_cells(row_index)):
                if row_index == 0 and _is_pruefende_rolle_cell(table_cell):
                    role = table_cell.text.split(":")[1].strip()
                    break  # because the prüfende rolle is always a full row with identical column cells
                if table_cell.text == "Nr.":
                    self._column_index_step_number = column_index
                    self._row_index_last_header = row_index  # type:ignore[assignment]
                elif table_cell.text == "Prüfschritt":
                    self._column_index_description = column_index
                elif table_cell.text == "Prüfergebnis":
                    self._column_index_check_result = column_index
                elif table_cell.text == "Code":
                    self._column_index_result_code = column_index
                elif table_cell.text == "Hinweis":
                    self._column_index_note = column_index
        self._metadata = EbdTableMetaData(ebd_code=ebd_key, sub_chapter=sub_chapter, chapter=chapter, role=role)

    def convert_docx_table_to_ebd_table(self) -> EbdTable:
        """
        Converts the raw docx table of an EBD to an EbdTable.
        The latter contains the same data but in an easily accessible format that can be used to e.g. plot real graphs.
        """
        rows: List[EbdTableRow] = []
        sub_rows: List[EbdTableSubRow] = []
        for table_row, sub_row_position in zip(
            self._docx_table.rows[self._row_index_last_header + 1 :],
            cycle([_EbdSubRowPosition.UPPER, _EbdSubRowPosition.LOWER]),
        ):
            row_cells = list(_sort_columns_in_row(table_row))
            if sub_row_position == _EbdSubRowPosition.UPPER:
                # clear list every second entry
                sub_rows = []
                step_number = row_cells[self._column_index_step_number].text.strip()
                description = row_cells[self._column_index_description].text.strip()
            boolean_outcome, subsequent_step_number = _cell_to_bool(row_cells[self._column_index_check_result])
            result_code = row_cells[self._column_index_result_code].text.strip()
            note = row_cells[self._column_index_note].text.strip()
            sub_row = EbdTableSubRow(
                check_result=EbdCheckResult(subsequent_step_number=subsequent_step_number, result=boolean_outcome),
                result_code=result_code or None,
                note=note or None,
            )
            sub_rows.append(sub_row)
            if sub_row_position == _EbdSubRowPosition.LOWER:
                row = EbdTableRow(
                    description=description,
                    step_number=step_number,
                    sub_rows=sub_rows,
                )
                rows.append(row)
        result = EbdTable(
            rows=rows,
            metadata=self._metadata,
        )
        return result
