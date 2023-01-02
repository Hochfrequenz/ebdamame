"""
module contains data as we expected them to be scraped from the docx file
"""

from ebdtable2graph.models import EbdTable
from ebdtable2graph.models.ebd_table import (
    EbdCheckResult,
    EbdTableMetaData,
    EbdTableRow,
    EbdTableSubRow,
    MultiStepInstruction,
)

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
table_e0453 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0453",
        chapter="6.18 AD: Stammdatensynchronisation",
        sub_chapter="6.18.1 E_0453_Änderung prüfen",
        role="ÜNB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Sind Fehler im Rahmen der AHB-Prüfungen in den Stammdaten des NB festgestellt worden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"),
                    result_code="A97",
                    note="Die Stammdaten des NB genügen nicht den AHB-Vorgaben.\nHinweis: Diese Prüfung ist auf alle Stammdaten des NB anzuwenden. Es sind die Fehlerorte aller dabei festgestellten Fehler in der Antwort zu benennen.\nEine Durchführung der nachfolgend in diesem EBD genannten Prüfungen erfolgt nicht.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="2"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Ist als Aggregationsverantwortlicher der ÜNB im Vorgang angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Ist die im Vorgang enthaltene Marktlokations-ID zum genannten Zeitpunkt dem ÜNB bereits zur Aggregation zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="Ende"),
                    result_code="A19",
                    note="Die Marktlokation bzw. Tranche ist für den genannten Zeitpunkt nicht dem ÜNB zur Aggregation gemeldet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Sind Fehler im Rahmen der AHB-Prüfungen in den Stammdaten des LF festgestellt worden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"),
                    result_code="A98",
                    note="Die Stammdaten des LF genügen nicht den AHB-Vorgaben.\nHinweis: Diese Prüfung ist auf alle Stammdaten des LF anzuwenden. Es sind die Fehlerorte aller dabei festgestellten Fehler in der Antwort zu benennen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="5"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Wurde die angegebene Verarbeitungsnummer im Vorgang bereits für einen verarbeiteten Vorgang zu dieser Marktlokation verwendet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="6"),
                    result_code="A20",
                    note="Verarbeitungsnummer bereits verwendet",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Ist die richtige Regelzone angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"),
                    result_code="A01",
                    note="Regelzone falsch",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="7"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Ist der angegebene Netzbetreiber der Marktlokation in der Regelzone bekannt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="8"),
                    result_code="A02",
                    note="Netzbetreiber nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",
            description="Ist das Bilanzierungsgebiet zum angegebenen Zeitpunkt in der Regelzone gültig?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="9"),
                    result_code="A03",
                    note="Bilanzierungsgebiet nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="9",
            description="Ist der angegebene Netzbetreiber dem Bilanzierungsgebiet zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="10"),
                    result_code="A14",
                    note="Angegebener NB entspricht nicht dem zugeordneten NB des Bilanzierungsgebiets",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="10",
            description="Wird die Marktlokation auf Grundlage von Werten bilanziert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="11"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="12"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="11",
            description="Ist der Messstellenbetreiber zum angegebenen Zeitpunkt in der BDEW-Codenummerndatenbank registriert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="12"),
                    result_code="A15",
                    note="Messstellenbetreiber nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="12"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="12",
            description="Ist der im Vorgang genannte LF identisch mit dem Absender der Nachricht?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="13"),
                    result_code="A04",
                    note="LF im Vorgang weicht vom Absender ab",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="13"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="13",
            description="Ist der Bilanzkreis zum angegebenen Zeitpunkt gültig?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="14"),
                    result_code="A05",
                    note="Bilanzkreis nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="14"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="14",
            description="Passt die Prognosegrundlage zum ZRT?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="15"),
                    result_code="A16",
                    note="Prognosegrundlage passt nicht zum ZRT",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="15"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="15",
            description="Passt die OBIS-Kennzahl zum ZRT?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="16"),
                    result_code="A06",
                    note="OBIS nicht passend",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="16"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="16",
            description="Passt die Lieferrichtung zum ZRT?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="17"),
                    result_code="A07",
                    note="Lieferrichtung nicht passend",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="17"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="17",
            description="Passt der angegebene Aggregationsverantwortliche in dem Vorgang zur Aggregationsverantwortung der Marktlokation im System des ÜNB, sofern die Marktlokation beim ÜNB schon bekannt ist?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="18"),
                    result_code="A17",
                    note="Aggregationsverantwortlicher im Vorgang passt nicht zur Aggregationsverantwortung der Marktlokation im System des ÜNB",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="18"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="18",
            description="Ist die Aggregationsverantwortung im Vorgang dem NB zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="19"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="19",
            description="Wird die Marktlokation auf Grundlage von Profilen bilanziert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="20"),
                    result_code="A18",
                    note="Falscher Aggregationsverantwortlicher",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="20",
            description="Ist die Aggregationsverantwortung im Vorgang dem ÜNB zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="27"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="21",
            description="Entspricht der Zeitreihentyp (ZRT) den gültigen ZRT zur Datenaggregation beim ÜNB?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="22"),
                    result_code="A08",
                    note="ZRT nicht passend",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="22"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="22",
            description="Entspricht das Bilanzierungsverfahren dem gültigen Bilanzierungsverfahren zur Datenaggregation beim ÜNB?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="23"),
                    result_code="A09",
                    note="Bilanzierungsverfahren nicht gültig",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="23"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="23",
            description="Wird die Marktlokation auf Grundlage von Profilen bilanziert?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="24"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="27"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="24",
            description="Ist das angegebene normierte Profil zum angegebenen Zeitpunkt für das Bilanzierungsgebiet Bestandteil der Profildefinitionsliste des Netzbetreibers?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="25"),
                    result_code="A10",
                    note="Normiertes Profil liegt nicht vor",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="25"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="25",
            description="Ist das angegebene normierte Profil zum angegebenen Zeitpunkt ein Profil aus der Gruppe SLP mit synthetischen Verfahren?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="26"),
                    result_code="A11",
                    note="Normiertes Profil nicht SLP mit synthetischem Verfahren",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="26"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="26",
            description="Ist die Prognosegrundlage der Marktlokation eine, für die der ÜNB die Aggregation durchführen darf?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="27"),
                    result_code="A12",
                    note="Unpassende Prognosegrundlage",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="27"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="27",
            description="Hat keine vorangegangene Prüfung zu einer Antwort geführt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A13",
                    note="Stammdaten wurden widerspruchsfrei übernommen.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A**",
                    note="Stammdaten wurden übernommen \nHinweis A**: Es werden alle gemerkten Antwortcodes der vorhergehenden Prüfschritte übermittelt.",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=[
        MultiStepInstruction(
            first_step_number_affected="4",
            instruction_text="Alle festgestellten Antworten sind anzugeben, soweit im Format möglich (maximal 8 Antwortcodes)*.",
        )
    ],
)
