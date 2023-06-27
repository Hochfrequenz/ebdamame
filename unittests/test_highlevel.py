from typing import List, Tuple

import pytest  # type:ignore[import]
from docx.table import Table  # type:ignore[import]
from ebdtable2graph.models import EbdTable

from ebddocx2table import EbdChapterInformation, TableNotFoundError
from ebddocx2table.docxtableconverter import DocxTableConverter

from . import get_all_ebd_keys, get_document, get_ebd_docx_tables
from .examples import table_e0003, table_e0453, table_e0462, table_e0901


@pytest.fixture
def get_ebd_keys_and_files(datafiles, request) -> List[Tuple[str, str]]:
    filename = request.param
    all_keys_and_files = ((key, filename) for key in get_all_ebd_keys(datafiles, filename).keys())
    return list(all_keys_and_files)


class TestEbdDocx2Table:
    """
    A class for tests of the entire package/library
    """

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v34.docx")
    @pytest.mark.parametrize("filename", ["ebd20221128.docx", "ebd20230619.docx", "ebd20230619_v34.docx"])
    def test_can_read_document(self, datafiles, filename: str):
        actual = get_document(datafiles, filename)
        assert actual is not None

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v34.docx")
    @pytest.mark.parametrize(
        "filename,expected_length,expected_entries",
        [
            pytest.param(
                "ebd20221128.docx",
                241,
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
            pytest.param("ebd20230619.docx", 249, []),  # number is not double-checked yet
            pytest.param("ebd20230619_v34.docx", 293, []),  # number is not double-checked yet
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
        "filename, ebd_key,expected_number_of_tables",
        [
            pytest.param("ebd20221128.docx", "E_0003", 1, id="E_0003: One table on only one page"),
            pytest.param("ebd20221128.docx", "E_0015", 1, id="E_0015: one table spanning multiple pages"),
            pytest.param("ebd20221128.docx", "E_0901", 2, id="E_0901: multiple tables on multiple pages")
            # pytest.param("ebd20221128.docx", "E_0461"), # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/6
        ],
    )
    def test_get_ebd_docx_table(self, datafiles, filename: str, ebd_key: str, expected_number_of_tables: int):
        actual = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        assert actual is not None
        assert len(actual) == expected_number_of_tables
        for table in actual:
            assert isinstance(table, Table)

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key, chapter, sub_chapter, expected",
        [
            pytest.param(
                "ebd20221128.docx",
                "E_0003",
                "7.39 AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
                "7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
                table_e0003,
                id="E_0003: Simple single page table",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0901",
                "16.1 AD: Ermittlung und Abstimmung der abrechnungsrelevanten Ausfallarbeit – Prognosemodell",
                "16.1.2 E_0901_Gegenvorschlag prüfen",
                table_e0901,
                id="E_0901: table that span over two pages",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0453",
                "6.18 AD: Stammdatensynchronisation",
                "6.18.1 E_0453_Änderung prüfen",
                table_e0453,
                id="E_0453 with a multi-column mid table",
            ),
            pytest.param(
                "ebd20221128.docx",
                "E_0462",
                "6.4 AD: Lieferbeginn",
                "6.4.1 E_0462_Prüfen, ob Anmeldung direkt ablehnbar",
                table_e0462,
                id="E_0462 with gray outer lefts",
            ),
        ],
    )
    def test_convert_docx_table_to_ebd_table(
        self, datafiles, filename: str, ebd_key: str, chapter: str, sub_chapter: str, expected: EbdTable
    ):
        docx_table = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        converter = DocxTableConverter(docx_table, ebd_key=ebd_key, chapter=chapter, sub_chapter=sub_chapter)
        actual = converter.convert_docx_tables_to_ebd_table()
        assert actual == expected

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619.docx")
    @pytest.mark.datafiles("unittests/test_data/ebd20230619_v34.docx")
    @pytest.mark.parametrize(
        "get_ebd_keys_and_files",
        [
            pytest.param(
                "ebd20221128.docx",  # this is used as positional argument for the indirect fixture
            ),
            pytest.param(
                "ebd20230619.docx",  # this is used as positional argument for the indirect fixture
            ),
            pytest.param(
                "ebd20230619_v34.docx",
                id="19.06.2023 v3.4 / FV2310",
            ),
        ],
        indirect=["get_ebd_keys_and_files"],  # see `def get_ebd_keys_and_files(datafiles, request)`
    )
    def test_extraction(self, datafiles, get_ebd_keys_and_files: List[Tuple[str, str]], subtests):
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
                    converter = DocxTableConverter(
                        docx_tables, ebd_key=ebd_key, chapter="Dummy Chapter", sub_chapter="Dummy Subchapter"
                    )
                    actual = converter.convert_docx_tables_to_ebd_table()
                    assert isinstance(actual, EbdTable)
                # In the long run, all these catchers shall be removed.
                except AttributeError as attribute_error:
                    if attribute_error.name == "_column_index_step_number":
                        pytest.skip("https://github.com/Hochfrequenz/ebddocx2table/issues/71")
                except TableNotFoundError:
                    # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/9
                    pass  # ignore for now
                except ValueError as value_error:
                    # Simply run the test, then see how many of the subtests pass and which are skipped.
                    # The skipped ones require developer analysis and code improvements.
                    # This library has probably reached v1.0.0 if this catch block is not necessary anymore.
                    match value_error.args[0]:
                        case "None is not in list":
                            # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/20
                            issue_number = "20"
                        case "Exactly one of the entries in sub_rows has to have check_result.result True":
                            # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/21
                            issue_number = "21"
                        case "The cell content '--' does not belong to a ja/nein cell":
                            # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/23
                            issue_number = "23"
                        case _:
                            raise
                except UnboundLocalError as unbound_error:
                    match unbound_error.args[0]:
                        case "cannot access local variable 'role' where it is not associated with a value":
                            # https://github.com/Hochfrequenz/ebd_docx_to_table/issues/22
                            issue_number = "22"
                        case _:
                            raise
                    error_msg = f"Error while scraping '{ebd_key}' (#{issue_number})"
                    pytest.skip(error_msg)
