# Feature Specification: Currency Converter (US/CA to INR)

**Feature Branch**: `001-currency-converter`

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "Build a currency converter that turns an amount in US dollars or Canadian dollars into Indian Rupees (INR). The user gives an amount and a country code. Only US (1 dollar = 90 INR) and CA (1 dollar = 100 INR) are supported. The result is shown in INR with 2 decimal places. Country codes are accepted in small or capital letters. If the input is wrong, the user sees a clear error and never a wrong number. Not included: other countries, live or changing rates, converting from INR to other currencies."

## Clarifications

### Session 2026-10-17

- Q: When the exact INR value falls exactly halfway between two cents, which way does it round? → A: Round half up (0.135 → 0.14, 0.125 → 0.13)
- Q: Should an amount with more than 2 decimal places be accepted or rejected? → A: Accepted and converted exactly; only the final result is rounded
- Q: If both amount and country are wrong, which error is shown? → A: The amount error, checked first
- Q: Where is the conversion log kept? → A: A log file saved on disk, one line per conversion
- Q: Are failed conversions logged? → A: No, only successful conversions are logged
- Q (Product Owner): Are results shown with a thousands separator? → A: No, results have no thousands separator (9000.00, not 9,000.00)
- Q (Product Owner): Is there a maximum amount, and how are commas or scientific notation treated? → A: Maximum amount is 1000000; larger amounts show "Amount must be 1000000 or less". Amounts with commas (1,000) or scientific notation (1e5) show "Amount must be a number"
- Q (Product Owner): How are amounts like .5, 5. and +5 treated? → A: Rejected with "Amount must be a number"
- Q (Product Owner): What happens if the rates file is missing or unreadable? → A: The error "Rates are unavailable" is shown and no result
- Q (Product Owner): What happens if the conversion log cannot be written? → A: The error "Could not write the conversion log" is shown and no result
- Q (Product Owner): Who decides which countries are supported, the spec or the rates file? → A: The spec: supported countries are fixed to US and CA. The rates file must contain exactly US and CA; a missing or extra country gives "Rates are unavailable"
- Q (Product Owner): What happens if the converted result rounds to 0.00? → A: The error "Amount is too small to convert" is shown and no result (for example 0.00001 US)
- Q (Product Owner): Which rates-file problems give "Rates are unavailable"? → A: A missing or unreadable file, invalid YAML, a missing or extra country, or any rate that is not a number greater than 0
- Q (Solution Architect): How are wrong command-line arguments and amounts starting with "-" handled? → A: The wrong number of arguments shows usage and exits with code 2 and no result. A first argument starting with "-" is always the amount, never a command-line option
- Q (Product Owner): Is there an exception to "an amount starting with - is always the amount"? → A: Yes, only `-h` and `--help`, which show usage and exit with code 0
- Q (Product Owner): Are amounts with leading zeros such as 00005 accepted? → A: Yes, they mean the same number (00005 US gives 450.00 INR)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert a dollar amount to INR (Priority: P1)

A user enters an amount and a country code (US or CA) and receives the equivalent amount in Indian Rupees, shown with exactly 2 decimal places. Country codes work in small or capital letters.

**Why this priority**: This is the whole purpose of the converter; without it there is no product.

**Independent Test**: Enter each valid example (amount + country code) and compare the displayed result to the expected INR value exactly.

**Acceptance Scenarios**:

1. **Given** the user enters amount 100 and country US, **When** they convert, **Then** they see `9000.00 INR`
2. **Given** the user enters amount 100 and country CA, **When** they convert, **Then** they see `10000.00 INR`
3. **Given** the user enters amount 2.50 and country US, **When** they convert, **Then** they see `225.00 INR`
4. **Given** the user enters amount 100 and country `us` (small letters), **When** they convert, **Then** they see `9000.00 INR`
5. **Given** the user enters amount 1000000 (the maximum) and country US, **When** they convert, **Then** they see `90000000.00 INR` with no thousands separator
6. **Given** the user enters amount 1000000 (the maximum) and country CA, **When** they convert, **Then** they see `100000000.00 INR` with no thousands separator

---

### User Story 2 - Clear errors for invalid input (Priority: P1)

