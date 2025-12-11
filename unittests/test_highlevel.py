from typing import List, Tuple

import pytest  # type:ignore[import]
from docx.table import Table
from rebdhuhn.models.ebd_table import EbdTable, EbdTableMetaData

from ebdamame import EbdChapterInformation, EbdNoTableSection, EbdTableNotConvertibleError, TableNotFoundError
from ebdamame.docxtableconverter import DocxTableConverter

from . import get_all_ebd_keys, get_document, get_ebd_docx_tables
from .examples import table_e0003, table_e0097, table_e0453, table_e0462, table_e0901


@pytest.fixture
def get_ebd_keys_and_files(datafiles, request) -> List[Tuple[str, str]]:
    filename = request.param
    all_keys_and_files = ((key, filename) for key in get_all_ebd_keys(datafiles, filename).keys())
    return list(all_keys_and_files)


class TestEbdamame:
    """
    A class for tests of the entire package/library
    """

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v33.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230629_v34.docx")
    @pytest.mark.parametrize("filename", ["ebd20221128.docx", "ebd20230619_v33.docx", "ebd20230629_v34.docx"])
    def test_can_read_document(self, datafiles, filename: str):
        actual = get_document(datafiles, filename)
        assert actual is not None

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v33.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230629_v34.docx")
    @pytest.mark.parametrize(
        "filename,expected_length,expected_entries",
        [
            pytest.param(
                "ebd20221128.docx",
                244,
                [
                    # arbitrary checks ("Stichproben") only
                    (
                        "Kündigung Stromliefervertrag prüfen",
                        EbdChapterInformation(
                            chapter=6,
                            chapter_title="GPKE",
                            section=1,
                            section_title="AD: Kündigung",
                            subsection=1,
                            subsection_title="E_0400_Kündigung Stromliefervertrag prüfen",
                        ),
                    ),
                    (
                        "MaBiS-ZP Aktivierung prüfen",
                        EbdChapterInformation(
                            chapter=7,
                            chapter_title="MaBiS",
                            section=2,
                            section_title="AD: Aktivierung eines MaBiS-Zählpunkts für die Netzzeitreihe an BIKO",
                            subsection=1,
                            subsection_title="E_0024_MaBiS-ZP Aktivierung prüfen",
                        ),
                    ),
                    (
                        "Datenstatus nach Eingang einer AAÜZ vergeben",
                        EbdChapterInformation(
                            chapter=7,
                            chapter_title="MaBiS",
                            section=61,
                            section_title="AD: Übermittlung Datenstatus für die monatliche Ausfallarbeitsüberführungszeitreihe (AAÜZ) an NB und BKV(LF)",
                            subsection=2,
                            subsection_title="E_0076_Datenstatus nach Eingang einer AAÜZ vergeben",
                        ),
                    ),
                ],
            ),
            pytest.param("ebd20230619_v33.docx", 252, []),  # number is not double-checked yet
            pytest.param("ebd20230629_v34.docx", 295, []),  # number is not double-checked yet
        ],
    )
    def test_get_ebd_keys(
        self, datafiles, filename: str, expected_length: int, expected_entries: List[Tuple[str, EbdChapterInformation]]
    ):
        actual = get_all_ebd_keys(datafiles, filename)
        assert len(actual) == expected_length  # arbitrary, didn't check if these are really _all_ the keys
        kapitels = sorted(actual.values(), key=lambda k: (k[1].chapter, k[1].section, k[1].subsection))
        for expected_entry in expected_entries:
            assert expected_entry in kapitels

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key,expected_number_of_tables, empty_ebd_str",
        [
            pytest.param("ebd20221128.docx", "E_0003", 1, "", id="E_0003: One table on only one page"),
            pytest.param("ebd20221128.docx", "E_0015", 1, "", id="E_0015: one table spanning multiple pages"),
            pytest.param("ebd20221128.docx", "E_0901", 2, "", id="E_0901: multiple tables on multiple pages"),
            pytest.param(
                "ebd20221128.docx",
                "E_0402",
                0,
                "Derzeit ist für diese Entscheidung kein Entscheidungsbaum notwendig, da keine Antwort gegeben wird. Der Netzbetreiber muss prüfen, ob eine Abmeldeanfrage zu senden ist.",
                id="E_0402: no table",
            ),
            # pytest.param("ebd20221128.docx", "E_0461"), # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/6
        ],
    )
    def test_get_ebd_docx_table(
        self, datafiles, filename: str, ebd_key: str, expected_number_of_tables: int, empty_ebd_str: str
    ):
        actual = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert actual is not None
        if isinstance(actual, EbdNoTableSection):
            assert actual.remark == empty_ebd_str
        else:
            assert len(actual) == expected_number_of_tables
            for table in actual:
                assert isinstance(table, Table)

    @pytest.mark.datafiles("unittests/test_data/ebd20230629_v34.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key",
        [
            pytest.param("ebd20230629_v34.docx", "E_0406", id="E_0406: EB-Table starts after pages of text"),
        ],
    )
    def test_finding_tables_positive(self, datafiles, filename: str, ebd_key: str):
        docx_tables = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert docx_tables is not None and not isinstance(docx_tables, EbdNoTableSection)
        converter = DocxTableConverter(
            docx_tables,
            ebd_key=ebd_key,
            chapter="Dummy Chapter",
            section="Dummy Section",
            ebd_name=f"{ebd_key} Dummy name",
        )
        actual = converter.convert_docx_tables_to_ebd_table()  # must not throw TableNotFoundError
        assert isinstance(actual, EbdTable)

    @pytest.mark.datafiles("unittests/test_data/ebd20230629_v34.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key, empty_ebd_str",
        [
            pytest.param(
                "ebd20230629_v34.docx",
                "E_0561",
                "Es ist das EBD E_0556 zu nutzen.",
                id="Es ist das EBD E_0556 zu nutzen.",
            ),
            pytest.param("ebd20230629_v34.docx", "E_9999", "", id="Table does not exist"),
        ],
    )
    def test_finding_tables_negative(self, datafiles, filename: str, ebd_key: str, empty_ebd_str: str):
        if empty_ebd_str != "":
            empty_section = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
            assert isinstance(empty_section, EbdNoTableSection) and empty_section.remark == empty_ebd_str
        else:
            with pytest.raises(TableNotFoundError):
                docx_tables = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
                converter = DocxTableConverter(
                    [],
                    ebd_key=ebd_key,
                    chapter="Dummy Chapter",
                    ebd_name=f"{ebd_key} Dummy Name",
                    section="Dummy Section",
                )
                _ = converter.convert_docx_tables_to_ebd_table()

    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v34.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key, excepted_subsequent",
        [
            pytest.param("ebd20230619_v34.docx", "E_0012", "2"),
            pytest.param("ebd20230619_v34.docx", "E_0021", "Ende"),
        ],
    )
    def test_wrong_encoding_of_rightarrow(self, datafiles, filename: str, ebd_key: str, excepted_subsequent: str):
        docx_tables = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert docx_tables is not None and not isinstance(docx_tables, EbdNoTableSection)
        converter = DocxTableConverter(
            docx_tables, ebd_key=ebd_key, chapter="Dummy Chapter", ebd_name="Dummy EBD Name", section="Dummy Section"
        )
        actual = converter.convert_docx_tables_to_ebd_table()
        assert any(
            subrow
            for row in actual.rows
            for subrow in row.sub_rows
            if subrow.check_result.subsequent_step_number == excepted_subsequent
        )

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key, chapter, _, ebd_name, section, expected",
        [
            pytest.param(
                "ebd20221128.docx",
                "E_0003",
                "GPKE",
                "7.39 AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
                "E_0003_Bestellung der Aggregationsebene RZ prüfen",
                "7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
                table_e0003,
                id="E_0003: Simple single page table",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0901",
                "GPKE",
                "16.1 AD: Ermittlung und Abstimmung der abrechnungsrelevanten Ausfallarbeit – Prognosemodell",
                "E_0901_Gegenvorschlag prüfen",
                "16.1.2 E_0901_Gegenvorschlag prüfen",
                table_e0901,
                id="E_0901: table that span over two pages",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0453",
                "GPKE",
                "6.18 AD: Stammdatensynchronisation",
                "E_0453_Änderung prüfen",
                "6.18.1 E_0453_Änderung prüfen",
                table_e0453,
                id="E_0453 with a multi-column mid table",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0462",
                "GPKE",
                "6.4 AD: Lieferbeginn",
                "E_0462_Prüfen, ob Anmeldung direkt ablehnbar",
                "6.4.1 E_0462_Prüfen, ob Anmeldung direkt ablehnbar",
                table_e0462,
                id="E_0462 with gray outer lefts",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0097",
                "GPKE",
                "Austausch der Lieferantenausfallarbeitsclearingliste (Einzelanforderung)",
                "E_0097_Marktlokationen mit LF-AACL abgleichen",
                "7.56.1 E_0097_Marktlokationen mit LF-AACL abgleichen",
                table_e0097,
                id="E_0097 contains step numbers with *",
            ),
        ],
    )
    def test_convert_docx_table_to_ebd_table(
        self,
        datafiles,
        filename: str,
        ebd_key: str,
        chapter: str,
        _: str,
        ebd_name: str,
        section: str,
        expected: EbdTable,
    ):
        docx_table = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert docx_table is not None and not isinstance(docx_table, EbdNoTableSection)
        converter = DocxTableConverter(docx_table, ebd_key=ebd_key, chapter=chapter, ebd_name=ebd_name, section=section)
        actual = converter.convert_docx_tables_to_ebd_table()
        assert actual == expected

    @pytest.mark.datafiles("unittests/test_data/EBD_4.2_20260401_99991231_20251211_oxox_12000.docx")
    def test_extraction_of_e0060_raises_ebd_table_not_convertible_error(self, datafiles):
        """
        Test extraction of E_0060 from EBD v4.2 document.
        E_0060 has a simple table structure with "--" values instead of ja/nein,
        which is not yet supported by the converter.
        See: https://github.com/Hochfrequenz/ebdamame/issues/23
        """
        filename = "EBD_4.2_20260401_99991231_20251211_oxox_12000.docx"
        ebd_key = "E_0060"
        docx_tables = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert docx_tables is not None and not isinstance(docx_tables, EbdNoTableSection)
        assert len(docx_tables) >= 1
        converter = DocxTableConverter(
            docx_tables,
            ebd_key=ebd_key,
            chapter="MaBiS",
            section="AD: Übermittlung Datenstatus des Deltazeitreihenübertrags vom BIKO an ÜNB und NB",
            ebd_name="E_0060_Datenstatus nach Eingang eines Deltazeitreihenübertrags vergeben",
        )
        with pytest.raises(EbdTableNotConvertibleError) as exc_info:
            converter.convert_docx_tables_to_ebd_table()
        assert exc_info.value.ebd_key == ebd_key
        assert "non-boolean" in exc_info.value.reason.lower() or "--" in exc_info.value.reason

    @pytest.mark.snapshot
    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v33.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230629_v34.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20240403_v35.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20250404_v40b.docx")
    @pytest.mark.parametrize(
        "get_ebd_keys_and_files",
        [  # some are commented to improve performance make sure to update snapshots if needed
            # pytest.param(
            #    "ebd20221128.docx",  # this is used as positional argument for the indirect fixture
            # ),
            # pytest.param(
            #    "ebd20230619_v33.docx",  # this is used as positional argument for the indirect fixture
            #    id="19.06.2023 v3.3 / FV2304",
            # ),
            pytest.param(
                "ebd20230629_v34.docx",
                id="19.06.2023 v3.4 / FV2310",
            ),
            pytest.param(
                "ebd20240403_v35.docx",
                id="08.10.2024 v3.5 / FV2410",
            ),
            pytest.param(
                "ebd20250404_v40b.docx",
                id="08.10.2024 v3.5 / FV2504",
            ),
        ],
        indirect=["get_ebd_keys_and_files"],  # see `def get_ebd_keys_and_files(datafiles, request)`
    )
    def test_extraction(self, datafiles, get_ebd_keys_and_files: List[Tuple[str, str]], subtests, snapshot):
        """
        tests the extraction and conversion without specific assertions
        """
        # The idea behind the test is, that it automatically tries to scrape all available EBD tables from a given file.
        # This is a useful test because in the end, that's what an application built upon this library will try to do.
        # So I tried to combine the okay-ish "get_all_ebd_keys" feature with the extraction logic.
        # My idea was that the EBD keys extracted from a given document are used to automatically generate distinct
        # test cases for each ebd_key inside a given file.
        # I thought this was possible with indirect parametrization:
        # https://docs.pytest.org/en/stable/example/parametrize.html#indirect-parametrization
        # https://github.com/search?l=Python&q=org%3AHochfrequenz+indirect+%3D+true&type=Code
        # I thought that I only needed to feed the datafiles fixture and a filename as arguments to my own fixture that
        # then should yield me differently parametrized test runs for each EBD inside the file. The advantage would have
        # been that I do not have to define the expected EBDs to be tested in advance. But I failed.
        # I tried really hard for 1.5 to get the parametrization right and then just gave up and came around with a
        # different approach, called pytest-subtests: https://github.com/pytest-dev/pytest-subtests
        for ebd_key, filename in get_ebd_keys_and_files:
            with subtests.test(ebd_key, key=ebd_key, file=filename):
                # this requires pytest-subtests to be installed (see tox.ini)
                issue_number: str
                try:
                    docx_tables = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
                    if isinstance(docx_tables, EbdNoTableSection):
                        actual_meta_data = EbdTableMetaData(
                            ebd_code=ebd_key,
                            chapter="Dummy Chapter",
                            ebd_name="Dummy Ebd Name",
                            section="Dummy Section",
                            role="Dummy",
                            remark=docx_tables.remark,
                        )
                        # need to adapt EbdTableMetaData
                        assert actual_meta_data == snapshot(name=ebd_key)
                    else:
                        converter = DocxTableConverter(
                            docx_tables,
                            ebd_key=ebd_key,
                            chapter="Dummy Chapter",
                            ebd_name=f"{ebd_key} Dummy Name",
                            section="Dummy Section",
                        )
                        actual = converter.convert_docx_tables_to_ebd_table()
                        assert isinstance(actual, EbdTable)
                        assert actual == snapshot(name=ebd_key)
                # In the long run, all these catchers shall be removed.
                except AttributeError as attribute_error:
                    if attribute_error.name == "_column_index_step_number":
                        pytest.skip(f"{ebd_key}\t https://github.com/Hochfrequenz/ebdamame/issues/71")
                except EbdTableNotConvertibleError:
                    # https://github.com/Hochfrequenz/ebdamame/issues/23
                    pass  # ignore forever
                except TableNotFoundError:
                    # https://github.com/Hochfrequenz/ebdamame/issues/9
                    pass  # ignore for now
                except ValueError as value_error:
                    # Simply run the test, then see how many of the subtests pass and which are skipped.
                    # The skipped ones require developer analysis and code improvements.
                    # This library has probably reached v1.0.0 if this catch block is not necessary anymore.
                    match value_error.args[0]:
                        case "None is not in list":
                            # https://github.com/Hochfrequenz/ebdamame/issues/20
                            issue_number = "20"
                        case "Exactly one of the entries in sub_rows has to have check_result.result True":
                            # https://github.com/Hochfrequenz/ebdamame/issues/21
                            issue_number = "21"
                        case "The cell content 'gültiges daten-ergebnis' does not belong to a ja/nein cell":
                            # https://github.com/Hochfrequenz/ebdamame/issues/74
                            issue_number = "74"
                        case "No cell containing a valid step number found.":
                            issue_number = "to be added"
                        case "The cell content 'à 110' does not belong to a ja/nein cell":
                            issue_number = "to be added"
                        case _:
                            raise
                    error_msg = f"Error while scraping '{ebd_key}' (#{issue_number}): {value_error}"
                    pytest.skip(error_msg)
                except UnboundLocalError as unbound_error:
                    match unbound_error.args[0]:
                        case "cannot access local variable 'role' where it is not associated with a value":
                            # https://github.com/Hochfrequenz/ebdamame/issues/22
                            issue_number = "22"
                        case _:
                            raise
                    error_msg = f"Error while scraping '{ebd_key}' (#{issue_number}): {unbound_error}"
                    pytest.skip(error_msg)
