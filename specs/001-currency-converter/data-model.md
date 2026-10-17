# Data Model: Currency Converter

No database. All data is short-lived values in memory, one settings file and one log file.

## Conversion Request (in memory)

| Field | Type | Rules |
|-------|------|-------|
| amount | text from the command line, then `Decimal` | Matches `^-?\d+(\.\d+)?$`; more than 0; at most 1000000 |
| country | text, normalised to upper case | Must be `US` or `CA` (fixed by the spec, not by the rates file) |

Order of steps: amount is a number, amount more than 0, amount at most 1000000, country supported,
read rates, calculate, result not 0.00, write log, print.

## Rate (`config/rates.yaml`)

```yaml
rates:
  US: 90
  CA: 100
```

| Field | Type | Rules |
|-------|------|-------|
| country code | upper-case text key | The map contains exactly `US` and `CA`: a missing or extra key gives "Rates are unavailable" |
| rate | YAML number, read as `Decimal(str(value))` | INR per one dollar; MUST be a number greater than 0 and finite; text, true/false, null, zero, negative or `.inf`/`.nan` give "Rates are unavailable" |

The file must exist, be readable and be valid YAML with a `rates` map. Changing this file requires
Product Owner approval.

## Conversion Result (in memory)

| Field | Type | Rules |
|-------|------|-------|
| inr | `Decimal` | `amount * rate`, rounded half up to 2 decimals, printed with no thousands separator; if it rounds to 0.00 the result is the error "Amount is too small to convert" |

Or an error: one of the exact messages in [contracts/cli.md](contracts/cli.md).

## Conversion Record (`logs/conversions.log`)

One line per successful conversion, appended:

```text
<UTC ISO timestamp> | <amount as entered> | <country, upper case> | <inr, 2 decimals>
```

| Field | Example |
|-------|---------|
| timestamp | `2026-10-17T10:15:30+00:00` |
| amount | `2.50` |
| country | `US` |
| inr | `225.00` |

Failed conversions (including "Amount is too small to convert") are never logged. No state
transitions.