When the country or amount is invalid, the user sees a clear error message and never a number that could be mistaken for a result.

**Why this priority**: Showing a wrong number is worse than showing nothing; this is a non-negotiable rule of the project.

**Independent Test**: Enter each invalid example and confirm the exact error message is shown and no INR amount is shown.

**Acceptance Scenarios**:

1. **Given** the user enters amount 100 and country UK, **When** they convert, **Then** they see the error "Only US and CA are supported"
2. **Given** the user enters amount 0 and country US, **When** they convert, **Then** they see the error "Amount must be more than 0"
3. **Given** the user enters amount -5 and country CA, **When** they convert, **Then** they see the error "Amount must be more than 0"
4. **Given** the user enters amount `abc` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
5. **Given** the user enters amount 1000001 and country US, **When** they convert, **Then** they see the error "Amount must be 1000000 or less"
6. **Given** the user enters amount `1,000` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
7. **Given** the user enters amount `1e5` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
8. **Given** the user enters amount `abc` and country UK, **When** they convert, **Then** they see only the error "Amount must be a number"
9. **Given** the user enters amount `.5` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
10. **Given** the user enters amount `-1e5` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
11. **Given** the user enters amount `-abc` and country US, **When** they convert, **Then** they see the error "Amount must be a number"
12. **Given** the user enters amount `0.00001` and country US, **When** they convert, **Then** they see the error "Amount is too small to convert"
13. **Given** the rates file is missing, **When** the user converts 100 US, **Then** they see the error "Rates are unavailable"
14. **Given** the user enters only one argument, **When** they run the program, **Then** they see a usage message, the program exits with code 2 and no result is shown

---

### User Story 3 - Conversions are recorded (Priority: P2)

Each successful conversion is recorded with the amount, country, result and time, so there is a history of what the converter produced.

**Why this priority**: It supports auditing but does not change what the user sees.

**Independent Test**: Perform a valid conversion, then check the record contains the amount, country, result and time.

**Acceptance Scenarios**:

1. **Given** the user converts 100 US successfully, **When** the conversion completes, **Then** a record exists with amount 100, country US, result 9000.00 and the time of conversion
2. **Given** the conversion log cannot be written, **When** the user converts 100 US, **Then** they see the error "Could not write the conversion log" and no result

---

### Edge Cases

