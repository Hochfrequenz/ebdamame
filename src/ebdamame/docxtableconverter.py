"""
This module converts tables read from the docx file into a format that is easily accessible (but still a table).
"""

import logging
import re
from enum import Enum
from itertools import cycle, groupby
from typing import Generator, List, Literal, Optional, Tuple

import attrs
from docx.table import Table, _Cell, _Row
from more_itertools import first, first_true, last
from rebdhuhn.models.ebd_table import (
    _STEP_NUMBER_REGEX,
    EbdCheckResult,
    EbdTable,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    MultiStepInstruction,
)

_logger = logging.getLogger(__name__)


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


_subsequent_step_pattern = re.compile(r"^(?P<bool>(?:ja)|(?:nein))[\sà]*(?P<subsequent_step_number>(?:\d+\*?)|ende)?")

_step_number_pattern = re.compile(_STEP_NUMBER_REGEX)


def _get_index_of_first_column_with_step_number(cells: List[_Cell]) -> int:
    """
    returns the index of the first cell in cells, that contains a step number
    """
    first_step_number_cell = first_true(
        cells, pred=lambda cell: _step_number_pattern.match(cell.text.strip()) is not None
    )
    if first_step_number_cell is None:
        raise ValueError("No cell containing a valid step number found.")

    step_number_column_index = cells.index(first_step_number_cell)
    _logger.debug("The step number is in column %i", step_number_column_index)
    return step_number_column_index


def _get_use_cases(cells: List[_Cell]) -> List[str]:
    """
    Extract use cases from the given list of cells.
    May return empty list, never returns None.
    """
    index_of_step_number = _get_index_of_first_column_with_step_number(cells)
    use_cases: List[str]
    if index_of_step_number != 0:
        # "use_cases" are present; This means, that this step must only be applied for certain scenarios,
        use_cases = [c.text for c in cells[0:index_of_step_number]]
    else:
        use_cases = []
    _logger.debug("%i use cases have been found", len(use_cases))
    return use_cases  # we don't return None here because we need something that has a length in the calling code


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


