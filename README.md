# ebddocx2table

![Unittests status badge](https://github.com/Hochfrequenz/ebd_docx_to_table/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/ebd_docx_to_table/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/ebd_docx_to_table/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/ebd_docx_to_table/workflows/Black/badge.svg)
![PyPi Status Badge](https://img.shields.io/pypi/v/ebddocx2table)

This repository contains the source code of the Python package [`ebddocx2table`](https://pypi.org/project/ebddocx2table).

## Rationale

Assume, that you want to analyse or visualize the Entscheidungsbaumdiagramme (EBD) by EDI@Energy.
The website edi-energy.de, as always, only provides you with PDF or Word files instead of _really_ digitized data.

The package `ebddocx2table` scrapes the `.docx` files and returns data in a model defined in the "sister" package [`ebdtable2graph`](https://pypi.org/project/ebdtable2graph).

Once you scraped the data (using this package) you can plot it with [`ebdtable2graph`](https://pypi.org/project/ebdtable2graph).

## How to use this Repository on Your Machine (for development)

Please follow the instructions in
our [Python Template Repository](https://github.com/Hochfrequenz/python_template_repository#how-to-use-this-repository-on-your-machine)
. And for further information, see the [Tox Repository](https://github.com/tox-dev/tox).

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.

## Related Tools and Context

This repository is part of the [Hochfrequenz Libraries and Tools for a truly digitized market communication](https://github.com/Hochfrequenz/digital_market_communication/).
