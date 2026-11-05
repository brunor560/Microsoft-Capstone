# Billing export format (BIL-7)

`GET /api/todos/export.csv` returns the todo list for the billing team's
nightly ingest. The ingest parses the file **byte for byte**, so every rule
below is part of the contract. Changing any of them breaks billing.

| Rule | Detail |
|---|---|
| Encoding | UTF-8, no byte-order mark |
| Line ending | `CRLF` after every line, including the last |
| Header | Exactly `ID,TITLE,DONE` |
| Row order | Open todos first, then completed ones; by id ascending inside each group |
| `ID` | The todo id, zero-padded to 6 digits (`42` → `000042`) |
| `TITLE` | Titles longer than 40 characters are cut to their first 39 characters followed by `~` |
| Spreadsheet guard (SEC-31) | A title (after cutting) that starts with `=`, `+`, `-` or `@` gets a leading `'` |
| `DONE` | `Y` for completed, `N` for open |
| Empty list | The header line only |

## Quoting

Fields follow RFC 4180: a field that contains a comma, a double quote, a
carriage return or a line feed is wrapped in double quotes, and each double
quote inside it is doubled. Other fields are not quoted. Quoting is applied
last, after cutting and the spreadsheet guard.

Example:

```
ID,TITLE,DONE
000003,Buy milk,N
000007,"Call Sam, then Alex",N
000001,'=SUM(A1),Y
```

The module is `app/legacy/billing-export.js`. It has no tests.
