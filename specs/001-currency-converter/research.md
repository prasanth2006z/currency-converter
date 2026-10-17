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

## 2. Negative numbers on the command line

- **Decision**: Use plain positional arguments (`amount`, `country`) with argparse.
- **Rationale**: argparse treats `-5` as a negative number, not an option, when the parser defines no
  options that look like numbers, so `python -m converter -5 CA` reaches the checker and shows
  "Amount must be more than 0".
- **Alternatives considered**: `--amount` flags (changes the command the architect specified).

## 3. Exact multiplication

- **Decision**: Multiply inside a local `decimal` context with precision sized to the input, then
  `quantize(Decimal("0.01"), ROUND_HALF_UP)`.
- **Rationale**: The default 28-digit context could round a very long amount during multiplication
  before the final rounding. Rates are whole numbers, so the product has at most as many decimals
  as the amount and an adequate precision makes it exact.
- **Alternatives considered**: limiting the number of digits (a new rule not in the spec).

## 4. Rates file location and format

- **Decision**: `config/rates.yaml` with a top-level `rates:` map; located from the package path;
  values converted with `Decimal(str(value))`. Supported countries are the keys of that map.
- **Rationale**: One file, no rate numbers in code (Principle I). Using the keys as the supported list
  means adding a country later is a data change, though the spec keeps scope at US and CA.
- **Alternatives considered**: current working directory lookup (breaks when run from elsewhere).

## 5. Failure when rates or log are unavailable

- **Decision**: Missing/invalid rates file shows "Rates are unavailable"; failure to write the log shows
  "Could not write the conversion log". Both exit non-zero with no result.
- **Rationale**: Principle VIII (never a wrong number) and Principle IV (every shown conversion is
  logged). Accepted by the Product Owner and now in the spec (FR-018, FR-019).
- **Alternatives considered**: showing the result anyway when the log fails (would break Principle IV).

## 6. Log timestamp

- **Decision**: UTC ISO 8601 to the second, e.g. `2026-10-17T10:15:30+00:00`.
- **Rationale**: Unambiguous and sortable; standard library only.
