import sys
from contextlib import contextmanager
from io import StringIO

from ynab_csv_import.app import choose_field


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


def test_choose_field() -> None:

    header_fields = ["Date", "Payee"]
    field_name = "Date"

    with replace_stdin(StringIO("1")):
        response = choose_field(field_name, header_fields)
