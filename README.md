# YNAB CSV Import

Python script to prepare a CSV file for import into YNAB

## Usage

```shell
Usage: ynab-csv-import [OPTIONS]

  Python script to prepare a CSV transaction file for import into YNAB

Options:
  -h, --help         Show this message and exit.
  -v, --verbosity    Repeat for debug messaging
  -V, --version      Show the version and exit.
  -c, --config PATH  The path to the YAML file containing the field mappings
  -f, --file PATH    CSV transaction file from your bank
```

## Data Format

File format information is taken from YNAB's [online documentation for CSV import files](https://support.ynab.com/en_us/formatting-a-csv-file-an-overview-BJvczkuRq#texteditor).

YNAB requires one of two formats for the CSV import file.

### Option One

This format uses separate fields for outflows and inflows.

| Date       | Payee   | Memo | Outflow | Inflow |
| ---------- | ------- | ---- | ------- | ------ |
| 06/22/2021 | Payee 1 | Memo | 100.00  |        |
| 06/23/2021 | Payee 2 | Memo |         | 500.00 |

Each field is separated by a comma, so it's important that every field is present in each line—even if your transactions don't fill every field. Always include the "Date,Payee,Memo,Outflow,Inflow" header line at the very top. Any field can be left blank except the date.

### Option Two

This format has one small variation—the amount is one field instead of two. Outflows are identified by a negative sign in the Amount field.

| Date       | Payee   | Memo | Amount  |
| ---------- | ------- | ---- | ------- |
| 06/22/2021 | Payee 1 | Memo | -100.00 |
| 06/22/2021 | Payee 2 | Memo |  500.00 |
