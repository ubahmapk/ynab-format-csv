from dataclasses import dataclass

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
    csv_field : str or None, optional
        The name of the corresponding field in the CSV file. Defaults to None.
    note : str, optional
        An optional note about the field mapping. Defaults to an empty string.
    """

    ynab_field: str
    csv_field: str | None = None
    note: str = ""
