import pytest
from ebdtable2graph import EbdTable
from examples import table_e0003

from ebddocx2table.docxtableconverter import DocxTableConverter

from . import get_document, get_ebd_docx_table


class TestEbdDocx2Table:
    """
    A class for tests of the entire package/library
    """

    @pytest.mark.datafiles("./test_data/ebd20221128.docx")
    @pytest.mark.parametrize("filename", ["ebd20221128.docx"])
    def test_can_read_document(self, datafiles, filename: str):
        actual = get_document(datafiles, filename)
        assert actual is not None

    @pytest.mark.datafiles("./test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key",
        [pytest.param("ebd20221128.docx", "E_0003")],  # 7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen	342
    )
    def test_get_ebd_docx_table(self, datafiles, filename: str, ebd_key: str):
        actual = get_ebd_docx_table(datafiles, filename, ebd_key=ebd_key)
        assert actual is not None

    @pytest.mark.datafiles("./test_data/ebd20221128.docx")
    @pytest.mark.parametrize(
        "filename, ebd_key, chapter, sub_chapter, expected",
        [
            pytest.param(
                "ebd20221128.docx",
                "E_0003",
                "7.39 AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
                "7.39.1 E_0003_Bestellung der Aggregationsebene RZ prüfen",
                table_e0003,
            )
        ],
    )
    def test_convert_docx_table_to_ebd_table(
        self, datafiles, filename: str, ebd_key: str, chapter: str, sub_chapter: str, expected: EbdTable
    ):
        docx_table = get_ebd_docx_table(datafiles, filename, ebd_key=ebd_key)
        converter = DocxTableConverter(docx_table, ebd_key=ebd_key, chapter=chapter, sub_chapter=sub_chapter)
        actual = converter.convert_docx_table_to_ebd_table()
        assert actual == expected
