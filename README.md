# Currency Converter (POC)

A tiny program that converts an amount from **US** or **Canadian** dollars into **Indian Rupees (INR)**.

We built it to practise **Spec-Driven Development (SDD)** with [GitHub Spec Kit](https://github.com/github/spec-kit) and Claude Code, before using the same way of working on a larger project.

## What it does

| You type | You get |
| --- | --- |
| `100 US` | 9,000.00 INR |
| `100 CA` | 10,000.00 INR |
| `100 UK` | Error: Only US and CA are supported |

## Fixed rates

| Country | Code | Rate |
| --- | --- | --- |
| United States | US | 1 dollar = 90 INR |
| Canada | CA | 1 dollar = 100 INR |

Rates live only in `config/rates.yaml`. Only the Product Owner can approve a change.

## How we work: 8 steps

| Step | What happens | Who | Spec Kit command |
| --- | --- | --- | --- |
| 1 | Say what we want | Product Owner | `/speckit-specify` |
| 2 | Write exact rules and examples | PO + Tech Lead + QA | `/speckit-clarify`, `/speckit-checklist` |
| 3-4 | Set the project rules | Enterprise Architect | `/speckit-constitution` |
| 5 | Decide how to build it | Solution Architect | `/speckit-plan` |
| 6 | Build it with AI | Tech Lead + Developer + AI | `/speckit-tasks`, `/speckit-implement` |
| 7 | Test it | QA | `pytest` |
| 8 | Check and release | Right approver | `/speckit-analyze` + review |

The AI writes drafts, code and tests. **People make the decisions.**

## Project structure

```
currency-converter/
  .specify/      Spec Kit rules, templates and constitution
  .claude/       Spec Kit skills for Claude Code
  docs/          Intent and notes
  config/        rates.yaml
  converter/     Program code
  tests/         Automated tests
```

## Status

- [x] Step 0: Project set up with Spec Kit
- [x] Step 1: Product intent written
- [ ] Step 3: Constitution
- [ ] Step 2: Spec and examples
- [ ] Step 5: Plan
- [ ] Step 6: Build
- [ ] Step 7: Test
- [ ] Step 8: Release

## How to run

Coming after Step 6.