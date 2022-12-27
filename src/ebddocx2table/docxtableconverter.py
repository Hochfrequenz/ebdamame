"""
This module converts tables read from the docx file into a format that is easily accessible (but still a table).
"""
import re
from enum import Enum
from itertools import cycle, groupby
from typing import Generator, List, Literal, Optional, Tuple

from docx.table import Table, _Cell, _Row  # type:ignore[import]
from ebdtable2graph.models import EbdTable, EbdTableRow, EbdTableSubRow
from ebdtable2graph.models.ebd_table import EbdCheckResult, EbdTableMetaData, MultiStepInstruction
from more_itertools import first


def _is_pruefende_rolle_cell_text(text: str) -> bool:
    """ "
    Returns true iff the given text mentions the market role that is responsible for applying this entscheidungsbaum
    """
    return text.startswith("Prüfende Rolle: ")


def _sort_columns_in_row(docx_table_row: _Row) -> Generator[_Cell, None, None]:
    """
    The internal structure of the table rows is not as you'd expect it to be as soon as there are merged columns.
    This problem is described in https://github.com/python-openxml/python-docx/issues/970#issuecomment-877386927 .
    We apply the workaround described in the GithHub issue.
    """
    for table_column in docx_table_row._tr.tc_lst:  # pylint:disable=protected-access
        yield _Cell(table_column, docx_table_row.table)


_subsequent_step_pattern = re.compile(r"^(?P<bool>(?:ja)|(?:nein))\s*(?P<subsequent_step_number>(?:\d+\*?)|ende)?")


def _read_subsequent_step_cell(cell: _Cell) -> Tuple[bool, Optional[str]]:
    """
    Parses the cell that contains the outcome and the subsequent step (e.g. "ja➡5" where "5" is the subsequent step
    number).
    """
    cell_text = cell.text.lower().strip()
    # we first match against the lower case cell text; then we convert the "ende" to upper case again in the end.
    # this is to avoid confusion with "ja" vs. "Ja"
    match = _subsequent_step_pattern.match(cell_text)
    if not match:
        raise ValueError(f"The cell content '{cell_text}' does not belong to a ja/nein cell")
    group_dict = match.groupdict()
    result_is_ja = group_dict["bool"] == "ja"
    subsequent_step_number = group_dict["subsequent_step_number"]
    if subsequent_step_number == "ende":
        subsequent_step_number = "Ende"
    return result_is_ja, subsequent_step_number


