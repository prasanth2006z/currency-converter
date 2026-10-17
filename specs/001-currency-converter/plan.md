# Implementation Plan: Currency Converter (US/CA to INR)

**Branch**: `001-currency-converter` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-currency-converter/spec.md`

## Summary

A small offline command-line tool: `python -m converter 100 US` prints `9000.00 INR`. It checks the
input, reads the rate for the country from `config/rates.yaml`, multiplies with exact `Decimal`
maths, rounds half up to 2 decimals, appends one line to `logs/conversions.log`, and prints the
result. Invalid input prints the exact spec error message and never a number. Structure is three
small parts (input checker, rate reader, calculator) plus a thin CLI entry point.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: standard library (`argparse`, `decimal`, `re`, `datetime`, `pathlib`) and PyYAML

**Storage**: Files only: `config/rates.yaml` (read) and `logs/conversions.log` (append)

**Testing**: pytest

**Target Platform**: Any OS with Python 3.11+, run from the repository root

**Project Type**: CLI

**Performance Goals**: Instant response (SC-003); no measurable work beyond reading one small file

**Constraints**: Fully offline; `Decimal` only (no `float`); no dependencies beyond PyYAML and pytest

**Scale/Scope**: One command, two countries, one user at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How the plan meets it |
|-----------|--------|-----------------------|
| I. Rates in one settings file | Pass | Rates exist only in `config/rates.yaml`; code has no rate numbers. Tests use their own fixture rate file. |
| II. Product Owner approves rate changes | Pass (process) | Documented in quickstart; any change to `config/rates.yaml` needs recorded approval at review. |
| III. Exact decimal money | Pass | `Decimal` end to end, amount parsed from text, rates via `Decimal(str(value))`, `ROUND_HALF_UP` at the end. |
| IV. Every conversion logged | Pass | One line per successful conversion with time, amount, country, result. |
| V. Fully offline | Pass | No network imports or calls. |
| VI. Test-first | Pass | Each spec example maps to a named pytest test (table below); tests are written and seen failing before code. |
| VII. Keep it simple | Pass | Python 3.11+, stdlib + PyYAML + pytest, no framework. |
| VIII. Invalid input fails loudly | Pass | Checker runs before any calculation; errors go to stderr with a non-zero exit code and no result. |

**Post-design re-check**: all gates still pass. No violations, so no Complexity Tracking entries.

## Design

### The parts

| Part | File | Job |
|------|------|-----|
| Input checker | `converter/checker.py` | Checks amount then country; returns a `Decimal` amount and upper-case country code, or raises `InputError(message)`. |
| Rate reader | `converter/rates.py` | Reads `config/rates.yaml` and returns the `Decimal` rate for a country. |
| Calculator | `converter/calculator.py` | `amount * rate`, rounded half up to 2 decimals, returned as `Decimal`. |
| CLI entry | `converter/cli.py`, `converter/__main__.py` | argparse, wires the parts, writes the log line, prints the result or error. |

### Checking order (decides which error wins)

1. Amount is a number: must match `^-?\d+(\.\d+)?$`. This rejects `abc`, `1,000`, `1e5`, `nan`, `inf`, empty text and spaces. Otherwise "Amount must be a number".
2. Amount is more than 0, otherwise "Amount must be more than 0".
3. Amount is 1000000 or less, otherwise "Amount must be 1000000 or less".
4. Country, compared in upper case, is one of the countries in `rates.yaml`, otherwise "Only US and CA are supported".

The amount is checked first, so `abc UK` shows only the amount error (spec clarification).

### Exactness

- The amount is converted with `Decimal(text)` and never passes through `float`.
- The calculator multiplies inside a local `decimal` context whose precision is large enough for the input length, so the multiplication is exact. Only the final `quantize(Decimal("0.01"), ROUND_HALF_UP)` rounds.
- The result is printed with `format(result, "f")`: no thousands separator and no exponent (`90000000.00`).

### Rates file

```yaml
rates:
  US: 90
  CA: 100
