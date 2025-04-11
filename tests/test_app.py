import pytest
from pathlib import Path
import pandas as pd
from typer.testing import CliRunner
from loguru import logger
from ynab_format_csv.app import (
    generate_ynab_header_fields,
    print_sample_rows,
    choose_field,
    map_csv_header_fields,
    filter_dataframe,
    prompt_to_save_mapping,
    version_callback,
    app,
)
from ynab_format_csv.dataclasses import FieldMapping


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Test Payment", "Test Deposit"],
            "Amount": [-50.00, 100.00],
        }
    )


@pytest.fixture
def field_mappings():
    """Create sample field mappings"""
    return [
        FieldMapping(ynab_field="Date", csv_field="Date"),
        FieldMapping(ynab_field="Payee", csv_field="Description"),
        FieldMapping(ynab_field="Amount", csv_field="Amount"),
    ]


def test_generate_ynab_header_fields():
    """Test generation of YNAB header fields"""
    fields = generate_ynab_header_fields()
    assert len(fields) == 6
    assert fields[0].ynab_field == "Date"
    assert fields[1].ynab_field == "Payee"
    assert fields[2].ynab_field == "Memo"
    assert fields[3].ynab_field == "Amount"
    assert fields[4].ynab_field == "Outflow"
    assert fields[5].ynab_field == "Inflow"


def test_print_sample_rows(capsys, sample_df):
    """Test printing sample rows from DataFrame"""
    print_sample_rows(sample_df, num_rows=2)
    captured = capsys.readouterr()
    assert "Sample of the first 2 rows in the CSV file:" in captured.out
    assert "Test Payment" in captured.out
    assert "Test Deposit" in captured.out


def test_filter_dataframe(sample_df, field_mappings):
    """Test filtering and renaming DataFrame columns"""
    filtered_df = filter_dataframe(sample_df, field_mappings)
    assert list(filtered_df.columns) == ["Date", "Payee", "Amount"]
    assert len(filtered_df) == 2


def test_filter_dataframe_invalid_mapping(sample_df):
    """Test filtering with invalid mapping"""
    invalid_mappings = [FieldMapping(ynab_field="Date", csv_field="NonexistentField")]
    with pytest.raises(SystemExit):
        filter_dataframe(sample_df, invalid_mappings)


def test_app_main():
    """Test main CLI application"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test CSV file
        df = pd.DataFrame({"Date": ["2023-01-01"], "Description": ["Test"], "Amount": [100]})
        df.to_csv("test.csv", index=False)

        result = runner.invoke(app, ["test.csv"])
        assert result.exit_code == 0


def test_map_csv_header_fields(monkeypatch):
    """Test mapping CSV header fields with mocked user input"""

    def mock_choose_field(field_name, csv_header_fields):
        mapping = {"Date": "TransactionDate", "Payee": "Description", "Amount": "Amount"}
        return mapping.get(field_name, "Skipped")

    monkeypatch.setattr("ynab_format_csv.app.choose_field", mock_choose_field)

    ynab_fields = [FieldMapping(ynab_field="Date"), FieldMapping(ynab_field="Payee"), FieldMapping(ynab_field="Amount")]
    csv_fields = ["TransactionDate", "Description", "Amount"]

    result = map_csv_header_fields(ynab_fields, csv_fields)
    assert result[0].csv_field == "TransactionDate"
    assert result[1].csv_field == "Description"
    assert result[2].csv_field == "Amount"


def test_prompt_to_save_mapping(monkeypatch, tmp_path, field_mappings):
    """Test prompting to save mapping with mocked user input"""
    # Mock user confirming save and providing file path
    responses = iter(["y", str(tmp_path / "mapping.yaml")])
    monkeypatch.setattr("typer.confirm", lambda *args, **kwargs: next(responses) == "y")
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: next(responses))

    prompt_to_save_mapping(field_mappings)
    assert (tmp_path / "mapping.yaml").exists()
