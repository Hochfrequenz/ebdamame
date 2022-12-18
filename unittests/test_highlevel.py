import pytest  # type:ignore[import]
from docx.table import Table  # type:ignore[import]
from ebdtable2graph import EbdTable

from ebddocx2table.docxtableconverter import DocxTableConverter

from . import get_all_ebd_keys, get_document, get_ebd_docx_tables
from .examples import table_e0003, table_e0901


class TestEbdDocx2Table:
    """
    A class for tests of the entire package/library
    """

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.parametrize("filename", ["ebd20221128.docx"])
    def test_can_read_document(self, datafiles, filename: str):
        actual = get_document(datafiles, filename)
        assert actual is not None

    @pytest.mark.datafiles("unittests/test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename,expected_length",
        [pytest.param("ebd20221128.docx", 241)],
    )
    def test_get_ebd_keys(self, datafiles, filename: str, expected_length: int):
        actual = get_all_ebd_keys(datafiles, filename)
        assert len(actual) == expected_length  # arbitrary, didn't check if these are really _all_ the keys

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
        ],
    )
    def test_convert_docx_table_to_ebd_table(
        self, datafiles, filename: str, ebd_key: str, chapter: str, sub_chapter: str, expected: EbdTable
    ):
        docx_table = get_ebd_docx_tables(datafiles, filename, ebd_key=ebd_key)
        converter = DocxTableConverter(docx_table, ebd_key=ebd_key, chapter=chapter, sub_chapter=sub_chapter)
        actual = converter.convert_docx_tables_to_ebd_table()
        assert actual == expected
