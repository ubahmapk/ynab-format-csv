import pytest
import pandas as pd
import yaml
from pathlib import Path
from unittest.mock import mock_open, patch, MagicMock

from ynab_format_csv.dataclasses import FieldMapping
from ynab_format_csv.fileio import (
    write_field_mappings_to_yaml,
    read_field_mappings_from_yaml,
    read_csv_transaction_file,
    write_dataframe_to_csv_file,
)


# Fixtures
@pytest.fixture
def sample_field_mappings():
    return [
        FieldMapping(ynab_field="Date", csv_field="Transaction Date"),
        FieldMapping(ynab_field="Payee", csv_field="Description"),
        FieldMapping(ynab_field="Amount", csv_field="Amount"),
    ]


@pytest.fixture
def sample_yaml_content():
    return """
- ynab_field: Date
  csv_field: Transaction Date
  note: ''
- ynab_field: Payee
  csv_field: Description
  note: ''
- ynab_field: Amount
  csv_field: Amount
  note: ''
"""


@pytest.fixture
def sample_csv_content():
    return """Transaction Date,Description,Amount
2023-01-01,Grocery Store,-50.00
2023-01-02,Salary,1000.00"""


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "Transaction Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Grocery Store", "Salary"],
            "Amount": [-50.00, 1000.00],
        }
    )


# Test write_field_mappings_to_yaml
def test_write_field_mappings_to_yaml_success(sample_field_mappings, tmp_path):
    """Test successful writing of field mappings to YAML file"""
    output_file = tmp_path / "mappings.yaml"

    write_field_mappings_to_yaml(sample_field_mappings, output_file)

    assert output_file.exists()
    with open(output_file) as f:
        content = yaml.safe_load(f)

    assert len(content) == 3
    assert content[0]["ynab_field"] == "Date"
    assert content[0]["csv_field"] == "Transaction Date"


def test_write_field_mappings_to_yaml_permission_error(sample_field_mappings):
    """Test handling of permission error when writing YAML file"""
    with pytest.raises(SystemExit) as exc_info:
        with patch("pathlib.Path.open", side_effect=PermissionError):
            write_field_mappings_to_yaml(sample_field_mappings, Path("/invalid/path"))

    assert exc_info.value.code == 1


# Test read_field_mappings_from_yaml
def test_read_field_mappings_from_yaml_success(sample_yaml_content, tmp_path):
    """Test successful reading of field mappings from YAML file"""
    input_file = tmp_path / "mappings.yaml"
    with open(input_file, "w") as f:
        f.write(sample_yaml_content)

    result = read_field_mappings_from_yaml(input_file)

    assert len(result) == 3
    assert isinstance(result[0], FieldMapping)
    assert result[0].ynab_field == "Date"
    assert result[0].csv_field == "Transaction Date"


def test_read_field_mappings_from_yaml_invalid_yaml(tmp_path):
    """Test handling of invalid YAML content"""
    input_file = tmp_path / "invalid.yaml"
    with open(input_file, "w") as f:
        f.write("invalid: yaml: content:")

    result = read_field_mappings_from_yaml(input_file)
    assert result == []


def test_read_field_mappings_from_yaml_corrupt_mapping(tmp_path):
    """Test handling of valid YAML but invalid mapping structure"""
    input_file = tmp_path / "corrupt.yaml"
    with open(input_file, "w") as f:
        f.write("- invalid_field: value")

    result = read_field_mappings_from_yaml(input_file)
    assert result == []


# Test read_csv_transaction_file
def test_read_csv_transaction_file_success(sample_csv_content, tmp_path):
    """Test successful reading of CSV file"""
    input_file = tmp_path / "transactions.csv"
    with open(input_file, "w") as f:
        f.write(sample_csv_content)

    result = read_csv_transaction_file(input_file)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["Transaction Date", "Description", "Amount"]


def test_read_csv_transaction_file_not_found():
    """Test handling of non-existent CSV file"""
    with pytest.raises(SystemExit) as exc_info:
        read_csv_transaction_file(Path("nonexistent.csv"))

    assert exc_info.value.code == 1


# Test write_dataframe_to_csv_file
def test_write_dataframe_to_csv_file_success(sample_dataframe, tmp_path):
    """Test successful writing of DataFrame to CSV file"""
    output_dir = tmp_path
    file_path = Path("output.csv")

    write_dataframe_to_csv_file(sample_dataframe, output_dir, file_path)

    output_file = output_dir / file_path
    assert output_file.exists()

    # Verify content
    df_read = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df_read, sample_dataframe)


def test_write_dataframe_to_csv_file_default_directory(sample_dataframe, tmp_path):
    """Test writing CSV file to default directory when output_dir is None"""
    file_path = Path("output.csv")

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        write_dataframe_to_csv_file(sample_dataframe, None, file_path)

    output_file = tmp_path / file_path
    assert output_file.exists()


# Integration tests
def test_full_mapping_workflow(sample_field_mappings, sample_dataframe, tmp_path):
    """Test the full workflow of writing mappings to YAML and reading them back"""
    # Write mappings
    yaml_file = tmp_path / "mappings.yaml"
    write_field_mappings_to_yaml(sample_field_mappings, yaml_file)

    # Read mappings back
    read_mappings = read_field_mappings_from_yaml(yaml_file)

    # Verify
    assert len(read_mappings) == len(sample_field_mappings)
    for original, read in zip(sample_field_mappings, read_mappings):
        assert original.ynab_field == read.ynab_field
        assert original.csv_field == read.csv_field


def test_full_csv_workflow(sample_dataframe, tmp_path):
    """Test the full workflow of writing CSV data and reading it back"""
    # Write CSV
    file_path = Path("test.csv")
    write_dataframe_to_csv_file(sample_dataframe, tmp_path, file_path)

    # Read CSV back
    read_df = read_csv_transaction_file(tmp_path / file_path)

    # Verify
    pd.testing.assert_frame_equal(read_df, sample_dataframe)
