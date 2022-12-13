"""
module contains data as we expected them to be scraped from the docx file
"""

from ebdtable2graph import EbdTable
from ebdtable2graph.models.ebd_table import EbdCheckResult, EbdTableMetaData, EbdTableRow, EbdTableSubRow

# E_0003 is pretty short
# https://www.entscheidungsbaumdiagramm.de/diagram?ebdKey=E_0003&formatVersion=FV2204
table_e0003 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0003",
        chapter="7.39 AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
        sub_chapter="7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
        role="ÜNB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Erfolgt der Eingang der Bestellung fristgerecht?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Fristüberschreitung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="2",
            description="Erfolgt die Bestellung zum Monatsersten 00:00 Uhr?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Gewählter Zeitpunkt nicht zulässig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
    ],
)
