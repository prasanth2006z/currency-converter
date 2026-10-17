---

description: "Task list for the Currency Converter (US/CA to INR)"
---

# Tasks: Currency Converter (US/CA to INR)

**Input**: Design documents from `/specs/001-currency-converter/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: REQUIRED. Constitution Principle VI: tests are written before the code they cover, must be seen to fail first, and every spec example becomes a named pytest test (names are listed in the plan.md test plan).

**Organization**: Tasks are grouped by user story. Within each story: write tests, run them and confirm they fail, then implement until they pass.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on unfinished tasks)
- **[Story]**: US1 = convert (P1), US2 = clear errors (P1), US3 = logging (P2)
- Run all commands from the repository root. Tests run with `python -m pytest`.

## Path Conventions

Single project at repository root: `converter/`, `tests/`, `config/`, `logs/` (see plan.md Project Structure).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton and the rates settings file

- [X] T001 Create the folders `converter/`, `tests/`, `config/` and a `requirements.txt` listing only `PyYAML` and `pytest` (constitution Principle VII)
- [X] T002 [P] Create `config/rates.yaml` containing exactly a `rates:` map with `US: 90` and `CA: 100` and nothing else, plus a comment that any change needs recorded Product Owner approval (Principles I and II)
- [X] T003 [P] Add `logs/` to `.gitignore` so the runtime log is not committed
- [X] T004 [P] Create `converter/__init__.py` (empty) and `converter/__main__.py` that calls `converter.cli.main()` and exits with its return code, so `python -m converter 100 US` works

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared test fixtures, the constitution guard tests, and the empty shells every story fills in

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create `tests/conftest.py` with fixtures: `make_rates_file(yaml_text)` (a factory that writes any YAML text to a temporary file and returns its path), `rates_file` (built with the factory: `US: 90`, `CA: 100`), `log_path` (a temporary path whose folder does not exist yet) and a `run_cli(argv)` helper that calls `converter.cli.main(argv, rates_path=..., log_path=...)` and returns the exit code, captured stdout and captured stderr
- [X] T006 [P] Create `tests/test_constitution.py` with three guard tests over every `.py` file in `converter/`: `test_source_has_no_float` (use `tokenize` and fail on a NAME token `float`, so comments and strings are ignored; Principle III), `test_source_has_no_network_imports` (use `ast` and fail on an import of `socket`, `urllib`, `http`, `requests`, `ftplib`, `smtplib` or `ssl`; Principle V) and `test_source_has_no_hard_coded_rates` (read the real `config/rates.yaml` and fail if any of its rate values appears as a number or string literal in `converter/`; Principle I)
- [X] T007 [P] Create `converter/cli.py` with `main(argv=None, rates_path=None, log_path=None) -> int`: an argparse parser with two positional text arguments `amount` and `country` (no `type=float`); default paths are `config/rates.yaml` and `logs/conversions.log` found relative to the repository root, not the current directory; the body is a placeholder returning 1
- [X] T008 [P] Create `converter/checker.py` containing `class InputError(Exception)` (its message is the user-facing error) and the fixed constant `SUPPORTED_COUNTRIES = ("US", "CA")` (spec FR-002)

**Checkpoint**: Foundation ready - user story work can begin

---

## Phase 3: User Story 1 - Convert a dollar amount to INR (Priority: P1) MVP

**Goal**: `python -m converter 100 US` prints `9000.00 INR`; country code works in any letter case; results have exactly 2 decimals and no thousands separator.

**Independent Test**: Run the valid examples and compare stdout exactly; `python -m pytest tests/test_calculator.py tests/test_rates.py tests/test_acceptance.py` passes.

### Tests for User Story 1 (write FIRST, confirm they FAIL)

- [X] T009 [P] [US1] Create `tests/test_calculator.py` with `test_half_rounds_up` (amount 0.0015 at rate 90 gives `0.14`, exact result 0.135) and `test_exact_for_long_amounts` (an amount with 30 decimal digits is multiplied without early rounding), both on `converter.calculator.convert(amount: Decimal, rate: Decimal) -> Decimal`
- [X] T010 [P] [US1] Create `tests/test_rates.py` with `test_load_rates_returns_file_values` (`converter.rates.load_rates(path)` on the fixture file returns `{"US": Decimal("90"), "CA": Decimal("100")}`, and a file written with the factory using other values returns those values)
- [X] T011 [P] [US1] Create `tests/test_acceptance.py` (through `cli.main` with fixtures) with: `test_100_us_gives_9000_00`, `test_100_ca_gives_10000_00`, `test_2_50_us_gives_225_00`, `test_lowercase_country_accepted`, `test_mixed_case_country_accepted` (`Ca`), `test_max_amount_us_no_thousands_separator` (1000000 US prints `90000000.00 INR`), `test_max_amount_ca_no_thousands_separator` (1000000 CA prints `100000000.00 INR`), `test_extra_decimals_converted_exactly` (2.505 US prints `225.45 INR`), `test_smallest_convertible_amount_gives_0_01` (0.00006 US prints `0.01 INR`), `test_rates_come_from_rates_file` (a fixture built with US 80 changes `100 US` to `8000.00 INR`); each asserts exit code 0 and stdout is exactly `<result> INR` plus newline
- [X] T012 [US1] Run `python -m pytest` and confirm the new US1 tests FAIL (the guard tests from T006 pass because `converter/` has no violations yet)

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement `converter/calculator.py` `convert(amount, rate)`: multiply inside `decimal.localcontext()` with precision large enough that the product is exact for the input length, then `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`; no `float` anywhere (Principle III)
- [X] T014 [P] [US1] Implement the happy path of `converter/rates.py` `load_rates(path=None) -> dict[str, Decimal]`: read the YAML with `yaml.safe_load`, take the top-level `rates` map, convert each value with `Decimal(str(value))`; the default path is `config/rates.yaml` at the repository root (validation comes in US2)
- [X] T015 [P] [US1] Implement the happy path of `converter/checker.py` `check_input(amount_text, country_text)`: turn a valid amount text into a `Decimal` and return it with the country code in upper case (the rejection rules come in US2)
- [X] T016 [US1] Implement the happy path of `converter/cli.py` `main`, in this order: run the checker on the input FIRST, then load the rates, then convert, then print `format(result, "f")` followed by ` INR` to stdout and return 0 (depends on T013, T014, T015)
- [X] T017 [US1] Run `python -m pytest tests/test_calculator.py tests/test_rates.py tests/test_acceptance.py tests/test_constitution.py` and confirm all PASS

**Checkpoint**: User Story 1 works on its own (no checks or logging yet)

---

## Phase 4: User Story 2 - Clear errors for invalid input (Priority: P1)

**Goal**: Every invalid input prints the exact spec message to stderr, exits with code 1, and prints no INR amount. Also covers rates-file errors, "too small" results, leading-dash amounts and wrong argument counts.

**Independent Test**: Run the invalid examples and compare stderr exactly; stdout is empty each time.

### Tests for User Story 2 (write FIRST, confirm they FAIL)

- [X] T018 [P] [US2] Create `tests/test_checker.py` with `test_checker_rejections` (parametrised; `check_input` raises `InputError` with these exact messages: `abc`, `1,000`, `1e5`, `.5`, `5.`, `+5`, empty text, `nan`, `inf`, `-1e5`, `-abc`, `-1,000` -> "Amount must be a number"; `0` and `-5` -> "Amount must be more than 0"; `1000001` -> "Amount must be 1000000 or less"; country `UK` and empty country -> "Only US and CA are supported"), `test_checker_accepts_max_amount` (1000000 is accepted) and `test_checker_amount_checked_before_country` (`abc` with country `UK` raises the amount error)
- [X] T019 [P] [US2] Add to `tests/test_acceptance.py`, each asserting exit code 1, empty stdout and stderr equal to the exact message: `test_unsupported_country_error`, `test_zero_amount_error`, `test_negative_amount_error` (`-5 CA`), `test_non_numeric_amount_error`, `test_amount_over_maximum_error`, `test_comma_amount_error`, `test_scientific_notation_error`, `test_leading_dot_amount_error`, `test_trailing_dot_amount_error`, `test_plus_sign_amount_error`, `test_empty_amount_error`, `test_empty_country_error`, `test_amount_error_wins_over_country_error` (`abc UK`), `test_dash_scientific_notation_is_amount_error` (`-1e5 US`), `test_dash_text_is_amount_error` (`-abc US`), `test_dash_comma_is_amount_error` (`-1,000 US`), `test_amount_too_small_error` (`0.00001 US` -> "Amount is too small to convert"), `test_amount_error_wins_over_missing_rates` (`abc US` with a missing rates file -> "Amount must be a number"); and the "Rates are unavailable" tests: `test_missing_rates_file_shows_error`, `test_unreadable_rates_file_shows_error` (rates path is a folder), `test_invalid_yaml_rates_file_shows_error`, `test_rates_file_missing_country_shows_error` (no `CA`), `test_rates_file_extra_country_shows_error` (an added `UK: 50`), `test_zero_rate_shows_error`, `test_negative_rate_shows_error`, `test_non_numeric_rate_shows_error` (text, `true`, empty value and `.inf`); and `test_no_inr_amount_in_any_error_output` asserting that for every invalid example above stdout is empty and no output contains `INR`
- [X] T020 [P] [US2] Create `tests/test_arguments.py` with `test_no_arguments_shows_usage_exit_2`, `test_one_argument_shows_usage_exit_2`, `test_extra_argument_shows_usage_exit_2`; each asserts exit code 2, empty stdout, a usage message on stderr and no log file written
- [X] T021 [P] [US2] Add to `tests/test_rates.py` `test_rates_error_cases` (parametrised: `load_rates` raises `RatesError` for a missing file, an unreadable file, invalid YAML, no `rates` map, a missing `US`, a missing `CA`, an extra country, a rate of 0, a negative rate, a text rate, a `true` rate, an empty rate, and `.inf`/`.nan` rates)
- [X] T022 [US2] Run `python -m pytest` and confirm the new US2 tests FAIL

### Implementation for User Story 2

- [X] T023 [P] [US2] Implement the rejection rules in `converter/checker.py` in this exact order: (1) amount text must match `^-?\d+(\.\d+)?$` else `InputError("Amount must be a number")`; (2) amount more than 0 else `InputError("Amount must be more than 0")`; (3) amount 1000000 or less else `InputError("Amount must be 1000000 or less")`; (4) upper-cased country must be in `SUPPORTED_COUNTRIES` else `InputError("Only US and CA are supported")`
- [X] T024 [P] [US2] In `converter/rates.py` add `class RatesError(Exception)` and make `load_rates` raise it when: the file is missing or unreadable; the YAML is invalid or has no `rates` map; the map does not contain exactly the keys `US` and `CA`; or any rate is not a YAML number greater than 0 (reject text, booleans, null, zero, negatives and non-finite values; check booleans before numbers because `True` is an `int` in Python)
- [X] T025 [US2] In `converter/cli.py` (depends on T016, T023, T024): (a) pass the arguments to argparse after a `--` separator unless `-h` or `--help` is present, so an amount starting with "-" is always the amount; (b) catch the argparse `SystemExit` and return its exit code (2 for wrong argument counts, 0 for help); (c) catch `InputError` and `RatesError`, print only the message to stderr (`Rates are unavailable` for `RatesError`), print nothing to stdout and return 1; (d) after converting, if the result is 0.00 raise the error "Amount is too small to convert" the same way; (e) keep the order: check input, load rates, convert, too-small check
- [X] T026 [US2] Run `python -m pytest` and confirm all US1 and US2 tests PASS

**Checkpoint**: User Stories 1 and 2 both work; invalid input never shows a number

---

## Phase 5: User Story 3 - Conversions are recorded (Priority: P2)

**Goal**: Each successful conversion appends one line to `logs/conversions.log`; failed conversions (including "too small") are never logged; a result is never shown if its log line could not be written (FR-019).

**Independent Test**: Run `100 US`, then read the log file and see one line `<UTC ISO timestamp> | 100 | US | 9000.00`.

### Tests for User Story 3 (write FIRST, confirm they FAIL)

- [X] T027 [US3] Add to `tests/test_acceptance.py`: `test_successful_conversion_is_logged` (after `2.50 us` the log has exactly one line with four fields separated by ` | `: an ISO timestamp, `2.50`, `US`, `225.00`); `test_log_file_and_folder_created_on_first_use` (the log folder does not exist before the run); `test_failed_conversion_is_not_logged` (after `100 UK` the log file does not exist); `test_too_small_conversion_is_not_logged` (after `0.00001 US` the log file does not exist); `test_log_write_failure_shows_error_and_no_result` (log path is inside a file or a read-only location: stderr is "Could not write the conversion log", exit code 1, empty stdout)
- [X] T028 [US3] Run `python -m pytest` and confirm the new US3 tests FAIL
- [X] T029 [US3] In `converter/cli.py` write the log line after the too-small check and before printing the result: UTC time as ISO 8601 to the second (`datetime.now(timezone.utc).isoformat(timespec="seconds")`), the amount text as entered, the country in upper case, the result with 2 decimals, joined by ` | `; create the log folder if missing and append; on `OSError` print "Could not write the conversion log" to stderr, return 1, and print no result; never log failed conversions
- [X] T030 [US3] Run `python -m pytest` and confirm ALL tests PASS

**Checkpoint**: All three user stories work independently

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T031 Run the full suite `python -m pytest` from a clean checkout and confirm everything passes
- [X] T032 Prove the three guard tests in `tests/test_constitution.py` can fail: temporarily add `float(1)`, `import socket` and the literal `90` to files in `converter/`, confirm each guard test fails, then remove the three lines and confirm the suite passes again
- [X] T033 Run every command in `specs/001-currency-converter/quickstart.md` by hand and confirm the outputs match, and that `logs/conversions.log` has one line per success and none for errors
- [X] T034 Check that every named test in the plan.md test plan exists in `tests/` and that every example in spec.md (acceptance scenarios and edge cases) has one; add any missing test and its fix
- [X] T035 Constitution review: confirm `config/rates.yaml` holds exactly US and CA, that nothing beyond PyYAML and pytest is in `requirements.txt`, and note in the change description that `config/rates.yaml` was created with Product Owner approval of the rates (Principle II is a process check; the other principles are enforced by the guard tests)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: needs Phase 1; blocks all stories
- **US1 (Phase 3)**: needs Phase 2; no dependency on other stories
- **US2 (Phase 4)**: needs Phase 2 and the US1 `cli.py` happy path (T016), because US2 adds the rejection rules to the same `checker.py`, `rates.py` and `cli.py`
- **US3 (Phase 5)**: needs US1 (T016) and US2 (T025), because logging sits in `cli.py` between the too-small check and the output
- **Polish (Phase 6)**: needs all stories

### Within Each Story

- Tests first, run, see them fail, then implement, then run until green (Principle VI)
- Inside `cli.py`: T007 -> T016 -> T025 -> T029 (same file, strictly in order)

### Parallel Opportunities

- Phase 1: T002, T003, T004
- Phase 2: T005, T006, T007, T008
- US1 tests: T009, T010, T011; US1 code: T013, T014, T015
- US2 tests: T018, T019, T020, T021; US2 code: T023, T024
- US3 has no parallel tasks (all edits are in two shared files)

---

## Parallel Example: User Story 1

```text
# Write the three test files together:
Task: "T009 tests/test_calculator.py"
Task: "T010 tests/test_rates.py"
Task: "T011 tests/test_acceptance.py"

