<!--
Sync Impact Report (temporary; remove before commit)
- Version change: (template, unversioned) -> 1.0.0
- Modified principles: none (initial adoption)
- Added principles: I. Rates in One Settings File; II. Product Owner Approves Rate Changes;
  III. Exact Decimal Money; IV. Every Conversion Is Logged; V. Fully Offline;
  VI. Test-First (NON-NEGOTIABLE); VII. Keep It Simple; VIII. Invalid Input Fails Loudly
- Added sections: Technology Constraints; Development Workflow & Quality Gates
- Removed sections: none
- Deferred TODOs: none
-->
# Currency Converter Constitution

This is a small proof-of-concept currency converter used to practise spec-driven development.
The principles below are set by the Enterprise Architect and are non-negotiable.

## Core Principles

### I. Rates in One Settings File
All exchange rates MUST live in `config/rates.yaml` and nowhere else. Rates MUST NOT be written,
hard-coded or duplicated inside source code (tests MAY use fixture rate files).
Rationale: a single source of truth makes rates auditable and changeable without touching code.

### II. Product Owner Approves Rate Changes
Only the Product Owner MAY approve a change to `config/rates.yaml`. Any change to that file MUST
carry recorded Product Owner approval before it is merged.
Rationale: rates are a business decision, not an engineering one.

### III. Exact Decimal Money
All money arithmetic MUST use Python `Decimal`. `float` MUST NOT be used for amounts or rates,
including parsing and intermediate values. Results MUST be rounded to 2 decimal places.
Rationale: binary floating point produces incorrect currency values.

### IV. Every Conversion Is Logged
Every successful conversion MUST be logged with the amount, the country, the result and the
time of conversion.
Rationale: logging provides an audit trail of what the converter produced.

### V. Fully Offline
The program MUST run fully offline. It MUST NOT make internet calls or call any external
service.
Rationale: predictable, reproducible results with no external dependencies or data exposure.

### VI. Test-First (NON-NEGOTIABLE)
Tests MUST be written before the code they cover, and MUST be seen to fail before implementation
begins. Every example in the spec MUST become an automated `pytest` test.
Rationale: spec examples are the acceptance criteria; automating them keeps spec and code aligned.

### VII. Keep It Simple
The project MUST use Python 3.11+ with the standard library plus PyYAML and pytest only. No web
framework and no other third-party dependencies MAY be added without an approved exception.
Rationale: this is a proof of concept; minimal tooling keeps the focus on the process.

### VIII. Invalid Input Fails Loudly
When input is invalid, the program MUST show a clear error message. It MUST NEVER display a wrong
number as a result.
Rationale: a visible error is always safer than a silently incorrect amount.

## Technology Constraints

- Language: Python 3.11 or newer.
- Runtime dependencies: standard library and PyYAML only.
- Test dependencies: pytest only.
- Configuration: `config/rates.yaml` is the only place rates are defined (Principle I).
- Network access: none at runtime (Principle V).

## Development Workflow & Quality Gates

- Spec examples are converted to failing pytest tests first, then code is written to pass them
  (Principle VI).
- Every change MUST be reviewed for compliance with this constitution before merge.
- Any change to `config/rates.yaml` MUST include Product Owner approval (Principle II).
- Reviews MUST confirm: no `float` in money paths, conversions are logged, no network calls, and
  invalid input produces an error rather than a number.

## Governance

- This constitution supersedes other practices for this project.
- Amendments to this constitution require Enterprise Architect approval, MUST be documented, and
  MUST update the version and amendment date below.
- Versioning follows semantic versioning: MAJOR for removed or redefined principles, MINOR for
  added principles or materially expanded guidance, PATCH for clarifications and wording.
- Any code that breaks a principle MUST have a written exception stating the reason, an owner
  and an end date. Expired exceptions MUST be resolved or renewed with approval.
- Compliance is verified at every review against the Core Principles and Quality Gates above.

**Version**: 1.0.0 | **Ratified**: 2026-10-17 | **Last Amended**: 2026-10-17
