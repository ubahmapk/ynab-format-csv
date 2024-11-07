from pathlib import Path
from sys import exit, stderr

import click
import pandas as pd
from loguru import logger

from ynab_format_csv.__version__ import __version__
from ynab_format_csv.dataclasses import FieldMapping
from ynab_format_csv.fileio import (
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
    log_level: str = "INFO"

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


def generate_ynab_header_fields() -> list[FieldMapping]:
    """
    Generate and return the list of YNAB header fields.

    Available fields taken from YNAB documentation:
    https://support.ynab.com/en_us/formatting-a-csv-file-an-overview-BJvczkuRq#texteditor

    Returns
    -------
    list of FieldMapping
        A list of FieldMapping objects representing the YNAB header fields.
    """

    return [
        FieldMapping(ynab_field="Date"),
        FieldMapping(ynab_field="Payee"),
        FieldMapping(ynab_field="Memo"),
        FieldMapping(ynab_field="Amount", note="A single field for both inflow and outflow"),
        FieldMapping(ynab_field="Outflow", note="Used if separate fields are used for inflow and outflow"),
        FieldMapping(ynab_field="Inflow", note="Used if separate fields are used for inflow and outflow"),
    ]


def print_sample_rows(df: pd.DataFrame, num_rows: int = 5) -> None:
    """
    Print a sample of the rows from the CSV file, to help the user see what the data looks like.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the CSV file data.
    num_rows : int, optional
        The number of rows to display from the DataFrame (default is 5).

    Returns
    -------
    None
    """

    click.echo()
    click.echo(f"Sample of the first {num_rows} rows in the CSV file:")
    click.echo(df.head(num_rows).to_string(index=False))

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
        prompt_text: str = f"\nWhich field should be used as the {field_name} field?\n\n"
        prompt_text += f"0. Skip {field_name} field\n"
        for i, header_field in enumerate(csv_header_fields):
            prompt_text += f"{i+1}. {header_field}\n"

        prompt_text += "\n"
        choice: int = click.prompt(prompt_text, type=int)

        if choice > len(csv_header_fields):
            print("Invalid selection. Try again.")
            continue

        # Return the field name and remove it from future available options
        if choice > 0:
            response_field_name = csv_header_fields.pop(choice - 1)

        return response_field_name


def map_csv_header_fields(ynab_header_fields: list[FieldMapping], csv_header_fields: list[str]) -> list[FieldMapping]:
    """
    Map the header fields to the YNAB fields.

    Parameters
    ----------
    ynab_header_fields : list[FieldMapping]
        A list of FieldMapping objects representing the YNAB header fields.
    csv_header_fields : list[str]
        A list of strings representing the CSV header fields.

    Returns
    -------
    list[FieldMapping]
        A list of FieldMapping objects with the CSV fields mapped to the YNAB fields.
    """

    for field in ynab_header_fields:
        field.csv_field = choose_field(field.ynab_field, csv_header_fields)

    return ynab_header_fields


def filter_dataframe(df: pd.DataFrame, field_mapping: list[FieldMapping]) -> pd.DataFrame:
    """
    Filter the transaction entries to only include the mapped fields, and properly renamed.

    Parameters
    ----------
    df : pd.DataFrame
        The CSV transaction data as a DataFrame.
    field_mapping : list[FieldMapping]
        A list of FieldMapping objects that define the mapping between CSV fields and YNAB fields.

    Returns
    -------
    pd.DataFrame
        The filtered and renamed CSV transaction data as a DataFrame.

    Raises
    ------
    KeyError
        The saved mapping file does not match the transaction file.
    """

    fields: list[str] = [
        field.ynab_field for field in field_mapping if (field.csv_field and field.csv_field.lower() != "skipped")
    ]

    mapping_dict: dict = {field.csv_field: field.ynab_field for field in field_mapping}

    # Rename the columns based on the field mapping
    df.rename(columns=mapping_dict, inplace=True)
    try:
        modified_df: pd.DataFrame = df[fields]
    except KeyError:
        click.secho(f"Hmmm.... It looks like the saved mapping file does not match the transaction file.", fg="red")
        click.echo(f"Please check that the correct files are being used.")
        click.echo()
        exit(1)

    return modified_df


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
    save_mapping: bool = click.confirm("Would you like to save this mapping to a file?", default=True)

    if save_mapping:
        file_path: Path = click.prompt("Enter the path to save the mapping file", type=click.Path())
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
    help="The path to the YAML file with saved field mappings",
)
@click.version_option(__version__, "-V", "--version")
@click.option("-v", "--verbosity", help="Repeat for debug messaging", count=True)
@click.help_option("-h", "--help")
@click.command()
def main(csv_file: Path, config_file: Path, verbosity: int) -> None:
    """Python script to prepare a CSV transaction file for import into YNAB"""

    # Set the logging level
    set_logging_level(verbosity)

    # Read the CSV file
    df: pd.DataFrame = read_csv_transaction_file(csv_file)

    # Read the header fields
    header_fields: list[str] = df.columns.tolist()
    ynab_header_fields: list[FieldMapping] = generate_ynab_header_fields()
    print_sample_rows(df)

    mapping: list[FieldMapping] = []

    if config_file:
        mapping = read_field_mappings_from_yaml(config_file)

    # If there's an error reading the YAML mapping, the resulting list will still be empty
    if not mapping:
        mapping = map_csv_header_fields(ynab_header_fields, header_fields)

    print(f"Field mapping:")
    for map in mapping:
        print(f"\t{map.ynab_field}\t<- {map.csv_field}")
    print()

    updated_df: pd.DataFrame = filter_dataframe(df, mapping)

    # Print sample of the updated dataframe
    print_sample_rows(updated_df)

    # Write the updated DataFrame to a new CSV file
    write_dataframe_to_csv_file(updated_df, csv_file.with_suffix(".ynab.csv"))

    # Prompt to save the field mapping to a YAML file
    if not config_file:
        prompt_to_save_mapping(mapping)

    return None