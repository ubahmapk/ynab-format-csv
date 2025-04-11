import pytest
import pandas as pd
from pathlib import Path
from ynab_format_csv.dataclasses import FieldMapping


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data"""
    return tmp_path / "test_data"


@pytest.fixture
def sample_csv_file(test_data_dir):
    """Create a sample CSV file for testing"""
    test_data_dir.mkdir(exist_ok=True)
    file_path = test_data_dir / "transactions.csv"

    df = pd.DataFrame(
        {
            "Date": ["2023-01-01", "2023-01-02"],
            "Description": ["Test Payment", "Test Deposit"],
            "Amount": [-50.00, 100.00],
        }
    )

    df.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_mapping_file(test_data_dir):
    """Create a sample mapping YAML file for testing"""
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir / "mapping.yaml"


@pytest.fixture
def cli_runner():
    """Provide a CLI runner for testing Typer commands"""
    from typer.testing import CliRunner

    return CliRunner()
