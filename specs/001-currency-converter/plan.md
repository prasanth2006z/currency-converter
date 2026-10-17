# Implementation Plan: Currency Converter (US/CA to INR)

**Branch**: `001-currency-converter` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-currency-converter/spec.md`

## Summary

A small offline command-line tool: `python -m converter 100 US` prints `9000.00 INR`. It checks the
input, reads the rates from `config/rates.yaml`, multiplies with exact `Decimal` maths, rounds half
up to 2 decimals, appends one line to `logs/conversions.log`, and prints the result. Invalid input
prints the exact spec error message and never a number. Structure is three small parts (input
checker, rate reader, calculator) plus a thin CLI entry point.

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
| I. Rates in one settings file | Pass | Rates exist only in `config/rates.yaml`. An automated test fails if a rate value appears as a literal in `converter/`. Tests use their own fixture rate files. |
| II. Product Owner approves rate changes | Pass (process) | Documented in quickstart; any change to `config/rates.yaml` needs recorded approval at review. |
| III. Exact decimal money | Pass | `Decimal` end to end, amount parsed from text, rates via `Decimal(str(value))`, `ROUND_HALF_UP` at the end. An automated test fails if `float` is used in `converter/`. |
| IV. Every conversion logged | Pass | One line per successful conversion with time, amount, country, result. |
| V. Fully offline | Pass | An automated test fails if `converter/` imports a network module. |
| VI. Test-first | Pass | Each spec example maps to a named pytest test (table below); tests are written and seen failing before code. |
| VII. Keep it simple | Pass | Python 3.11+, stdlib + PyYAML + pytest, no framework. |
| VIII. Invalid input fails loudly | Pass | Checker runs before any calculation; rates are validated; errors go to stderr with a non-zero exit code and no result. |

**Post-design re-check**: all gates still pass. No violations, so no Complexity Tracking entries.

## Design

### The parts

| Part | File | Job |
|------|------|-----|
| Input checker | `converter/checker.py` | Checks amount then country; returns a `Decimal` amount and upper-case country code, or raises `InputError(message)`. The supported countries `US` and `CA` are fixed in this file (spec FR-002). |
| Rate reader | `converter/rates.py` | Reads and validates `config/rates.yaml`; returns `{"US": Decimal, "CA": Decimal}` or raises `RatesError`. |
| Calculator | `converter/calculator.py` | `amount * rate`, rounded half up to 2 decimals, returned as `Decimal`. |
| CLI entry | `converter/cli.py`, `converter/__main__.py` | argparse, runs the steps in order, writes the log line, prints the result or error. |

### Order of steps (decides which error wins, spec FR-023)

1. Amount is a number: must match `^-?\d+(\.\d+)?$`. This rejects `abc`, `1,000`, `1e5`, `nan`, `inf`, `.5`, `5.`, `+5`, empty text and spaces. Otherwise "Amount must be a number".
2. Amount is more than 0, otherwise "Amount must be more than 0".
3. Amount is 1000000 or less, otherwise "Amount must be 1000000 or less".
4. Country, compared in upper case, is `US` or `CA`, otherwise "Only US and CA are supported".
5. Read and validate the rates file, otherwise "Rates are unavailable".
6. Calculate `amount * rate` and round half up to 2 decimals.
7. If the rounded result is 0.00, "Amount is too small to convert".
8. Write the log line, otherwise "Could not write the conversion log".
9. Print `<result> INR`.

The input is checked **before** the rates file is read, so `abc US` with a missing rates file shows
the amount error. Every error stops the run: nothing later happens, nothing is logged, and no
number is printed.

### Exactness

- The amount is converted with `Decimal(text)` and never passes through `float`.
- The calculator multiplies inside a local `decimal` context whose precision is large enough for the input length, so the multiplication is exact. Only the final `quantize(Decimal("0.01"), ROUND_HALF_UP)` rounds.
- The result is printed with `format(result, "f")`: no thousands separator and no exponent (`90000000.00`).
- Smallest US amount that still converts: 0.00006 (0.0054 rounds to 0.01). 0.00005 gives 0.0045, rounds to 0.00 and is rejected.

### Rates file

```yaml
rates:
  US: 90
  CA: 100
