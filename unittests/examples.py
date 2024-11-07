"""
module contains data as we expected them to be scraped from the docx file
"""

from rebdhuhn.models.ebd_table import (
    EbdCheckResult,
    EbdTable,
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
        section="7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
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

# E_0097 is an example of a table that has rows with "*"
table_e0097 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0097",
        chapter="7.56 AD: Austausch der Lieferantenausfallarbeitsclearingliste (Einzelanforderung)",
        section="7.56.1 E_0097_Marktlokationen mit LF-AACL abgleichen",
        role="LF",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Entspricht die Gültigkeit (Monat) dem angefragten Zeit-raum?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung der gesamten Liste\nZeitraum nicht plausibel",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Entspricht der MaBiS-ZP dem angefragten MaBiS-ZP?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A02",
                    note="Cluster: Ablehnung der gesamten Liste \nMaBiS-ZP entspricht nicht dem angefragten MaBiS-ZP",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Entspricht die Versionsangabe in der LF-AACL der Versionsangabe der LF-AASZR, zu der eine LF-AACL angefordert wurde?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung der gesamten Liste \nVersion nicht zugelassen",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Ist eine erwartete Marktlokation in der LF-AACL nicht enthalten?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Korrekturliste wegen Ablehnung\nZusätzlicher Datensatz / ergänzte Marktlokation",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="5"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Ist in der LF-AACL eine Marktlokation enthalten, die im Bilanzierungsmonat dem LF zur Bilanzierung nicht zugeordnet ist?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster: Korrekturliste wegen Ablehnung\nMarktlokation falschem LF zugeordnet",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Ist die in der LF-AACL enthaltene Marktlokation dem MaBiS-ZP zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Korrekturliste wegen Ablehnung\nZu viele Marktlokationen enthalten / entfallene Marktlokation",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="7"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Entspricht das Bilanzierungsgebiet dem zwischen NB und LF ausgetauschten Bilanzierungsgebiet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster: Korrekturliste wegen Ablehnung\nBilanzierungsrel. Daten nicht korrekt / fehlen",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",  # artificially incremented step number (was '7*')
            description="Entspricht der Bilanzkreis dem zwischen NB und LF ausgetauschten Bilanzkreis?",  # todo: check diff for "ausge-tauschten" in original .docx
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster: Korrekturliste wegen Ablehnung\nBilanzierungsrel. Daten nicht korrekt / fehlen",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="9",  # artificially incremented step number (was '7*')
            description="Entspricht die tatsächliche Ausfallarbeitsmenge der er-warteten Ausfallarbeitsmenge?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A07",
                    note="Cluster: Korrekturliste wegen Ablehnung\nBilanzierungsrel. Daten nicht korrekt / fehlen",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="Ende"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=[
        MultiStepInstruction(
            first_step_number_affected="4", instruction_text="Je Marktlokation erfolgen die nachfolgenden Prüfungen:"
        )
    ],
)

# E_0901 spans over multiple pages, let the fun begin
table_e0901 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0901",
        chapter="16.1 AD: Ermittlung und Abstimmung der abrechnungsrelevanten Ausfallarbeit – Prognosemodell",
        section="16.1.2 E_0901_Gegenvorschlag prüfen",
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
        section="6.18.1 E_0453_Änderung prüfen",
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

