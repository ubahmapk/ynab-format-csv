# YNAB CSV Import

Python script to prepare a CSV file for import into YNAB

## Data Format

YNAB requires the CSV file to include the following header fields in this order:

- Date
- Payee
- Memo
- Outflow
- Inflow

### Example data - Format 1

| Date       | Payee   | Memo | Outflow | Inflow | 
| ---------- | ------- | ---- | ------- | ------ |
| 06/22/2021 | Payee 1 | Memo |  100.00 |        |
| 06/23/2021 | Payee 2 | Memo |         | 500.00 |

### Example data - Format 2

| Date       | Payee   | Memo | Ammount |
| ---------- | ------- | ---- | ------- |
| 06/22/2021 | Payee 1 | Memo |  100.00 |
| 06/23/2021 | Payee 2 | Memo |  -25.15 |