# After the tests fail, write the three small modules together:
Task: "T013 converter/calculator.py"
Task: "T014 converter/rates.py"
Task: "T015 converter/checker.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup, Phase 2 Foundational
2. Phase 3 User Story 1
3. STOP and validate the valid examples. Note: US1 alone does not yet meet Principles IV and VIII, so it is a demo, not a release; US2 and US3 are required before the converter is considered done.

### Incremental Delivery

1. Setup + Foundational
2. US1 -> convert works
3. US2 -> errors are safe (both P1 stories together are the minimum usable product)
4. US3 -> logging complete
5. Polish -> full suite, guard-test proof, quickstart, constitution review

---

## Notes

- [P] tasks = different files, no dependencies
- Each test run before implementation must show failures; fix code, never weaken a test
- Error messages are exact; copy them from spec.md and contracts/cli.md
- Commit after each task or logical group

---

## Phase 7: Convergence

**Purpose**: Remaining work found by `/speckit-converge` on 2026-10-17. Complete with `/speckit-implement`.

- [X] T036 Reconcile `-h` and `--help` with FR-022: add `test_help_option_shows_usage_exit_0` to `tests/test_arguments.py` (covers `-h`, `--help`, `-h US` and `100 --help`: usage on stdout, exit code 0, no result, no log line), and state the exception in `spec.md` FR-022 ("`-h` and `--help` show usage and exit with code 0; every other argument starting with `-` is the amount") so spec, plan and `contracts/cli.md` agree per FR-022 (partial) NOTE: FR-022 in spec.md was already updated by the Product Owner decision; the test was added and passes against the existing code.
- [X] T037 Record Product Owner approval of `config/rates.yaml` (US 90, CA 100) in the commit message or change description that introduces the file, as T035 requires; no such record exists yet because the code is uncommitted, and Constitution II demands recorded approval before merge per Constitution II (partial) NOTE: the Product Owner will record the approval personally in the commit that adds `config/rates.yaml`; no git commit is made by Spec Kit tooling.
- [X] T038 Add `test_leading_zeros_amount_accepted` to `tests/test_acceptance.py`: `00005 US` prints `450.00 INR`, `007.5 CA` prints `750.00 INR`, `000 US` gives the error "Amount must be more than 0"; leading zeros are accepted per the spec edge case and Product Owner decision (partial)
