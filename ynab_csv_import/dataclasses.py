from dataclasses import dataclass


@dataclass
class FieldMapping:
    ynab_field: str
    csv_field: str | None = None
    note: str = ""
