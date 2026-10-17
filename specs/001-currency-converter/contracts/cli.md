# CLI Contract: `python -m converter`

Run from the repository root.

## Command

```text
python -m converter <amount> <country>
```

| Argument | Description |
|----------|-------------|
| amount | Dollar amount, plain decimal number, more than 0 and at most 1000000 |
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
| `1000001 US` | `Amount must be 1000000 or less` |
| `.5 US` | `Amount must be a number` |
| `5. US` | `Amount must be a number` |
| `+5 US` | `Amount must be a number` |
| `abc UK` | `Amount must be a number` (amount is checked first) |

System errors (spec FR-018 and FR-019), also stderr, exit code 1, no result:

| Situation | stderr |
|-----------|--------|
| Rates file missing, unreadable, invalid, or not defining both US and CA | `Rates are unavailable` |
| Log line cannot be written | `Could not write the conversion log` |

Missing arguments: argparse prints its usage message to stderr and exits with code 2. No number is
shown.
