"""
a small click based script to extract all EBDs from a given file.
"""

# invoke like this:
# main.py -i unittests/test_data/ebd20230619_v33.docx
#  -o ../machine-readable_entscheidungsbaumdiagramme/FV2304
#  -t json -t dot -t svg -t puml
# or
# main.py -i unittests/test_data/ebd20230629_v34.docx
#  -o ../machine-readable_entscheidungsbaumdiagramme/FV2310
#  -t json -t dot -t svg -t puml
import json
from pathlib import Path
from typing import Literal

import cattrs
import click
from ebdtable2graph import convert_graph_to_plantuml, convert_table_to_graph
from ebdtable2graph.graphviz import convert_dot_to_svg_kroki, convert_graph_to_dot
from ebdtable2graph.models import EbdGraph, EbdTable
from ebdtable2graph.models.errors import (
    EbdCrossReferenceNotSupportedError,
    EndeInWrongColumnError,
    NotExactlyTwoOutgoingEdgesError,
    OutcomeCodeAmbiguousError,
    PathsNotGreaterThanOneError,
)
from ebdtable2graph.plantuml import GraphTooComplexForPlantumlError

# pylint:disable=import-error
from ebddocx2table import TableNotFoundError, get_all_ebd_keys, get_ebd_docx_tables  # type:ignore[import]
from ebddocx2table.docxtableconverter import DocxTableConverter  # type:ignore[import]


def _dump_puml(puml_path: Path, ebd_graph: EbdGraph) -> None:
    plantuml_code = convert_graph_to_plantuml(ebd_graph)
    with open(puml_path, "w+", encoding="utf-8") as uml_file:
        uml_file.write(plantuml_code)


def _dump_dot(dot_path: Path, ebd_graph: EbdGraph) -> None:
    dot_code = convert_graph_to_dot(ebd_graph)
    with open(dot_path, "w+", encoding="utf-8") as uml_file:
        uml_file.write(dot_code)


def _dump_svg(svg_path: Path, ebd_graph: EbdGraph) -> None:
    dot_code = convert_graph_to_dot(ebd_graph)
    svg_code = convert_dot_to_svg_kroki(dot_code)
    with open(svg_path, "w+", encoding="utf-8") as svg_file:
        svg_file.write(svg_code)


def _dump_json(json_path: Path, ebd_table: EbdTable) -> None:
    with open(json_path, "w+", encoding="utf-8") as json_file:
        json.dump(cattrs.unstructure(ebd_table), json_file, ensure_ascii=False, indent=2, sort_keys=True)


@click.command()
@click.option(
    "-i",
    "--input_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    prompt="Input DOCX File",
    help="Path of a .docx file from which the EBDs shall be extracted",
)
@click.option(
    "-o",
    "--output_path",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    default="output",
    prompt="Output directory",
    help="Define the path where you want to save the generated files",
)
@click.option(
    "-t",
    "--export_types",
    type=click.Choice(["puml", "dot", "json", "svg"], case_sensitive=False),
    multiple=True,
    help="Choose which file you'd like to create",
)
# pylint:disable=too-many-locals, too-many-branches, too-many-statements,
def main(input_path: Path, output_path: Path, export_types: list[Literal["puml", "dot", "json", "svg"]]):
    """
    A program to get a machine-readable version of the AHBs docx files published by edi@energy.
    """
    if output_path.exists():
        click.secho(f"The output directory '{output_path}' exists already.", fg="yellow")
    else:
        output_path.mkdir(parents=True)
        click.secho(f"Created a new directory at {output_path}", fg="green")
    all_ebd_keys = get_all_ebd_keys(input_path)
    error_sources: dict[type, list[str]] = {}

    def handle_known_error(error: Exception, ebd_key: str) -> None:
        click.secho(f"Error while processing EBD {ebd_key}: {error}", fg="yellow")
        if type(error) not in error_sources:
            error_sources[type(error)] = []
        error_sources[type(error)].append(ebd_key)

    for ebd_key, (ebd_title, ebd_kapitel) in all_ebd_keys.items():
        click.secho(f"Processing EBD {ebd_kapitel} '{ebd_key}' ({ebd_title})")
        try:
            docx_tables = get_ebd_docx_tables(docx_file_path=input_path, ebd_key=ebd_key)
        except TableNotFoundError as table_not_found_error:
            click.secho(f"Table not found: {ebd_key}: {str(table_not_found_error)}; Skip!", fg="yellow")
            continue
        assert ebd_kapitel is not None
        try:
            converter = DocxTableConverter(
                docx_tables,
                ebd_key=ebd_key,
                chapter=ebd_kapitel.chapter_title,  # type:ignore[arg-type]
                # pylint:disable=line-too-long
                sub_chapter=f"{ebd_kapitel.chapter}.{ebd_kapitel.section}.{ebd_kapitel.subsection}: {ebd_kapitel.section_title}",
            )
            ebd_table = converter.convert_docx_tables_to_ebd_table()
        except Exception as scraping_error:  # pylint:disable=broad-except
            click.secho(f"Error while scraping {ebd_key}: {str(scraping_error)}; Skip!", fg="red")
            continue
        if "json" in export_types:
            _dump_json(output_path / Path(f"{ebd_key}.json"), ebd_table)
            click.secho(f"💾 Successfully exported '{ebd_key}.json'")
        try:
            ebd_graph = convert_table_to_graph(ebd_table)
        except (EbdCrossReferenceNotSupportedError, EndeInWrongColumnError, OutcomeCodeAmbiguousError) as known_issue:
            handle_known_error(known_issue, ebd_key)
            continue
        except Exception as unknown_error:  # pylint:disable=broad-except
            click.secho(f"Error while graphing {ebd_key}: {str(unknown_error)}; Skip!", fg="red")
            continue
        if "puml" in export_types:
            try:
                _dump_puml(output_path / Path(f"{ebd_key}.puml"), ebd_graph)
                click.secho(f"💾 Successfully exported '{ebd_key}.puml'")
            except AssertionError as assertion_error:
                # https://github.com/Hochfrequenz/ebdtable2graph/issues/35
                click.secho(str(assertion_error), fg="red")
            except (NotExactlyTwoOutgoingEdgesError, GraphTooComplexForPlantumlError) as known_issue:
                handle_known_error(known_issue, ebd_key)
            except Exception as general_error:  # pylint:disable=broad-exception-caught
                click.secho(f"Error while exporting {ebd_key} as UML: {str(general_error)}; Skip!", fg="yellow")

        try:
            if "dot" in export_types:
                _dump_dot(output_path / Path(f"{ebd_key}.dot"), ebd_graph)
                click.secho(f"💾 Successfully exported '{ebd_key}.dot'")
            if "svg" in export_types:
                _dump_svg(output_path / Path(f"{ebd_key}.svg"), ebd_graph)
                click.secho(f"💾 Successfully exported '{ebd_key}.svg'")
        except PathsNotGreaterThanOneError as known_issue:
            handle_known_error(known_issue, ebd_key)
        except AssertionError as assertion_error:
            # e.g. AssertionError: If indegree > 1, the number of paths should always be greater than 1 too.
            click.secho(str(assertion_error), fg="red")
            # both the SVG and dot path require graphviz to work, hence the common error handling block
    click.secho(json.dumps({str(k): v for k, v in error_sources.items()}, indent=4))
    click.secho("🏁Finished")


if __name__ == "__main__":
    # the parameter arguments gets provided over the CLI
    main()  # pylint:disable=no-value-for-parameter
