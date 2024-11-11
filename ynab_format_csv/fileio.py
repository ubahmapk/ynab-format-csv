from pathlib import Path
from sys import exit

import click
import pandas as pd
import yaml

from ynab_format_csv.dataclasses import FieldMapping


def write_field_mappings_to_yaml(field_mappings: list[FieldMapping], file_path: Path) -> None:
    """Save field mappings to a YAML file.

    Parameters
    ----------
    field_mappings : list[FieldMapping]
        The list of FieldMapping instances to write.
    file_path : Path
        The file name (including optional path) of the YAML file to write.

    Returns
    -------
    None
    """

    # Convert FieldMapping instances to dictionaries
    mappings_dict: list[dict[str, str]] = [field_mapping.__dict__ for field_mapping in field_mappings]

    try:
        # Write the list of dictionaries to a YAML file
        with Path.open(file_path, "w") as file:
            yaml.safe_dump(mappings_dict, file)
    except OSError as e:
        click.secho(f"Error writing to file: {file_path}. {e}", fg="red")
        exit(1)
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")
        exit(1)

    print(f"Field mappings written to {file_path}")

    return None


def read_field_mappings_from_yaml(file_path: Path) -> list[FieldMapping]:
    """
    Read previously saved field mappings from a YAML file.

    Parameters
    ----------
    file_path : Path
        The path to the YAML file.

    Returns
    -------
    list of FieldMapping
        The list of FieldMapping instances read from the YAML file.
    """

    mappings_dict: list[dict] = []
    field_mappings: list[FieldMapping] = []

    try:
        # Read the YAML file into a list of dictionaries
        with Path.open(file_path, "r") as file:
            mappings_dict = yaml.safe_load(file)
    except yaml.YAMLError as e:
        click.secho(f"Error parsing YAML file: {e}", fg="red")
        click.echo(f'Perhaps the file "{file_path}" is not a valid YAML file?')
        click.echo()
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")

    # Convert the dictionaries to FieldMapping instances
    try:
        field_mappings = [FieldMapping(**mapping) for mapping in mappings_dict]
    except TypeError as e:
        click.secho(f"Error reading mapping file: {e}", fg="red")
        click.echo(f"Perhaps the saved mapping file {file_path} is corrupt?")
        click.echo()

    return field_mappings


def read_csv_transaction_file(file_path: Path) -> pd.DataFrame:
    """
    Read the CSV transaction file and return a DataFrame.

    Parameters
    ----------
    file_path : Path
        The path to the CSV file to be read.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the data from the CSV file.

    Raises
    ------
    IOError
        If there is an error reading the file.
    """

    try:
        df: pd.DataFrame = pd.read_csv(file_path)
    except OSError:
        click.secho(f"Error reading file: {file_path}", fg="red")
        exit(1)

    return df


def write_dataframe_to_csv_file(df: pd.DataFrame, output_dir: Path, file_path: Path) -> None:
    """
    Write the DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame (of transactions) to be written to the CSV file.
    file_path : Path
        The file name (and optional path) to write the CSV data to.
    output_dir : Path
        The directory to save the updated CSV file to.

    Returns
    -------
    None
    """

    if not output_dir:
        output_dir = Path.cwd()

    full_path: Path = Path.joinpath(output_dir, file_path.name)
    df.to_csv(full_path, float_format="%.2f", index=False)
    print(f"Updated data written to {full_path}")
    print()

    return None
