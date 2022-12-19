"""
module contains data as we expected them to be scraped from the docx file
"""

from ebdtable2graph.models import EbdTable
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

# E_0901 spans over multiple pages, let the fun begin
table_e0901 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0901",
        chapter="16.1 AD: Ermittlung und Abstimmung der abrechnungsrelevanten Ausfallarbeit – Prognosemodell",
        sub_chapter="16.1.2 E_0901_Gegenvorschlag prüfen",
        role="NB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Liegt für die Ausfallarbeitszeitreihe bereits eine Zustimmung vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung\nAusfallarbeitszeitreihe wurde bereits bestätigt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="2"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="2",
            description="Ist der Gegenvorschlag zur Ausfallarbeitszeitreihe innerhalb der vorgegebenen Frist eingegangen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster: Ablehnung\nFristüberschreitung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="3",
            description="Liegt bereits ein Gegenvorschlag zur Ausfallarbeitszeitreihe vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung\nGegenvorschlag liegt bereits vor\nHinweis: Ein weiterer Gegenvorschlag kann nicht eingereicht werden.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"),
                    result_code=None,
                    note=None,
                ),
            ],
        ),
        EbdTableRow(
            step_number="4",
            description="Können die Energiemengen des Gegenvorschlages zur Ausfallarbeitszeitreihe akzeptiert werden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Ablehnung\nEnergiemengen falsch / nicht plausibel",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster: Zustimmung\nZustimmung",
                ),
            ],
        ),
    ],
)
