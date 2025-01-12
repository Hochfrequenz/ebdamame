# ebdamame

[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](LICENSE)
![Python Versions (officially) supported](https://img.shields.io/pypi/pyversions/ebdamame.svg)
![Unittests status badge](https://github.com/Hochfrequenz/ebdamame/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/ebdamame/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/ebdamame/workflows/Linting/badge.svg)
![Formatting status badge](https://github.com/Hochfrequenz/ebdamame/workflows/Formatting/badge.svg)
![PyPi Status Badge](https://img.shields.io/pypi/v/ebdamame)

🇩🇪 Dieses Repository enthält ein Python-Paket namens [`ebdamame`](https://pypi.org/project/ebdamame) (früher: `ebddocx2table`), das genutzt werden kann, um aus .docx-Dateien maschinenlesbare Tabellen, die einen Entscheidungsbaum (EBD) modellieren, zu extrahieren (scrapen).
Diese Entscheidungsbäume sind Teil eines regulatorischen Regelwerks für die deutsche Energiewirtschaft und kommen in der Eingangsprüfung der Marktkommunikation zum Einsatz.
Die mit diesem Paket erstellten maschinenlesbaren Tabellen können mit [`rebdhuhn`](https://pypi.org/project/rebdhuhn) (früher: `ebdtable2graph`) in echte Graphen und Diagramme umgewandelt werden.
Exemplarische Ergebnisse des Scrapings finden sich als .json-Dateien im Repository [`machine-readable_entscheidungsbaumdiagramme`](https://github.com/Hochfrequenz/machine-readable_entscheidungsbaumdiagramme/).

🇬🇧 This repository contains the source code of the Python package [`ebdamame`](https://pypi.org/project/ebdamame) (formerly published as `ebddocx2table`).

## Rationale

Assume that you want to analyse or visualize the Entscheidungsbaumdiagramme (EBD) by EDI@Energy.
The website edi-energy.de, as always, only provides you with PDF or Word files instead of _really_ digitized data.

The package `ebdamame` scrapes the `.docx` files and returns data in a model defined in the "sister" package [`rebdhuhn`](https://pypi.org/project/rebdhuhn) (formerly known as `ebdtable2graph`).

Once you scraped the data (using this package) you can plot it with [`rebdhuhn`](https://pypi.org/project/rebdhuhn).

## How to use the package

In any case, install the repo from PyPI:

```bash
pip install ebdamame
```

### Use as a library

```python
import json
from pathlib import Path

import cattrs

from ebdamame import TableNotFoundError, get_all_ebd_keys, get_ebd_docx_tables  # type:ignore[import]
from ebdamame.docxtableconverter import DocxTableConverter  # type:ignore[import]

docx_file_path = Path("unittests/test_data/ebd20230629_v34.docx")
# download this .docx File from edi-energy.de or find it in the unittests of this repository.
# https://github.com/Hochfrequenz/ebddocx2table/blob/main/unittests/test_data/ebd20230629_v34.docx
docx_tables = get_ebd_docx_tables(docx_file_path, ebd_key="E_0003")
converter = DocxTableConverter(
    docx_tables,
    ebd_key="E_0003",
    ebd_name="E_0003_AD: Bestellung der Aggregationsebene der Bilanzkreissummenzeitreihe auf Ebene der Regelzone",
    chapter="MaBiS",
    section="7.42.1"
)
result = converter.convert_docx_tables_to_ebd_table()
with open(Path("E_0003.json"), "w+", encoding="utf-8") as result_file:
    # the result file can be found here:
    # https://github.com/Hochfrequenz/machine-readable_entscheidungsbaumdiagramme/tree/main/FV2310
    json.dump(cattrs.unstructure(result), result_file, ensure_ascii=False, indent=2, sort_keys=True)
```

### Use as a CLI tool

_to be written_

## How to use this Repository on Your Machine (for development)

Please follow the instructions in our
[Python Template Repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine).
And for further information, see the [Tox Repository](https://github.com/tox-dev/tox).

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.

## Related Tools and Context

This repository is part of the [Hochfrequenz Libraries and Tools for a truly digitized market communication](https://github.com/Hochfrequenz/digital_market_communication/).
