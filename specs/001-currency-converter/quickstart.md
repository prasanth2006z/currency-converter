# Quickstart: Validate the Currency Converter

Prerequisites: Python 3.11+, run from the repository root.

## Setup

```text
python -m pip install -r requirements.txt
```

`requirements.txt` lists PyYAML and pytest only.

## Run the automated tests

```text
python -m pytest
```

Expected: all tests pass. Every spec example has a named test (see the table in [plan.md](plan.md)).

## Try the examples by hand

| Command | Expected output |
|---------|-----------------|
| `python -m converter 100 US` | `9000.00 INR` |
| `python -m converter 100 CA` | `10000.00 INR` |
| `python -m converter 2.50 US` | `225.00 INR` |
| `python -m converter 100 us` | `9000.00 INR` |
| `python -m converter 1000000 US` | `90000000.00 INR` |
| `python -m converter 100 UK` | error: `Only US and CA are supported` |
| `python -m converter 0 US` | error: `Amount must be more than 0` |
| `python -m converter -5 CA` | error: `Amount must be more than 0` |
| `python -m converter abc US` | error: `Amount must be a number` |
| `python -m converter 1000001 US` | error: `Amount must be 1000000 or less` |
| `python -m converter -1e5 US` | error: `Amount must be a number` |
| `python -m converter 0.00001 US` | error: `Amount is too small to convert` |
| `python -m converter 100` | usage message, exit code 2 |

Exact output formats and exit codes: [contracts/cli.md](contracts/cli.md).

## Check the log

After the successful runs above, `logs/conversions.log` has one line per success and none for the
errors, for example `2026-10-17T10:15:30+00:00 | 100 | US | 9000.00`. Field details:
[data-model.md](data-model.md).

## Check the rates rule

Rates are only in `config/rates.yaml`. Any change to that file needs recorded Product Owner approval
before it is merged.
