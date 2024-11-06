from pathlib import Path
from sys import stderr

import click
import pandas as pd
from loguru import logger

from ynab_csv_import.__version__ import __version__
from ynab_csv_import.dataclasses import FieldMapping
from ynab_csv_import.fileio import (
    read_csv_transaction_file,
    read_field_mappings_from_yaml,
    write_dataframe_to_csv_file,
    write_field_mappings_to_yaml,
)


def set_logging_level(verbosity: int) -> None:
    """
    Set the global logging level based on the verbosity level provided.

    Parameters
    ----------
    verbosity : int
        Verbosity level to set the logging level.
        - 0 or None: ERROR level
        - 1: INFO level
        - >1: DEBUG level

    Returns
    -------
    None
    """

    # Default level
    log_level = "INFO"

    if verbosity is not None:
        if verbosity == 1:
            log_level = "INFO"
        elif verbosity > 1:
            log_level = "DEBUG"
        else:
            log_level = "ERROR"

    logger.remove(0)
    # noinspection PyUnboundLocalVariable
    logger.add(stderr, level=log_level)

    return None


def read_csv_header_fields(df: pd.DataFrame) -> list:
    """Read the header fields from the CSV file"""

    return df.columns.tolist()


def generate_ynab_header_fields() -> list[FieldMapping]:
    """Generate the list of YNAB header fields"""

    return [
        FieldMapping(ynab_field="Date"),
        FieldMapping(ynab_field="Payee"),
        FieldMapping(ynab_field="Memo"),
        FieldMapping(ynab_field="Amount", note="A single field for both inflow and outflow"),
        FieldMapping(ynab_field="Outflow", note="Used if separate fields are used for inflow and outflow"),
        FieldMapping(ynab_field="Inflow", note="Used if separate fields are used for inflow and outflow"),
    ]


def print_sample_rows(df: pd.DataFrame, num_rows: int = 5) -> None:
    """Print a sample of the rows in the DataFrame"""

    click.echo()
    click.echo(f"Sample of the first {num_rows} rows in the CSV file:")
    click.echo(df.head(num_rows).to_string(index=False))
    click.echo()

    return None


def choose_field(field_name: str, csv_header_fields: list) -> str:
    """
    Choose a field from the list of header fields.

    Parameters
    ----------
    field_name : str
        The name of the YNAB field to map.
    csv_header_fields : list
        The list of header fields from the CSV file.

    Returns
    -------
    str
        The chosen field name from the CSV header fields, or "Skipped" if no field is chosen.
    """
    response_field_name: str = "Skipped"

    print()
    while True:
        # Loop through the ynab_header_fields and select a header field from the CSV file to map
        prompt_text = f"Which field should be used as the {field_name} field?\n\n"
        prompt_text += f"0. Skip {field_name} field\n"
        for i, header_field in enumerate(csv_header_fields):
            prompt_text += f"{i+1}. {header_field}\n"

        choice = click.prompt(prompt_text, type=int)

        if choice > len(csv_header_fields):
            print("Invalid selection. Try again.")
            continue

        # Return the field name and remove it from future available options
        if choice > 0:
            response_field_name = csv_header_fields.pop(choice - 1)

        return response_field_name


def map_csv_header_fields(ynab_header_fields: list[FieldMapping], csv_header_fields: list[str]) -> list[FieldMapping]:
    """Map the header fields to the YNAB fields"""

    for field in ynab_header_fields:
        field.csv_field = choose_field(field.ynab_field, csv_header_fields)

    return ynab_header_fields


def filter_dataframe(df: pd.DataFrame, field_mapping: list[FieldMapping]) -> pd.DataFrame:
    """Filter the DataFrame to only include the mapped fields, and properly renamed."""

    fields = [field.ynab_field for field in field_mapping if (field.csv_field and field.csv_field.lower() != "skipped")]

    mapping_dict = {field.csv_field: field.ynab_field for field in field_mapping}

    # Rename the columns based on the field mapping
    df.rename(columns=mapping_dict, inplace=True)

    return df[fields]


def prompt_to_save_mapping(field_mapping: list[FieldMapping]) -> None:
    """
    Prompt the user to save the field mapping to a YAML file.

    Parameters
    ----------
    field_mapping : list[FieldMapping]
        A list of FieldMapping objects that represent the field mappings to be saved.

    Returns
    -------
    None
    """

    print()
    save_mapping = click.confirm("Would you like to save this mapping to a file?", default=True)

    if save_mapping:
        file_path = click.prompt("Enter the path to save the mapping file", type=click.Path())
        write_field_mappings_to_yaml(field_mapping, file_path)

    return None


@click.option(
    "-f",
    "--file",
    "csv_file",
    type=click.Path(exists=True, path_type=Path),
    prompt="CSV file",
    help="CSV transaction file from your bank",
)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(exists=True, path_type=Path),
    help="The path to the YAML file containing the field mappings",
)
@click.version_option(__version__, "-V", "--version")
@click.option("-v", "--verbosity", help="Repeat for debug messaging", count=True)
@click.help_option("-h", "--help")
@click.command()
def main(csv_file: Path, config_file: Path, verbosity: int) -> None:
    """Main entry point for the script"""

    # Set the logging level
    set_logging_level(verbosity)

    # Read the CSV file
    df = read_csv_transaction_file(file_path=csv_file)

    # Read the header fields
    header_fields = read_csv_header_fields(df)
    ynab_header_fields = generate_ynab_header_fields()
    print_sample_rows(df)

    if config_file:
        mapping = read_field_mappings_from_yaml(config_file)
    else:
        mapping = map_csv_header_fields(ynab_header_fields, header_fields)

    print(f"Field mapping:")
    for map in mapping:
        print(f"\t{map.ynab_field}\t<- {map.csv_field}")
    print()

    updated_df = filter_dataframe(df, mapping)

    # Print sample of the updated dataframe
    print_sample_rows(updated_df)

    # Write the updated DataFrame to a new CSV file
    write_dataframe_to_csv_file(updated_df, csv_file.with_suffix(".ynab.csv"))

    # Prompt to save the field mapping to a YAML file
    if not config_file:
        prompt_to_save_mapping(mapping)

    return None
