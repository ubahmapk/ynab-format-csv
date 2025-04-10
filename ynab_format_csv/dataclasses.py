from dataclasses import dataclass, field

"""
This data class wouldn't normallly require a dedicated file,
but this seemed the easiest way to resolve the recursive import issue.
"""


@dataclass
class FieldMapping:
    """
    A dataclass for mapping YNAB fields to CSV fields.

    Attributes
    ----------
    ynab_field : str
        The name of the field in YNAB.
    csv_field : str, optional
        The name of the corresponding field in the CSV file. Defaults to an empty string.
    transaction_type_field : str, optional
        If the CSV file includes a "Transaction Type" field, which reports if the transaction
        is a deposit or withdrawal, the name of that field is listed here.
    note : str, optional
        An optional note about the field mapping. Defaults to an empty string.
    """

    ynab_field: str
    csv_field: str = ""
    note: str = ""


@dataclass
class MappingSet:
    fields: list[FieldMapping] = field(default_factory=list)
    transaction_field: bool = False