class _EbdSubRowPosition(Enum):
    """
    Describes the position of a subrow in the Docx Table.
    Most rows in the EBD table have two subrows where each subrow denoted one "ja"/"nein" answer to the question in the
    description column (left to the subrow). We use this enum to toggle upper➡lower➡upper➡lower ... when iterating
    over the rows. In the end each EbdTableRow shall contain two EbdTableSubRows of which the first is an "UPPER" and
    the second is a "LOWER" subrow. As soon as the "LOWER" subrow appeared we flush the two subrows into a EbdTableRow,
    whenever the "UPPER" subrow appears, we reset the subrow list (see loop in convert_docx_table_to_ebd_table).
    In EBD E_0003 ("nein", "A01") is the UPPER and ("ja->2",None) is the lower subrow.
    """

    UPPER = 1  #: the upper sub row
    LOWER = 2  #: the lower sub row


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class DocxTableConverter:
    """
    converts docx tables to EbdTables
    """

    def __init__(self, docx_tables: List[Table], ebd_key: str, chapter: str, sub_chapter: str):
        """
        the constructor initializes the instance and reads some metadata from the (first) table header
        """
        self._docx_tables = docx_tables
        self._column_index_step_number: int
        self._column_index_description: int
        self._column_index_check_result: int
        self._column_index_result_code: int
        self._column_index_note: int
        self._row_index_last_header: Literal[0, 1]  # either 0  or 1
        for row_index in range(0, 2):  # the first two lines/rows are the header of the table.
            # In the constructor we just want to read the metadata from the table.
            # For this purpose the first two lines are enough.
            # Now it feels natural, to loop over the cells/columns of the first row, but before we do so, we have to
            # remove duplicates. Although there are usually only 5 columns visible, technically there might be even 8.
            # In these cases (e.g. for E_0453) columns like 'Prüfergebnis' simply occur twice in the docx table header.
            distinct_cell_texts: List[str] = [
                x[0] for x in groupby(first(docx_tables).row_cells(row_index), lambda cell: cell.text)
            ]
            for column_index, table_cell_text in enumerate(distinct_cell_texts):
                if row_index == 0 and _is_pruefende_rolle_cell_text(table_cell_text):
                    role = table_cell_text.split(":")[1].strip()
                    break  # because the prüfende rolle is always a full row with identical column cells
                if table_cell_text == "Nr.":
                    self._column_index_step_number = column_index
                    # In most of the cases this will be 1,
                    # but it can be 0 if the first row does _not_ contain the "Prüfende Rolle".
                    self._row_index_last_header = row_index  # type:ignore[assignment]
                elif table_cell_text == "Prüfschritt":
                    self._column_index_description = column_index
                elif table_cell_text == "Prüfergebnis":
                    self._column_index_check_result = column_index
                elif table_cell_text == "Code":
                    self._column_index_result_code = column_index
                elif table_cell_text == "Hinweis":
                    self._column_index_note = column_index
        self._metadata = EbdTableMetaData(ebd_code=ebd_key, sub_chapter=sub_chapter, chapter=chapter, role=role)

    # I see that there are quite a few local variables, but honestly see no reason to break it down any further.
    # pylint:disable=too-many-locals, too-many-arguments
    def _handle_single_table(
        self,
        table: Table,
        multi_step_instructions: List[MultiStepInstruction],
        row_offset: int,
        rows: List[EbdTableRow],
        sub_rows: List[EbdTableSubRow],
    ) -> None:
        """
        Handles a single table (out of possible multiple tables for 1 EBD).
        The results are written into rows, sub_rows and multi_step_instructions. Those will be modified.
        """
        upper_lower_iterator = cycle([_EbdSubRowPosition.UPPER, _EbdSubRowPosition.LOWER])
        for table_row, sub_row_position in zip(
            table.rows[row_offset:],
            upper_lower_iterator,
        ):
            row_cells = list(_sort_columns_in_row(table_row))
            if len(row_cells) <= self._column_index_description:
                # These are the multi-column rows that span that contain stuff like
                # "Alle festgestellten Antworten sind anzugeben, soweit im Format möglich (maximal 8 Antwortcodes)*."
                _ = next(upper_lower_iterator)  # reset the iterator
                multi_step_instruction_text = row_cells[0].text
                # we store the text in the local variable for now because we don't yet know the next step number
                continue
            if sub_row_position == _EbdSubRowPosition.UPPER:
                # clear list every second entry
                sub_rows = []
                step_number = row_cells[self._column_index_step_number].text.strip()
                description = row_cells[self._column_index_description].text.strip()
            boolean_outcome, subsequent_step_number = _read_subsequent_step_cell(
                row_cells[self._column_index_check_result]
            )
            sub_row = EbdTableSubRow(
                check_result=EbdCheckResult(subsequent_step_number=subsequent_step_number, result=boolean_outcome),
                result_code=row_cells[self._column_index_result_code].text.strip() or None,
                note=row_cells[self._column_index_note].text.strip() or None,
            )
            sub_rows.append(sub_row)
            if sub_row_position == _EbdSubRowPosition.LOWER:
                row = EbdTableRow(
                    description=description,
                    step_number=step_number,
                    sub_rows=sub_rows,
                )
                if "multi_step_instruction_text" in locals():
                    # if the variable with the given name is defined, then we append a multi_step_instruction, once.
                    multi_step_instructions.append(
                        MultiStepInstruction(
                            instruction_text=multi_step_instruction_text,
                            # in contrast to the row in which we found the bare multi_step_instruction_text
                            # we know the step_number here. This is why the detection of the instruction and the append
                            # are not in the same place.
                            first_step_number_affected=step_number,
                        )
                    )
                    del multi_step_instruction_text  # prevent adding the same instructions for all following steps
                rows.append(row)

    def convert_docx_tables_to_ebd_table(self) -> EbdTable:
        """
        Converts the raw docx tables of an EBD to an EbdTable.
        The latter contains the same data but in an easily accessible format that can be used to e.g. plot real graphs.
        """
        rows: List[EbdTableRow] = []
        sub_rows: List[EbdTableSubRow] = []
        multi_step_instructions: List[MultiStepInstruction] = []
        for table_index, table in enumerate(self._docx_tables):
            offset: int = 0
            if table_index == 0:
                offset = self._row_index_last_header + 1
            self._handle_single_table(table, multi_step_instructions, offset, rows, sub_rows)
        result = EbdTable(rows=rows, metadata=self._metadata, multi_step_instructions=multi_step_instructions or None)
        return result