- A country code in mixed case (e.g. `Ca`) is treated the same as `CA`.
- A very small amount whose result rounds to 0.00 INR (e.g. `0.00001 US`) is rejected with "Amount is too small to convert" and no result. The smallest US amount that still converts is 0.00006 (gives `0.01 INR`).
- An amount with more than 2 decimal places (e.g. 2.505) is converted exactly and the result rounded to 2 decimal places.
- An empty amount or empty country code shows the matching error (amount: "Amount must be a number"; country: "Only US and CA are supported").
- An amount written as `.5`, `5.` or `+5` is rejected with "Amount must be a number" and no result.
- If the rates file is missing, unreadable or invalid YAML, does not contain exactly US and CA, or has a rate that is not a number greater than 0, the user sees the error "Rates are unavailable" and no result.
- An amount starting with "-" is always treated as the amount: `-5` gives "Amount must be more than 0"; `-1e5`, `-abc` and `-1,000` give "Amount must be a number". The only exception is `-h` and `--help`, which show the usage help, exit with code 0 and show no result.
- Leading zeros are accepted and mean the same number: `00005 US` gives `450.00 INR` and `007.5 CA` gives `750.00 INR`. `000 US` gives "Amount must be more than 0".
- With the wrong number of arguments (none, only one, or more than two) the user sees a usage message, the program exits with code 2, and no result is shown.
- The amount is checked before the rates file is read, so `abc US` shows "Amount must be a number" even when the rates file is missing.
- If the conversion log cannot be written, the user sees the error "Could not write the conversion log" and no result (a result is never shown without its log record).
- When both amount and country are invalid, the amount is checked first, so the user sees only the amount error (e.g. `abc UK` shows "Amount must be a number") and no result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to provide an amount and a country code and receive the equivalent amount in INR.
- **FR-002**: The system MUST support only two countries, fixed by this specification: US (1 dollar = 90 INR) and CA (1 dollar = 100 INR). The rates file does not add or remove supported countries.
- **FR-003**: The system MUST accept country codes in small or capital letters.
- **FR-004**: The result MUST be shown in INR with exactly 2 decimal places, in the form `<result> INR`.
- **FR-005**: Calculations MUST be exact (no rounding drift); only the final result is rounded to 2 decimal places, with exact halves rounded up (e.g. 0.135 becomes 0.14).
- **FR-006**: For an unsupported country code, the system MUST show the error "Only US and CA are supported" and no result.
- **FR-007**: For an amount of zero or less, the system MUST show the error "Amount must be more than 0" and no result.
- **FR-008**: For an amount that is not a number, the system MUST show the error "Amount must be a number" and no result.
- **FR-009**: The system MUST never show an INR amount when the input is invalid.
- **FR-010**: Every successful conversion MUST be recorded in a log file saved on disk, one line per conversion, with the amount, country, result and time. Failed conversions (errors) MUST NOT be logged.
- **FR-011**: The conversion rates MUST be kept in one settings file, not inside the program logic, and changes to it require Product Owner approval.
- **FR-012**: The system MUST work fully offline, with no calls to the internet or external services.
- **FR-013**: Every example in this specification MUST be covered by an automated test.
- **FR-014**: The system MUST show results with no thousands separator (e.g. `9000.00 INR`, not `9,000.00 INR`).
- **FR-015**: The maximum accepted amount is 1000000 (inclusive). For a larger amount, the system MUST show the error "Amount must be 1000000 or less" and no result.
- **FR-016**: An amount containing commas (e.g. `1,000`) or scientific notation (e.g. `1e5`) MUST be treated as not a number and show the error "Amount must be a number".
- **FR-017**: An amount written as `.5`, `5.` or `+5` MUST be treated as not a number and show the error "Amount must be a number".
- **FR-018**: If the rates file is missing, unreadable or invalid YAML, does not contain exactly US and CA (a missing or extra country), or has any rate that is not a number greater than 0, the system MUST show the error "Rates are unavailable" and no result.
- **FR-019**: If the conversion log cannot be written, the system MUST show the error "Could not write the conversion log" and no result.
- **FR-020**: If the converted result rounds to 0.00 (e.g. `0.00001 US`), the system MUST show the error "Amount is too small to convert" and no result, and MUST NOT log it.
- **FR-021**: With the wrong number of command-line arguments, the system MUST show a usage message, exit with code 2 and show no result.
- **FR-022**: An amount starting with "-" MUST always be treated as the amount, never as a command-line option (e.g. `-5`, `-1e5`, `-abc`, `-1,000`). The one exception is `-h` and `--help`, which show the usage help and exit with code 0, with no result and no log record.
- **FR-023**: The system MUST check the amount first, then the country, then read the rates file, then calculate.

### Key Entities

- **Conversion Request**: The amount and country code entered by the user.
- **Rate**: The INR value of one dollar for a supported country (US = 90, CA = 100).
- **Conversion Result**: The INR amount, rounded to 2 decimal places, or an error message.
- **Conversion Record**: A logged entry holding amount, country, result and time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 6 valid examples (100 US, 100 CA, 2.50 US, 100 us, and the maximum 1000000 for US and CA) produce exactly the stated results.
- **SC-002**: Every invalid example in this specification (all of User Story 2's scenarios and the edge cases) produces exactly the stated error message, and 100% of invalid inputs show no INR amount.
- **SC-003**: A user gets a result or error immediately (no noticeable wait) for any input.
- **SC-004**: 100% of successful conversions have a matching record with amount, country, result and time.
- **SC-005**: Every example in this specification has a passing automated test.

## Assumptions

- The user supplies an amount and country code via a simple command-line style entry; no web or mobile interface is in scope.
- Amounts are in dollars (US or Canadian) and are plain decimal numbers up to 1000000; currency symbols, thousands separators (commas), scientific notation and shortcut forms such as `.5`, `5.` and `+5` are not supported.
- Rates are fixed (US = 90, CA = 100) and only change through an approved edit to the settings file. The file holds exactly the two supported countries.
- Out of scope: other countries, live or changing rates, and converting from INR to other currencies.
- Purpose: a small proof of concept for practising spec-driven development before a larger project.
