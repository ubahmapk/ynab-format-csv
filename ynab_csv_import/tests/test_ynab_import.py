import pytest

from ynab_csv_import.app import choose_field


def test_choose_field() -> None:

    header_fields = ["Date", "Payee", "Category", "Memo", "Outflow", "Inflow"]

    assert choose_field("Date", header_fields) == "Date"
    assert choose_field("Payee", header_fields) == "Payee"
    assert choose_field("Category", header_fields) == "Category"
    assert choose_field("Memo", header_fields) == "Memo"
    assert choose_field("Outflow", header_fields) == "Outflow"
    assert choose_field("Inflow", header_fields) == "Inflow"
    assert choose_field("Not a field", header_fields) == "Date"
    assert choose_field("Date", ["Not a field"]) == "Date"
    assert choose_field("Not a field", ["Not a field"]) == "Date"
    assert choose_field("Not a field", []) == "Date"
    assert choose_field("", header_fields) == "Date"
    assert choose_field("", []) == "Date"
    assert choose_field("", ["Not a field"]) == "Date"
    assert choose_field("Date", []) == "Date"
    assert choose_field("Payee", []) == "Date"
    assert choose_field("Category", []) == "Date"
    assert choose_field("Memo", []) == "Date"
    assert choose_field("Outflow", []) == "Date"
    assert choose_field("Inflow", []) == "Date"
