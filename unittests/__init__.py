"""
This file is here, because this allows for best de-coupling of tests and application/library logic.
Further reading: https://docs.pytest.org/en/6.2.x/goodpractices.html#tests-outside-application-code
"""

from pathlib import Path

_TEST_DATA_DIR = Path(__file__).parent / "test_data"

# Expose commonly used files as constants
EBD_2022_11_28 = _TEST_DATA_DIR / "ebd20221128.docx"
EBD_2023_06_19_V33 = _TEST_DATA_DIR / "ebd20230619_v33.docx"
EBD_2023_06_19_V34 = _TEST_DATA_DIR / "ebd20230619_v34.docx"
EBD_2023_06_29_V34 = _TEST_DATA_DIR / "ebd20230629_v34.docx"
EBD_2024_04_03_V35 = _TEST_DATA_DIR / "ebd20240403_v35.docx"
EBD_2025_04_04_V40B = _TEST_DATA_DIR / "ebd20250404_v40b.docx"
EBD_V42 = _TEST_DATA_DIR / "EBD_4.2_20260401_99991231_20251211_oxox_12000.docx"