table_e0462 = EbdTable(
    metadata=EbdTableMetaData(
        ebd_code="E_0462",
        chapter="6.4 AD: Lieferbeginn",
        section="6.4.1 E_0462_Prüfen, ob Anmeldung direkt ablehnbar",
        role="NB",
    ),
    rows=[
        EbdTableRow(
            step_number="1",
            description="Ist in der Anmeldung die Angabe der Identifikationslogik mit dem Wert „Marktlokations-ID“ angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="2"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="2",
            description="Wurde die im Geschäftsvorfall angegebene ID der Marktlokation im IT-System des Empfängers gefunden?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A01",
                    note="Cluster: Ablehnung\nMarktlokation ist nicht identifizierbar.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="3"),
                    result_code=None,
                    note="Hinweis: Bei dieser Prüfung hat der NB auch die Marktlokationen zu berücksichtigen, die in den letzten drei Jahren vor dem Eingang der Anfrage im Netzgebiet des NB waren.",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="3",
            description="Nimmt die Marktlokation zum Anmeldedatum an der Marktkommunikation teil?\n(Dies sind Marktlokationen, bei welchen ein Bilanzkreis und ein Lieferant zugeordnet ist. Z.B. stillgelegte Marktlokationen oder Marktlokationen einer Kundenanlage, welche vom Kundenanlagenbetreiber beliefert werden und somit keine Zuordnung zu einem Lieferanten haben, nehmen nicht an der Marktkommunikation teil.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A15",
                    note="Cluster: Ablehnung\nMarktlokation, die über Marktlokations-ID identifiziert wurde, nimmt nicht an der Marktkommunikation teil.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="4",
            description="Wurde mit allen zur Verfügung gestellten Informationen aus der Anmeldung unter Wahrung der gebotenen Sorgfalt genau eine Marktlokation ermittelt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="5"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="6"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="5",
            description="Nimmt die Marktlokation zum Anmeldedatum an der Marktkommunikation teil? \n(Dies sind Marktlokationen, bei welchen ein Bilanzkreis und ein Lieferant zugeordnet ist. Z.B. stillgelegte Marktlokationen oder Marktlokationen einer Kundenanlage, welche vom Kundenanlagenbetreiber beliefert werden und somit keine Zuordnung zu einem Lieferanten haben, nehmen nicht an der Marktkommunikation teil.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A16",
                    note="Cluster: Ablehnung\nIdentifizierte Marktlokation nimmt nicht an der Marktkommunikation teil.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="6",
            description="Wurde mit allen zur Verfügung gestellten Informationen aus der Anmeldung unter Wahrung der gebotenen Sorgfalt mehr als eine Marktlokation ermittelt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="7"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="9"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="7",
            description="Handelt es sich um einen „Einzug in Neuanlage“?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A03",
                    note="Cluster: Ablehnung\nKeine Identifizierung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="8"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="8",
            description="Ist die Anmeldung (der Neuanlage) vor mehr als 60 WT eingegangen?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A18",
                    note="Cluster: Ablehnung\nNeuangelegte Marktlokation konnte nicht identifiziert werden",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="4"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="9",
            description="Nimmt von den identifizierten Marktlokationen exakt eine Marktlokation an der Marktkommunikation teil? \n(Die andere(n) Marktlokation(en) sind z.B. stillgelegte Marktlokation(en), Objekt(e) um einen Teil einer Kundenanlage.)",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A17",
                    note="Cluster: Ablehnung\nMehrfachidentifizierung",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="10"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="10",
            description="Ist die Marktlokation zum Eingangsdatum der Meldung dem Netzgebiet zugeordnet?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A04",
                    note="Cluster: Ablehnung\nMarktlokation befindet sich zum Eingangsdatum der Meldung nicht mehr im Netzgebiet des NB.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="11"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="11",
            description="Handelt es sich um einen Ein-/Auszug (Umzug)?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="14"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="12"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="12",
            description="Handelt es sich um einen „Einzug in Neuanlage“?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="14"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="13"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="13",
            description="Liegt der Transaktionsgrund zur Beendigung einer Ersatz-versorgung vor?\nDies ist bei dem folgenden Transaktionsgrund der Fall:\nLieferbeginn und Abmeldung aus der Ersatzversorgung",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="15"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="18"),
                    result_code=None,
                    note="Hinweis: es liegt der Transaktionsgrund „Wechsel“ vor.",
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="14",
            description="Sind bisheriger und neuer Anschlussnutzer identisch?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A13",
                    note="Cluster: Ablehnung\nEs handelt sich nicht um einen Einzug, da zum genannten Datum kein Anschlussnutzerwechsel stattfand.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="15"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="15",
            description="Handelt es sich um eine Marktlokation, deren Messlokationen vollständig mit iMS ausgestattet sind oder/und deren Prognosegrundlage auf Basis von Werten erfolgt?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="16"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="17"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug"],
        ),
        EbdTableRow(
            step_number="16",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens einen Tag nach dem Eingangsdatum der Anmeldung?\nHinweis: Diese Prüfung enthält keine Aussage darüber, ob eine Verschiebung des Lieferbeginns notwendig ist.",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A05",
                    note="Cluster: Ablehnung\nEingangsfrist bei iMS / kME mit RLM nicht ein-gehalten",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug", "iMS/kME mit RLM"],
        ),
        EbdTableRow(
            step_number="17",
            description="Liegt das Eingangsdatum der Anmeldung mehr als sechs Wochen nach dem Lieferbeginndatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A06",
                    note="Cluster: Ablehnung\nFristüberschreitung bei kME ohne RLM/mME/ Pauschalanlage",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Einzug", "kME ohne RLM/mME/ Pauschalanlage"],
        ),
        EbdTableRow(
            step_number="18",
            description="Ist in der Anmeldung die Angabe der Identifikationslogik mit dem Wert „Marktlokations-ID“ angegeben?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="19"), result_code=None, note=None
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="20"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel"],
        ),
        EbdTableRow(
            step_number="19",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens 7 WT nach dem Eingangsdatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A09",
                    note="Cluster: Ablehnung\nFrist bei einem Lieferantenwechsel nicht ein-gehalten im Rahmen der schnellen Identifikation.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel", "schnelle Identifikation"],
        ),
        EbdTableRow(
            step_number="20",
            description="Liegt das Lieferbeginndatum der Anmeldung mindestens 10 WT nach dem Eingangsdatum der Anmeldung?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A10",
                    note="Cluster: Ablehnung\nFrist bei einem Lieferantenwechsel nicht eingehalten im Rahmen der langsamen Identifikation.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="21"), result_code=None, note=None
                ),
            ],
            use_cases=["Lieferantenwechsel", "langsame Identifikation"],
        ),
        EbdTableRow(
            step_number="21",
            description="Liegt für diese Marktlokation bereits eine gerade in Arbeit befindliche und noch nicht beantwortete Anmeldung vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code="A11",
                    note="Cluster: Ablehnung\nAndere Anmeldung in Bearbeitung.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number="22"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="22",
            description="Liegt die notwendige Zuordnungsermächtigung (Bilanzkreis/Bilanzierungsverfahren) vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A12",
                    note="Cluster: Ablehnung\nZuordnungsermächtigung fehlt.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="23"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="23",
            description="Liegt der Transaktionsgrund „Lieferbeginn und Abmeldung aus der Ersatzversorgung“ vor?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code=None,
                    note="EBD E_0402_Prüfen, ob eine Abmeldeanfrage erforderlich",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number="24"), result_code=None, note=None
                ),
            ],
            use_cases=None,
        ),
        EbdTableRow(
            step_number="24",
            description="Ist der zum Anmeldedatum zugeordnete LF der GV?",
            sub_rows=[
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=False, subsequent_step_number=None),
                    result_code="A14",
                    note="Cluster: Ablehnung\nGrundversorger ist der Marktlokation nicht zu-geordnet.",
                ),
                EbdTableSubRow(
                    check_result=EbdCheckResult(result=True, subsequent_step_number=None),
                    result_code=None,
                    note="EBD E_0402_Prüfen, ob eine Abmeldeanfrage erforderlich",
                ),
            ],
            use_cases=None,
        ),
    ],
    multi_step_instructions=None,
)
