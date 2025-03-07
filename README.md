# YNAB Format CSV

Python script to format a CSV transaction file for import into YNAB

## Usage

```
Usage: ynab-format-csv [OPTIONS] CSV_FILE

  Python script to prepare a CSV transaction file for import into YNAB.

  This script accepts one argument, CSV_FILE, which should contain the
  transaction data from your bank.

Options:
  -h, --help         Show this message and exit.
  -v, --verbosity    Repeat for debug messaging
  -V, --version      Show the version and exit.
  -c, --config PATH  The path to the YAML file with saved field mappings
```

Output files are saved with the same name as the input file, but with a ".ynab.csv" extension.

## Sample (Partial) Run

```shell
ynab-format-csv -f bank-transaction-export-file.csv

Sample of the first 5 rows in the CSV file:
Trans. Date  Post Date         Description  Amount       Category
 10/01/2024 10/01/2024       GROCERY STORE   50.00      Groceries
 10/02/2024 10/02/2024         COFFEE SHOP    5.00    Restaurants
 10/03/2024 10/03/2024         GAS STATION   40.00 Transportation
 10/04/2024 10/04/2024 ONLINE SUBSCRIPTION   12.99  Entertainment
 10/05/2024 10/05/2024          RESTAURANT   30.00    Restaurants

Which field should be used as the Date field?

0. Skip Date field
1. Trans. Date
2. Post Date
3. Description
4. Amount
5. Category

:
```

## Data Format

File format information is taken from YNAB's [online documentation for CSV import files](https://support.ynab.com/en_us/formatting-a-csv-file-an-overview-BJvczkuRq#texteditor).

YNAB requires one of two formats for the CSV import file.

### Option One

This format uses separate fields for outflows and inflows.

| Date       | Payee   | Memo | Outflow | Inflow |
|------------|---------|------|---------|--------|
| 06/22/2021 | Payee 1 | Memo | 100.00  |        |
| 06/23/2021 | Payee 2 | Memo |         | 500.00 |

Each field is separated by a comma, so it's important that every field is present in each line—even if your transactions don't fill every field. Always include the "Date,Payee,Memo,Outflow,Inflow" header line at the very top. Any field can be left blank except the date.

### Option Two

This format has one small variation—the amount is one field instead of two. Outflows are identified by a negative sign in the Amount field.

| Date       | Payee   | Memo | Amount  |
|------------|---------|------|---------|
| 06/22/2021 | Payee 1 | Memo | -100.00 |
| 06/22/2021 | Payee 2 | Memo | 500.00  |

## Sample Transactions and Mappings

Sample transaction and mapping files are located in the resources directory