```

The reader looks for the file at `<repo root>/config/rates.yaml` (found from the package location, so
it works from any directory). Functions also accept an explicit path so tests can use fixtures.
If the file is missing, unreadable, not valid YAML, or does not define both US and CA, the CLI shows
"Rates are unavailable" and exits non-zero, with no number shown (FR-018, Principle VIII).

### Log line

`logs/conversions.log` is created (with its folder) on first use and appended to, one line per
successful conversion:

```text
2026-10-17T10:15:30+00:00 | 100 | US | 9000.00
```

Fields: UTC ISO timestamp to the second, amount as entered, upper-case country, result in INR,
separated by ` | `. Failed conversions are not logged. The line is written **before** the result
is printed; if writing fails, the CLI shows "Could not write the conversion log" and exits
non-zero without printing a result, so no unlogged conversion is ever shown (FR-019).

### Command line

See [contracts/cli.md](contracts/cli.md). Success prints `<result> INR` to stdout, exit code 0.
Errors print the exact message to stderr, exit code 1. Missing arguments are handled by argparse
(usage message, exit code 2, no number shown).

## Test plan (every spec example is a named test)

Tests live in `tests/`. `tests/test_acceptance.py` drives `converter.cli.main(argv, ...)` with a
fixture rates file and a temporary log path. Unit tests cover each part.

| Spec example | Test name |
|--------------|-----------|
| US1-1: 100 US -> 9000.00 INR | `test_100_us_gives_9000_00` |
| US1-2: 100 CA -> 10000.00 INR | `test_100_ca_gives_10000_00` |
| US1-3: 2.50 US -> 225.00 INR | `test_2_50_us_gives_225_00` |
| US1-4: 100 us -> 9000.00 INR | `test_lowercase_country_accepted` |
| US1-5: 1000000 US -> 90000000.00 INR | `test_max_amount_us_no_thousands_separator` |
| US1-6: 1000000 CA -> 100000000.00 INR | `test_max_amount_ca_no_thousands_separator` |
| US2-1: 100 UK -> "Only US and CA are supported" | `test_unsupported_country_error` |
| US2-2: 0 US -> "Amount must be more than 0" | `test_zero_amount_error` |
| US2-3: -5 CA -> "Amount must be more than 0" | `test_negative_amount_error` |
| US2-4: abc US -> "Amount must be a number" | `test_non_numeric_amount_error` |
| US2-5: 1000001 US -> "Amount must be 1000000 or less" | `test_amount_over_maximum_error` |
| US2-6: 1,000 US -> "Amount must be a number" | `test_comma_amount_error` |
| US2-7: 1e5 US -> "Amount must be a number" | `test_scientific_notation_error` |
| US2-8: abc UK -> only the amount error | `test_amount_error_wins_over_country_error` |
| US3-1: log record for 100 US | `test_successful_conversion_is_logged` |
| Edge: mixed case `Ca` | `test_mixed_case_country_accepted` |
| Edge: 2.505 (more than 2 decimals) | `test_extra_decimals_converted_exactly` |
| Edge: empty amount / empty country | `test_empty_amount_error`, `test_empty_country_error` |
| FR-017 / Edge: `.5` -> "Amount must be a number" | `test_leading_dot_amount_error` |
| FR-017 / Edge: `5.` -> "Amount must be a number" | `test_trailing_dot_amount_error` |
| FR-017 / Edge: `+5` -> "Amount must be a number" | `test_plus_sign_amount_error` |
| Clarification: half rounds up (0.135 -> 0.14) | `test_half_rounds_up` |
| Clarification: errors are not logged | `test_failed_conversion_is_not_logged` |
| FR-011: rates come from the file | `test_rates_come_from_rates_file` (changed fixture file changes the result) |
| FR-009: no number on any error | `test_no_inr_amount_in_any_error_output` |
| FR-018 / Edge: rates file missing -> "Rates are unavailable" | `test_missing_rates_file_shows_error` |
| FR-018 / Edge: rates file unreadable -> "Rates are unavailable" | `test_unreadable_rates_file_shows_error` |
| FR-019 / Edge: log cannot be written -> "Could not write the conversion log" | `test_log_write_failure_shows_error_and_no_result` |
| Constitution III: no `float` in code | `test_source_has_no_float` (scans `converter/` for `float`) |

## Project Structure

### Documentation (this feature)

```text
specs/001-currency-converter/
|-- plan.md              # This file
|-- research.md          # Phase 0 output
|-- data-model.md        # Phase 1 output
|-- quickstart.md        # Phase 1 output
|-- contracts/
|   `-- cli.md           # Phase 1 output
|-- checklists/
|   `-- requirements.md
`-- tasks.md             # Phase 2 output (/speckit-tasks, not created here)
```

### Source Code (repository root)

```text
config/
`-- rates.yaml           # US: 90, CA: 100 (Product Owner approval to change)
converter/
|-- __init__.py
|-- __main__.py          # python -m converter
|-- cli.py               # argparse, wiring, log line, output
|-- checker.py           # input checker
|-- rates.py             # rate reader
`-- calculator.py        # Decimal maths and rounding
tests/
|-- test_acceptance.py   # spec examples through cli.main
|-- test_checker.py
|-- test_rates.py
|-- test_calculator.py
`-- test_constitution.py # no float in source
logs/
`-- conversions.log      # created at runtime; git-ignored
requirements.txt         # PyYAML, pytest
```

**Structure Decision**: Single flat package `converter/` with one module per part. No sub-packages,
classes or abstractions beyond one `InputError` exception.

## Complexity Tracking

No constitution violations; nothing to justify.
