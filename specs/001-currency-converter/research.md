# Research: Currency Converter

The Technical Context had no unresolved unknowns: the Solution Architect fixed the stack, layout
and log format. This file records the small decisions that were still open.

## 1. Amount text check

- **Decision**: Accept only text matching `^-?\d+(\.\d+)?$`, then `Decimal(text)`.
- **Rationale**: `Decimal()` alone also accepts `1e5`, `NaN`, `Infinity` and padded spaces, which the
  spec says must be "Amount must be a number". A strict pattern gives exactly the spec's rules and
  keeps the amount out of `float`.
- **Alternatives considered**: `try Decimal(text)` with extra rejects (easy to miss a case);
  `float()` (forbidden by the constitution).
- **Consequence**: `.5`, `5.` and `+5` are rejected as "not a number". The spec does not mention
  them; the Product Owner accepted this (spec FR-017).

## 2. Amounts starting with "-" on the command line

- **Decision**: Use plain positional arguments (`amount`, `country`) with argparse, and pass them
  after a `--` separator (unless `-h` or `--help` is present) so the first argument is always the amount.
- **Rationale**: argparse only treats values such as `-5` or `-.5` as numbers. Anything else that
  starts with "-" (`-1e5`, `-abc`, `-1,000`) would be read as an unknown option and give a usage error
  instead of "Amount must be a number". After `--` every argument is positional (spec FR-022).
- **Alternatives considered**: `--amount` flags (changes the command the architect specified);
  `parse_known_args` (hides genuine usage mistakes).

## 3. Exact multiplication

- **Decision**: Multiply inside a local `decimal` context with precision sized to the input, then
  `quantize(Decimal("0.01"), ROUND_HALF_UP)`.
- **Rationale**: The default 28-digit context could round a very long amount during multiplication
  before the final rounding. Rates are whole numbers, so the product has at most as many decimals
  as the amount and an adequate precision makes it exact.
- **Alternatives considered**: limiting the number of digits (a new rule not in the spec).

## 4. Rates file location and format

- **Decision**: `config/rates.yaml` with a top-level `rates:` map; located from the package path;
  values converted with `Decimal(str(value))`. The file must contain exactly `US` and `CA`, each a
  finite number greater than 0. The supported countries are fixed in the checker, not read from the file.
- **Rationale**: One file, no rate numbers in code (Principle I). Fixing the countries follows the spec
  (FR-002), so editing the file cannot add a country. Validating every rate means a bad value cannot
  produce a wrong number (Principle VIII).
- **Alternatives considered**: using the file's keys as the supported list (lets a file edit change
  scope); current working directory lookup (breaks when run from elsewhere).

## 5. Failure when rates or log are unavailable

- **Decision**: Missing/invalid rates file shows "Rates are unavailable"; failure to write the log shows
  "Could not write the conversion log". Both exit non-zero with no result.
- **Rationale**: Principle VIII (never a wrong number) and Principle IV (every shown conversion is
  logged). Accepted by the Product Owner and now in the spec (FR-018, FR-019).
- **Alternatives considered**: showing the result anyway when the log fails (would break Principle IV).

## 6. Log timestamp

- **Decision**: UTC ISO 8601 to the second, e.g. `2026-10-17T10:15:30+00:00`.
- **Rationale**: Unambiguous and sortable; standard library only.

## 7. Order of steps

- **Decision**: Amount, then country, then read the rates file, then calculate, then check for 0.00,
  then log, then print (spec FR-023).
- **Rationale**: The amount error must win over the country error and over a missing rates file; the
  log is written last so only successful conversions are logged and a shown result always has a record.
- **Alternatives considered**: loading rates first (a missing file would hide input errors).

## 8. Results that round to 0.00

- **Decision**: Reject with "Amount is too small to convert" (Product Owner decision, spec FR-020).
- **Rationale**: Amounts with more than 2 decimals are accepted, so a tiny amount such as 0.00001 US
  would otherwise show `0.00 INR`, which looks like a result but is not useful. The smallest US amount
  that converts is 0.00006.
- **Alternatives considered**: a minimum amount rule (a new threshold not in the spec); showing 0.00 INR.

## 9. Automated constitution guards

- **Decision**: `tests/test_constitution.py` uses `tokenize`/`ast` to check `converter/*.py` for `float`,
  network imports and hard-coded rate values (read from the real `config/rates.yaml`).
- **Rationale**: Principles I, III and V become enforced by the test run instead of a manual grep.
  Tokenising ignores comments and strings for the `float` check, so a comment cannot cause a false failure.
- **Alternatives considered**: a manual grep task (not repeatable); a linter plugin (new dependency).