# pylint:disable=too-few-public-methods
@attrs.define
class _EnhancedDocxTableLine:
    """
    A structure that primarily contains a single row from a DOCX table but also meta information about previous and
    following elements in the table. It gathers information that are not directly accessible when only looking at one
    single row.
    """

    row: _Row = attrs.field(validator=attrs.validators.instance_of(_Row))
    """
    The row that is currently being processed
    """
    sub_row_position: _EbdSubRowPosition = attrs.field(validator=attrs.validators.instance_of(_EbdSubRowPosition))
    """
    denotes if row is an upper/lower sub row
    """
    cells: List[_Cell] = attrs.field(
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(_Cell), iterable_validator=attrs.validators.instance_of(list)
        )
    )
    """
    the (sanitized) cells of the row
    """
    multi_step_instruction_text: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(str))
    )
    """
    a multistep instruction text that may be applicable to this row (if not None)
    """


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
        self._row_index_last_header: Literal[0, 1] = 1  #: the index of the last table header row
        # the index of the last header row _could_ by dynamically calculated but so far it has always been 1.
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
                    # self._row_index_last_header = row_index  # type:ignore[assignment]
                elif table_cell_text == "Prüfschritt":
                    self._column_index_description = column_index
                elif table_cell_text == "Prüfergebnis":
                    self._column_index_check_result = column_index
                elif table_cell_text == "Code":
                    self._column_index_result_code = column_index
                elif table_cell_text == "Hinweis":
                    self._column_index_note = column_index

        self._metadata = EbdTableMetaData(ebd_code=ebd_key, sub_chapter=sub_chapter, chapter=chapter, role=role)

    @staticmethod
    def _enhance_list_view(table: Table, row_offset: int) -> List[_EnhancedDocxTableLine]:
        """
        Loop over the given table and enhance the table rows with additional information.
        It spares the main loop in _handle_single_table from peeking ahead or looking back.
        """
        result: List[_EnhancedDocxTableLine] = []
        upper_lower_iterator = cycle([_EbdSubRowPosition.UPPER, _EbdSubRowPosition.LOWER])
        multi_step_instruction_text: Optional[str] = None
        for table_row, sub_row_position in zip(
            table.rows[row_offset:],
            upper_lower_iterator,
        ):
            row_cells = list(_sort_columns_in_row(table_row))
            if len(row_cells) <= 2:
                # These are the multi-column rows that span that contain stuff like
                # "Alle festgestellten Antworten sind anzugeben, soweit im Format möglich (maximal 8 Antwortcodes)*."
                _ = next(upper_lower_iterator)  # reset the iterator
                multi_step_instruction_text = row_cells[0].text
                # we store the text in the local variable for now because we don't yet know the next step number
                continue
            result.append(
                _EnhancedDocxTableLine(
                    row=table_row,
                    sub_row_position=sub_row_position,
                    multi_step_instruction_text=multi_step_instruction_text,
                    cells=row_cells,
                )
            )
            multi_step_instruction_text = None
        return result

    # I see that there are quite a few local variables, but honestly see no reason to break it down any further.
    # pylint:disable=too-many-arguments
    def _handle_single_table(
        self,
        table: Table,
        multi_step_instructions: List[MultiStepInstruction],
        row_offset: int,
        rows: list[EbdTableRow],
        sub_rows: list[EbdTableSubRow],
    ) -> None:
        """
        Handles a single table (out of possible multiple tables for 1 EBD).
        The results are written into rows, sub_rows and multi_step_instructions. Those will be modified.
        """
        use_cases: list[str] = []
        for row_index, enhanced_table_row in enumerate(self._enhance_list_view(table=table, row_offset=row_offset)):
            if enhanced_table_row.sub_row_position == _EbdSubRowPosition.UPPER:
                use_cases = _get_use_cases(enhanced_table_row.cells)
                sub_rows = []  # clear list every second entry
                step_number = enhanced_table_row.cells[len(use_cases) + self._column_index_step_number].text.strip()
                description = enhanced_table_row.cells[len(use_cases) + self._column_index_description].text.strip()
            boolean_outcome, subsequent_step_number = _read_subsequent_step_cell(
                enhanced_table_row.cells[len(use_cases) + self._column_index_check_result]
            )
            if step_number.endswith("*"):
                self._handle_single_table_star_exception(table, multi_step_instructions, row_offset, rows, row_index)
                break
            sub_row = EbdTableSubRow(
                check_result=EbdCheckResult(subsequent_step_number=subsequent_step_number, result=boolean_outcome),
                result_code=enhanced_table_row.cells[len(use_cases) + self._column_index_result_code].text.strip()
                or None,
                note=enhanced_table_row.cells[len(use_cases) + self._column_index_note].text.strip() or None,
            )
            _logger.debug(
                "Successfully read sub row %s/%s", sub_row.result_code or subsequent_step_number, boolean_outcome
            )
            sub_rows.append(sub_row)
            if enhanced_table_row.sub_row_position == _EbdSubRowPosition.LOWER:
                row = EbdTableRow(
                    description=description,
                    step_number=step_number,
                    sub_rows=sub_rows,
                    use_cases=use_cases or None,
                )
                rows.append(row)
                _logger.debug("Successfully read row #%s ('%s')", step_number, description)
            if enhanced_table_row.multi_step_instruction_text:
                multi_step_instructions.append(
                    MultiStepInstruction(
                        first_step_number_affected=step_number,
                        instruction_text=enhanced_table_row.multi_step_instruction_text,
                    )
                )

    # see above boolean_outcome and subsequent_step_number could be ignored iff schemes of *-numbers are always the same
    # pylint:disable=too-many-locals
    def _handle_single_table_star_exception(
        self,
        table: Table,
        multi_step_instructions: list[MultiStepInstruction],
        row_offset: int,
        rows: list[EbdTableRow],
        row_index: int,
    ) -> None:
        """
        Completes table when handling of single table (out of possible multiple tables for 1 EBD) hit a step
        with several instructions. Those instructions will be split in individual steps.
        As above, the results are written into rows, sub_rows and multi_step_instructions. Those will be modified.
        """
        use_cases: list[str] = []
        complete_table = self._enhance_list_view(table=table, row_offset=row_offset)
        enhanced_table_row = complete_table[row_index]
        use_cases = _get_use_cases(enhanced_table_row.cells)
        star_case_result_code = (
            enhanced_table_row.cells[len(use_cases) + self._column_index_result_code].text.strip() or None
        )
        star_case_note = enhanced_table_row.cells[len(use_cases) + self._column_index_note].text.strip() or None
        while row_index < len(complete_table):
            enhanced_table_row = complete_table[row_index]
            step_number = str(int(last(rows).step_number) + 1)
            description = enhanced_table_row.cells[len(use_cases) + self._column_index_description].text.strip()
            boolean_outcome, subsequent_step_number = _read_subsequent_step_cell(
                enhanced_table_row.cells[len(use_cases) + self._column_index_check_result]
            )

            this_is_the_last_row = row_index == len(complete_table) - 1

            if this_is_the_last_row:
                next_step = "Ende"
            else:
                next_step = str(int(step_number) + 1)

            row = EbdTableRow(
                description=description,
                step_number=step_number,
                sub_rows=[
                    EbdTableSubRow(
                        check_result=EbdCheckResult(
                            subsequent_step_number=subsequent_step_number, result=boolean_outcome
                        ),
                        result_code=star_case_result_code,
                        note=star_case_note,
                    ),
                    # point to next step
                    EbdTableSubRow(
                        check_result=EbdCheckResult(subsequent_step_number=next_step, result=True),
                        result_code=None,
                        note=None,
                    ),
                ],
                use_cases=use_cases or None,
            )
            rows.append(row)
            _logger.debug("Successfully added artificial row #%s ('%s')", step_number, description)

            if enhanced_table_row.multi_step_instruction_text:
                multi_step_instructions.append(
                    MultiStepInstruction(
                        first_step_number_affected=step_number,
                        instruction_text=enhanced_table_row.multi_step_instruction_text,
                    )
                )
            row_index += 1

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
        _logger.info("Successfully created an EbdTable for EBD '%s'", result.metadata.ebd_code)
        return result
