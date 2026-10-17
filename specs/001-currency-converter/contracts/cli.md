# CLI Contract: `python -m converter`

Run from the repository root.

## Command

```text
python -m converter <amount> <country>
```

| Argument | Description |
|----------|-------------|
| amount | Dollar amount, plain decimal number, more than 0 and at most 1000000. Always the first argument, even when it starts with "-" |
| country | `US` or `CA`, any letter case |

## Success

- stdout: `<result> INR`, result with exactly 2 decimals and no thousands separator
- exit code: 0
- side effect: one line appended to `logs/conversions.log`

| Input | stdout |
|-------|--------|
| `100 US` | `9000.00 INR` |
| `100 CA` | `10000.00 INR` |
| `2.50 US` | `225.00 INR` |
| `100 us` | `9000.00 INR` |
| `1000000 US` | `90000000.00 INR` |
| `1000000 CA` | `100000000.00 INR` |
| `0.00006 US` | `0.01 INR` |

## Errors

- stderr: the message only (exact text below), stdout is empty
- exit code: 1
- no log line is written

| Input | stderr |
|-------|--------|
| `100 UK` | `Only US and CA are supported` |
| `0 US` | `Amount must be more than 0` |
| `-5 CA` | `Amount must be more than 0` |
| `abc US` | `Amount must be a number` |
| `1,000 US` | `Amount must be a number` |
| `1e5 US` | `Amount must be a number` |
| `-1e5 US` | `Amount must be a number` |
| `-abc US` | `Amount must be a number` |
| `-1,000 US` | `Amount must be a number` |
| `.5 US` | `Amount must be a number` |
| `5. US` | `Amount must be a number` |
| `+5 US` | `Amount must be a number` |
| `1000001 US` | `Amount must be 1000000 or less` |
| `0.00001 US` | `Amount is too small to convert` |
| `abc UK` | `Amount must be a number` (amount is checked first) |

Order of checks: amount, then country, then the rates file, then the calculation (spec FR-023). So
`abc US` shows the amount error even when the rates file is missing.

System errors (spec FR-018 and FR-019), also stderr, exit code 1, no result:

| Situation | stderr |
|-----------|--------|
| Rates file missing, unreadable, invalid YAML, not exactly US and CA, or a rate that is not a number greater than 0 | `Rates are unavailable` |
| Log line cannot be written | `Could not write the conversion log` |

## Wrong number of arguments (spec FR-021)

None, one, or more than two arguments: argparse prints its usage message to stderr and the program
exits with code 2. stdout is empty and no number is shown. No log line is written.

`-h` and `--help` show the usage help and exit with code 0.