```

The reader looks for the file at `<repo root>/config/rates.yaml` (found from the package location, so
it works from any directory). Functions also accept an explicit path so tests can use fixtures.
It shows "Rates are unavailable" (exit 1, no number) when any of these is true (FR-018):

- the file is missing or unreadable
- the YAML is invalid, or there is no `rates` map
- the map does not contain exactly `US` and `CA` (a missing or an extra key)
- a rate is not a number greater than 0: text, `true`/`false`, null, zero, negative, or not finite
  (`.inf`, `.nan`)

Rates are read as YAML numbers and converted with `Decimal(str(value))`.

### Log line

`logs/conversions.log` is created (with its folder) on first use and appended to, one line per
successful conversion:

```text
2026-10-17T10:15:30+00:00 | 100 | US | 9000.00
```

Fields: UTC ISO timestamp to the second, amount as entered, upper-case country, result in INR,
separated by ` | `. Failed conversions (including "too small") are not logged. The line is written
**before** the result is printed; if writing fails, the CLI shows "Could not write the conversion
log" and exits non-zero without printing a result, so no unlogged conversion is ever shown (FR-019).

### Command line

See [contracts/cli.md](contracts/cli.md). Success prints `<result> INR` to stdout, exit code 0.
Errors print the exact message to stderr, exit code 1.

- **Amounts starting with "-" (FR-022)**: `main` hands argparse the arguments after a `--`
  separator (unless `-h` or `--help` is present), so the first argument is always the amount and
  `-5`, `-1e5`, `-abc` and `-1,000` reach the checker.
- **Wrong number of arguments (FR-021)**: argparse prints its usage message to stderr and exits with
  code 2; `main` returns that code. No number is shown.

## Test plan (every spec example is a named test)

Tests live in `tests/`. `tests/test_acceptance.py` drives `converter.cli.main(argv, ...)` with a
fixture rates file and a temporary log path. Unit tests cover each part.

### Convert (User Story 1)

| Spec example | Test name |
|--------------|-----------|
| US1-1: 100 US -> 9000.00 INR | `test_100_us_gives_9000_00` |
| US1-2: 100 CA -> 10000.00 INR | `test_100_ca_gives_10000_00` |
| US1-3: 2.50 US -> 225.00 INR | `test_2_50_us_gives_225_00` |
| US1-4: 100 us -> 9000.00 INR | `test_lowercase_country_accepted` |
| US1-5: 1000000 US -> 90000000.00 INR | `test_max_amount_us_no_thousands_separator` |
| US1-6: 1000000 CA -> 100000000.00 INR | `test_max_amount_ca_no_thousands_separator` |
| Edge: mixed case `Ca` | `test_mixed_case_country_accepted` |
| Edge: 2.505 (more than 2 decimals) -> 225.45 INR | `test_extra_decimals_converted_exactly` |
| Edge: 0.00006 US -> 0.01 INR (smallest that converts) | `test_smallest_convertible_amount_gives_0_01` |
| Clarification: half rounds up (0.135 -> 0.14) | `test_half_rounds_up` (calculator) |
| Calculator keeps exactness for long amounts | `test_exact_for_long_amounts` (calculator) |
| FR-011: rates come from the file | `test_rates_come_from_rates_file` (acceptance, changed fixture changes the result), `test_load_rates_returns_file_values` (unit) |

### Errors (User Story 2)

| Spec example | Test name |
|--------------|-----------|
| US2-1: 100 UK -> "Only US and CA are supported" | `test_unsupported_country_error` |
| US2-2: 0 US -> "Amount must be more than 0" | `test_zero_amount_error` |
| US2-3: -5 CA -> "Amount must be more than 0" | `test_negative_amount_error` |
| US2-4: abc US -> "Amount must be a number" | `test_non_numeric_amount_error` |
| US2-5: 1000001 US -> "Amount must be 1000000 or less" | `test_amount_over_maximum_error` |
| US2-6: 1,000 US -> "Amount must be a number" | `test_comma_amount_error` |
| US2-7: 1e5 US -> "Amount must be a number" | `test_scientific_notation_error` |
| US2-8: abc UK -> only the amount error | `test_amount_error_wins_over_country_error` |
| US2-9: .5 US -> "Amount must be a number" | `test_leading_dot_amount_error` |
| Edge: 5. US -> "Amount must be a number" | `test_trailing_dot_amount_error` |
| Edge: +5 US -> "Amount must be a number" | `test_plus_sign_amount_error` |
| US2-10: -1e5 US -> "Amount must be a number" | `test_dash_scientific_notation_is_amount_error` |
| US2-11: -abc US -> "Amount must be a number" | `test_dash_text_is_amount_error` |
| FR-022: -1,000 US -> "Amount must be a number" | `test_dash_comma_is_amount_error` |
| FR-022: -5 CA reaches the checker (not a CLI option) | `test_negative_amount_error` |
| US2-12: 0.00001 US -> "Amount is too small to convert" | `test_amount_too_small_error` |
| Edge: empty amount / empty country | `test_empty_amount_error`, `test_empty_country_error` |
| US2-13 / FR-018: rates file missing | `test_missing_rates_file_shows_error` |
| FR-018: rates file unreadable | `test_unreadable_rates_file_shows_error` |
| FR-018: invalid YAML | `test_invalid_yaml_rates_file_shows_error` |
| FR-018: rates file missing CA (or US) | `test_rates_file_missing_country_shows_error` |
| FR-018: rates file with an extra country | `test_rates_file_extra_country_shows_error` |
| FR-018: rate is zero | `test_zero_rate_shows_error` |
| FR-018: rate is negative | `test_negative_rate_shows_error` |
| FR-018: rate is text, true/false, null or not finite | `test_non_numeric_rate_shows_error` |
| FR-023: abc US with missing rates -> amount error | `test_amount_error_wins_over_missing_rates` |
| FR-018 rules at unit level | `test_rates_error_cases` (parametrised, in `test_rates.py`) |
| FR-021 / US2-14: one argument | `test_one_argument_shows_usage_exit_2` |
| FR-021: no arguments | `test_no_arguments_shows_usage_exit_2` |
| FR-021: three arguments | `test_extra_argument_shows_usage_exit_2` |
| FR-009: no number on any error | `test_no_inr_amount_in_any_error_output` |
| Checker rules and order at unit level | `test_checker_rejections`, `test_checker_accepts_max_amount`, `test_checker_amount_checked_before_country` (in `test_checker.py`) |

### Logging (User Story 3)

| Spec example | Test name |
|--------------|-----------|
| US3-1: log record for 100 US | `test_successful_conversion_is_logged` |
| Plan: log file and folder created on first use | `test_log_file_and_folder_created_on_first_use` |
| Clarification: errors are not logged | `test_failed_conversion_is_not_logged` |
| FR-020: too-small errors are not logged | `test_too_small_conversion_is_not_logged` |
| US3-2 / FR-019: log cannot be written | `test_log_write_failure_shows_error_and_no_result` |

### Constitution guards (`tests/test_constitution.py`)

| Rule | Test name |
|------|-----------|
| III: no `float` in code | `test_source_has_no_float` (tokenises `converter/*.py`; comments and strings are ignored) |
| V: no network imports | `test_source_has_no_network_imports` (parses imports; fails on `socket`, `urllib`, `http`, `requests`, `ftplib`, `smtplib`, `ssl`) |
| I: no hard-coded rate values | `test_source_has_no_hard_coded_rates` (reads the real `config/rates.yaml` and fails if any of its rate values appears as a number or string literal in `converter/*.py`) |

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
`-- tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
config/
`-- rates.yaml           # US: 90, CA: 100 (Product Owner approval to change)
converter/
|-- __init__.py
|-- __main__.py          # python -m converter
|-- cli.py               # argparse, order of steps, log line, output
|-- checker.py           # input checker, fixed US/CA list
|-- rates.py             # rate reader and validation
`-- calculator.py        # Decimal maths and rounding
tests/
|-- conftest.py          # fixtures: rates file factory, log path, run helper
|-- test_acceptance.py   # spec examples through cli.main
|-- test_arguments.py    # usage and leading-dash handling
|-- test_checker.py
|-- test_rates.py
|-- test_calculator.py
`-- test_constitution.py # guards: no float, no network, no hard-coded rates
logs/
`-- conversions.log      # created at runtime; git-ignored
requirements.txt         # PyYAML, pytest
```

**Structure Decision**: Single flat package `converter/` with one module per part. No sub-packages,
classes or abstractions beyond two small exceptions (`InputError`, `RatesError`).

## Complexity Tracking

No constitution violations; nothing to justify.
