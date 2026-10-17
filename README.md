# Currency Converter (POC) — Learn Spec-Driven Development

A tiny command-line program that converts an amount in **US** or **Canadian** dollars into **Indian Rupees (INR)**.

The program is simple on purpose. The real goal is to **practise Spec-Driven Development (SDD)** with [GitHub Spec Kit](https://github.com/github/spec-kit) and Claude Code, so the same way of working can be used on a larger project.

This README is also a **step-by-step walkthrough**. Every command and every prompt we used is below, in the order we ran them, so anyone can repeat the exercise.

---

## What the program does

| You type | You get |
| --- | --- |
| `python -m converter 100 US` | `9000.00 INR` |
| `python -m converter 100 CA` | `10000.00 INR` |
| `python -m converter 100 UK` | Error: `Only US and CA are supported` |
| `python -m converter abc US` | Error: `Amount must be a number` |

### Fixed rates

| Country | Code | Rate |
| --- | --- | --- |
| United States | `US` | 1 dollar = 90 INR |
| Canada | `CA` | 1 dollar = 100 INR |

Rates live only in `config/rates.yaml`. Only the Product Owner can approve a change.

---

## Who does what

| Role | Like in a house… | Job in this project |
| --- | --- | --- |
| Product Owner (PO) | The family who wants the house | Says **what** we need and **why** |
| Enterprise Architect (EA) | The city's building rules | Sets the rules every project must follow (the constitution) |
| Solution Architect (SA) | The house architect | Decides **how** to build it, inside the EA's rules |
| Tech Lead (TL) | The site supervisor | Breaks work into tasks, reviews code |
| Developer (Dev) | The builder | Builds it with the AI |
| QA (Tester) | The inspector | Checks everything works, including user mistakes |
| AI (Claude Code) | A very fast helper | Writes drafts, code and tests. **Never makes the final decision.** |

---

## The flow at a glance

| # | Step | Who | Spec Kit command | Output |
| --- | --- | --- | --- | --- |
| 0 | Set up the project | Dev | `specify init` | `.specify/`, `.claude/` |
| 1 | Project rules | EA | `/speckit-constitution` | `.specify/memory/constitution.md` |
| 2 | What we want | PO | `/speckit-specify` | `docs/intent.md` → `specs/001-.../spec.md` |
| 3 | Remove guesses | PO + QA | `/speckit-clarify` | Clarifications in `spec.md` |
| 4 | How to build it | SA | `/speckit-plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/` |
| 5 | Break into tasks | TL | `/speckit-tasks` | `tasks.md` |
| 6 | Check before building | TL + all | `/speckit-analyze` | Analysis report (no files changed) |
| 7 | Build | Dev + AI | `/speckit-implement` | Code and tests |
| 8 | Test, review, release | QA + approvers | `pytest` + pull request | Merged to `main` |

**Golden rule:** the AI fills gaps with reasonable guesses. After every step, a human reads the output and decides whether those guesses are what the business wants. If a later step invents a new behaviour, it goes **back into the spec** first.

---

## Step 0 — Set up the project (Developer)

### Prerequisites

- Python **3.11+** (`python --version`)
- Git (`git --version`)
- A GitHub account
- [Claude Code](https://www.anthropic.com/claude-code)
- VS Code

### 0.1 Create the folder and start Git

Run in the terminal:

```bash
mkdir currency-converter
cd currency-converter
git init
mkdir docs config converter tests
code .
```

### 0.2 Create `.gitignore`

On Windows (Command Prompt or PowerShell), run:

```bat
(echo .venv/& echo __pycache__/& echo .pytest_cache/& echo *.log& echo .claude/settings.local.json) > .gitignore
```

Check it with `type .gitignore`. You should see 5 lines.

### 0.3 Tell Git who you are (once per computer)

```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

### 0.4 Install uv and Spec Kit

On Windows, run:

```bat
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close the terminal and open a new one, then run:

```bash
uv tool install specify-cli
specify version
```

### 0.5 Add Spec Kit to the project

```bash
specify init --here --script ps
```

- Answer `y` when it warns that the folder is not empty.
- Choose **claude (Claude Code)** as the coding agent.
- Use `--script ps` on Windows, or `--script sh` on macOS or Linux.

### 0.6 First commit and push to GitHub

Create an **empty** repo named `currency-converter` on github.com. Leave "Add a README" **unticked**. Then run:

```bash
git add .
git commit -m "Add Spec Kit and README"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/currency-converter.git
git push -u origin main
```

### 0.7 Create the feature branch

Spec Kit only creates branches when its optional Git hook is installed, so create the branch yourself:

```bash
git checkout -b 001-currency-converter
git push -u origin 001-currency-converter
```

Everything from here on goes on this branch, and arrives in `main` as **one pull request**.

### 0.8 Start Claude Code

```bash
claude
```

All the prompts below are **pasted into Claude Code**, not into the terminal.

> With Claude Code, Spec Kit commands use a **dash**: `/speckit-specify`, not `/speckit.specify`.

---

## Step 1 — Constitution: the project rules (Enterprise Architect)

The constitution holds the non-negotiable rules. In a real company these exist **before** any feature request, which is why this step comes first.

**Prompt** (paste into Claude Code):

```text
/speckit-constitution This is a small proof-of-concept currency converter used to practise spec-driven development. The Enterprise Architect sets these non-negotiable principles:

1. Rates live in one settings file only (config/rates.yaml), never written inside the code.
2. Only the Product Owner may approve a change to rates.yaml.
3. Money uses exact decimal maths (Python Decimal), never float. Results are rounded to 2 decimal places.
4. Every conversion is logged with amount, country, result and time.
5. No internet or external service calls. The program runs fully offline.
6. Tests are written before code. Every example in the spec must become an automated test (pytest).
7. Keep it simple: Python 3.11+, standard library plus PyYAML and pytest only. No web framework.
8. If input is invalid, show a clear error. Never show a wrong number.

Governance: changes to this constitution need Enterprise Architect approval. Any code that breaks a principle needs a written exception with a reason, an owner and an end date.
```

**What we got:** `.specify/memory/constitution.md` v1.0.0, with 8 principles. Test-First is marked NON-NEGOTIABLE.

**Human review (EA):** the AI added three sensible rules, and we kept them:
- Tests may use fake rate files.
- A change to `rates.yaml` needs recorded PO approval before merge.
- Expired exceptions must be resolved or renewed.

**Save:**

```bash
git add .
git commit -m "docs: adopt constitution v1.0.0 (8 core principles + governance)"
git push
```

---

## Step 2 — Specify: what we want (Product Owner)

The PO describes **what** and **why** only. Leave out Python, files and technology; the constitution already covers those.

The idea flows through three documents, each more exact than the last:

| Document | Written by | Purpose | Changes later? |
| --- | --- | --- | --- |
| `docs/intent.md` | PO, in their own words | Records the original idea and why | No, it's the starting point |
| `/speckit-specify` prompt | PO | Points the AI at the intent and adds exact examples | No, it's a one-time input |
| `spec.md` | AI, reviewed by people | The exact, testable source of truth | Yes, it grows through clarify, plan and analyze |

Keep the PO's words in **one file** (`intent.md`). The prompt only adds what's new, such as exact examples.

### 2.1 The PO writes the intent

Create `docs/intent.md`:

```markdown
# Intent: Currency converter (POC)

## What we want
A user types an amount and a country code (US or CA)
and sees the value in Indian Rupees (INR).

## Why
To practise our new step-by-step way of working on something small.

## Rules
- US: 1 dollar = 90 INR
- CA: 1 dollar = 100 INR
- Any other country: show a clear error message

## Not included
- Other countries
- Live or changing rates
- Converting from INR to other currencies

Approved by: <PO name> (Product Owner)   Date: <date>
```

**Save:**

```bash
git add docs/intent.md
git commit -m "docs: PO intent for currency converter"
```

### 2.2 Turn the intent into a spec

**Prompt:**

```text
/speckit-specify Use docs/intent.md as the Product Owner's intent. Also apply these details:

The result is shown in INR with 2 decimal places. Country codes are accepted in small or capital letters.

Examples that must work exactly like this:
- 100 US -> 9000.00 INR
- 100 CA -> 10000.00 INR
- 2.50 US -> 225.00 INR
- 100 us -> 9000.00 INR
- 100 UK -> error "Only US and CA are supported"
- 0 US -> error "Amount must be more than 0"
- -5 CA -> error "Amount must be more than 0"
- abc US -> error "Amount must be a number"

If the input is wrong, the user sees a clear error and never a wrong number.
```

> In our first run we typed the whole idea into the prompt and skipped `intent.md`, so the PO's words ended up in two places. The version above is the corrected way.

**What we got:** `specs/001-currency-converter/spec.md` with 3 user stories, 13 requirements and 5 success criteria, plus `checklists/requirements.md` (16/16 passing).

**Human review (PO + QA):** Claude Code said there were no open questions. A human reviewer still found four quiet guesses:
1. `9000.00` vs `9,000.00`: the spec and README disagreed.
2. The AI *assumed* amounts like `2.505` are accepted and rounded.
3. No maximum amount was set.
4. "One error is shown" when both fields are wrong, but not *which* one.

**Lesson:** the AI marking "no questions" does not mean there are no questions.

---

## Step 3 — Clarify: remove the guesses (PO + QA)

### 3.1 Let Spec Kit ask its own questions

**Prompt:**

```text
/speckit-clarify
```

Claude Code asks up to 5 questions, one at a time. **Our answers:**

| # | Question | PO answer |
| --- | --- | --- |
| 1 | How are exact halves rounded? | Round half up (0.135 → 0.14) |
| 2 | Amounts with more than 2 decimals? | Accept them and convert exactly, rounding only at the end |
| 3 | Both fields wrong — which error? | Amount error first (`abc UK` → "Amount must be a number") |
| 4 | Where is the conversion log? | A file on disk, one line per conversion |
| 5 | Log failed conversions? | No, only successful ones |

### 3.2 Add what the tool missed

`/speckit-clarify` caught 2 of our 4 review points, and asked 3 good ones we hadn't thought of. We added the rest by hand.

**Prompt:**

```text
Update the spec with two more PO decisions, recorded in the same Clarifications session:
1. Results are shown with no thousands separator, e.g. 9000.00 (not 9,000.00).
2. Maximum amount is 1000000. Larger amounts give error "Amount must be 1000000 or less". Amounts with commas (1,000) or scientific notation (1e5) give "Amount must be a number".
Add these as examples in the acceptance scenarios.
```

**Lesson:** the tool and a human reviewer each catch things the other misses. Use both.

**Save:**

```bash
git add .
git commit -m "spec: record clarifications (rounding, errors, logging, format, max)"
git push
```

---

## Step 4 — Plan: how to build it (Solution Architect)

The spec says **what**; the plan says **how**.

**Prompt:**

```text
/speckit-plan Solution Architect decisions:
- Python 3.11+, standard library plus PyYAML and pytest only (as the constitution says).
- Command line: "python -m converter 100 US". Use argparse.
- Rates read only from config/rates.yaml (US: 90, CA: 100).
- Use Decimal with ROUND_HALF_UP for the final 2-decimal result.
- Three small parts: input checker, rate reader, calculator, plus a small CLI entry point.
- Log successful conversions to logs/conversions.log, one line per conversion: ISO timestamp, amount, country, result in INR, separated by " | ".
- Folders: converter/ for code, tests/ for pytest tests, config/ for rates.
- Every acceptance example in the spec must map to a named test.
Keep the design as simple as possible.
```

**What we got:** `plan.md`, `research.md`, `data-model.md`, `contracts/cli.md` and `quickstart.md`. All 8 constitution principles pass, and there's a 25-row test table.

**Human review (SA):** the plan invented three behaviours the spec didn't have. **Anything the program does must be in the spec first**, so we pushed them back.

**Prompt:**

```text
The PO accepts these three plan decisions. Add them to the spec (Clarifications session, functional requirements, and edge cases with exact messages):
1. Amounts like .5, 5. and +5 are rejected with "Amount must be a number".
2. If the rates file is missing or unreadable: "Rates are unavailable", no result shown.
3. If the conversion log cannot be written: "Could not write the conversion log", no result shown.
Make sure plan.md's test table still matches the spec.
```

**Save:**

```bash
git add .
git commit -m "plan: 001 implementation plan; spec updated with plan decisions"
git push
```

---

## Step 5 — Tasks: break it down (Tech Lead)

**Prompt:**

```text
/speckit-tasks
```

**What we got:** `tasks.md`, a numbered task list (T001–T033), with tests listed before the code they test.

---

## Step 6 — Analyze: check before building (Tech Lead + everyone)

This step compares the spec, plan, tasks and constitution. It only reports, and changes no files.

**Prompt:**

```text
/speckit-analyze
```

**What it found:** 0 critical, 2 high, 3 medium and 5 low issues. The two HIGH ones:
- **I1:** adding `UK: 5` to the rates file would silently enable UK, which is scope creep through a back door.
- **C1:** a rate of `0` or `-90` would produce a wrong number.

**Our decisions:**

| ID | Decision | Who |
| --- | --- | --- |
| I1 | Only US and CA are supported. The rates file must contain exactly those two. | PO |
| C1 | Each rate must be a number greater than 0. | EA |
| U1 | A result that rounds to 0.00 shows "Amount is too small to convert". | PO |
| I2 | Amounts starting with `-` are always treated as amounts, not options. | SA |
| I3 | Check the input first, then load the rates. | SA |
| U2 | Invalid YAML or a missing US/CA entry gives "Rates are unavailable". | PO |
| U3 | A wrong number of arguments shows usage and exits with code 2. | SA |
| G1 | An automated test checks for no network imports and no hard-coded rates. | EA |
| D1, T1 | Wording fixes. | TL |

**Prompt:**

```text
Approved. Apply these decisions to spec.md, plan.md, research.md, data-model.md, contracts/cli.md and tasks.md as needed:

I1 (PO): Supported countries are fixed to US and CA by the spec. rates.yaml must contain exactly US and CA; missing or extra keys give "Rates are unavailable".
C1 (EA): Each rate must be a number greater than 0, otherwise "Rates are unavailable". Add tests.
U1 (PO): If the converted result rounds to 0.00, show error "Amount is too small to convert". Add to spec and tests.
I2 (SA): Amounts starting with "-" are always treated as the amount, never as a command-line option. Add tests for -5, -1e5, -abc, -1,000.
I3 (SA): Check input first, then load rates. Update the plan checking order and T016.
U2 (PO): Add invalid YAML and missing US/CA entries to FR-018.
U3 (SA): Wrong number of arguments shows usage and exits with code 2. Add as an edge case and a test.
G1 (EA): Add an automated test that converter/ contains no network imports and no hard-coded rate values, replacing the manual grep in T033.
D1, T1 (TL): Apply your suggested wording fixes.

Record the product decisions in the spec's Clarifications section. Then run /speckit-analyze again.
```

Repeat until the analysis shows **no HIGH or MEDIUM issues**.

**Lesson:** the analyze step found real problems **before any code existed**. At that point a fix costs one sentence, not a bug.

**Save:**

```bash
git add .
git commit -m "tasks: 001 task list; fixes from analyze"
git push
```

---

## Step 7 — Implement: build it (Developer + AI)

**Prompt:**

```text
/speckit-implement
```

Claude Code works through `tasks.md` in order. For each story it writes the **tests first**, checks they fail, then writes the code until they pass.

**What we got:**
- `config/rates.yaml` with US 90 and CA 100, and a note that changes need PO approval
- `converter/`: `checker.py`, `rates.py`, `calculator.py`, `cli.py`, `__main__.py`
- `tests/`: acceptance, arguments, checker, rates, calculator, constitution guards, and fixtures
- `requirements.txt` listing PyYAML and pytest only
- All 35 tasks marked `[X]`, with **88 tests passing**

**Two moments worth noticing:**
- **The guard tests caught the AI's own mistake.** Its first draft of `rates.py` used `float`, and the constitution test failed. The rules are checked by the computer, not just written down.
- **It proved the guards work.** It deliberately added `float(1)`, `import socket` and a hard-coded `90`, watched all three guard tests fail, then removed them. A test you have never seen fail might be testing nothing.

**Human review (Dev + QA):** run the tests and try the program yourself (see [How to run](#how-to-run)). Try to break it with your own inputs.

---

## Step 8 — Converge, review and release (QA + approvers)

### 8.1 Drift check: does the code still match the documents?

**Prompt:**

```text
/speckit-converge
```

It compares the finished code with the spec, plan, tasks and constitution, and appends any gaps to `tasks.md`. It found 2 LOW gaps:
- **F1:** `-h` and `--help` show help, but the spec said anything starting with `-` is an amount.
- **F2:** the PO approval of the rates wasn't recorded in a commit yet.

It also noticed that leading zeros like `00005` are accepted, though the spec doesn't mention them.

**Our decisions and prompt:**

```text
PO decisions:
- F1: Keep -h/--help as the one exception to FR-022. Update FR-022 in the spec to say so, and complete T036 with a test.
- Leading zeros (e.g. 00005) are accepted and mean the same number. Add this to the spec's edge cases and add a test.
- F2/T037: I will record the PO approval myself in the commit that adds config/rates.yaml. Mark T037 done with that note. Do not make any git commits.

Then run /speckit-implement to finish T036, and /speckit-converge again.
```

Repeat until `/speckit-converge` reports **no gaps**.

**Lesson:** even after all tests pass, the code can quietly do things the spec doesn't say. Converge finds them so the spec stays the source of truth.

### 8.2 Commit in three parts

The rates get their own commit, so the **PO approval is recorded** (constitution Principle II).

```bash
git add config/rates.yaml
git commit -m "config: rates US=90, CA=100" -m "Approved-by: <PO name> (Product Owner)"

git add README.md
git commit -m "docs: README walkthrough with all SDD steps and prompts"

git add .
git commit -m "feat: 001 currency converter (all tasks done, converge clean)"

git push
```

### 8.3 Pull request and sign-off

1. On GitHub, click **Compare & pull request** for `001-currency-converter`.
2. Title it `001: Currency converter POC`.
3. Use this description. Each role ticks its own box:

```markdown
## What
Converts US/CA dollars to INR (US=90, CA=100). Spec: specs/001-currency-converter/spec.md

## Review checklist
- [ ] PO: behaviour matches spec examples; rates.yaml approved
- [ ] EA: constitution guard tests pass (no float, no network, no hard-coded rates)
- [ ] SA: code follows plan.md structure
- [ ] TL: all tasks in tasks.md marked done; code reviewed
- [ ] QA: all tests pass; manual checks done

## Known follow-ups
- Low-severity analyze items N1–N5
```

4. When every box is ticked, click **Merge pull request**. The feature is released to `main`.

---

## How to run

Requires **Python 3.11 or newer**. The commands below are for Windows; on macOS or Linux, use `.venv/bin/python` instead of `.venv\Scripts\python`.

### One-time setup

```bash
git clone https://github.com/prasanth2006z/currency-converter.git
cd currency-converter
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

If you don't have Python 3.12, use any version from 3.11 up: `py -3.11 -m venv .venv`.

### Run the tests

```bash
.venv\Scripts\python -m pytest
```

All tests should pass.

### Use the program

```bash
.venv\Scripts\python -m converter 100 US
.venv\Scripts\python -m converter 100 CA
.venv\Scripts\python -m converter 2.50 us
.venv\Scripts\python -m converter 100 UK
```

Expected output: `9000.00 INR`, `10000.00 INR`, `225.00 INR`, and then the error `Only US and CA are supported`.

### See the conversion log

```bash
type logs\conversions.log
```

Each **successful** conversion adds one line: `timestamp | amount | country | result`. Failed conversions are not logged. On macOS or Linux, use `cat logs/conversions.log`.

---

## Gotchas we hit (so you don't have to)

| Problem | Cause | Fix |
| --- | --- | --- |
| `'.venv' is not recognized as an internal or external command` | File content was typed into the terminal | File content goes in a file; only commands go in the terminal |
| A `.gitignore` line got merged with the previous one | The file had no line break at the end | Rewrite the whole file with `> .gitignore` (Step 0.2) |
| `Author identity unknown` | Git name and email not set | Step 0.3 |
| `src refspec main does not match any` | No commit exists yet | Commit first, then push |
| `remote origin already exists` | The remote was added with the placeholder `YOUR-USERNAME` | `git remote set-url origin https://github.com/<you>/currency-converter.git` |
| Long text pasted into PowerShell broke | Backticks and special characters | Create the file in VS Code (`code FILE`) and paste there |
| `LF will be replaced by CRLF` | Windows line endings | Harmless; ignore |
| No feature branch created by Spec Kit | The optional Git hook isn't installed | Create it yourself (Step 0.7) |
| `docs/intent.md` missing | Skipped while fixing Git setup; the idea was typed straight into the specify prompt | Write `intent.md` first and point `/speckit-specify` at it (Step 2) |
| `/speckit.specify` not found | Claude Code uses dashes | `/speckit-specify` |
| Tests fail with plain `python -m pytest` | The default `python` is 3.10, and the project needs 3.11+ | Use the project's `.venv` (see [How to run](#how-to-run)) |
| The AI marked a task done that needed a human action (PO approval) | Some tasks are human decisions, not code | `/speckit-converge` caught it; record approvals in commits |

---

## Project structure

```
currency-converter/
  .specify/                 Spec Kit: constitution, templates, scripts
  .claude/skills/           Spec Kit skills for Claude Code
  docs/intent.md            Product Owner's intent
  specs/001-currency-converter/
    spec.md                 What (PO)
    plan.md                 How (SA)
    research.md             Small design decisions
    data-model.md           Data shapes
    contracts/cli.md        Exact outputs and exit codes
    quickstart.md           How to run
    tasks.md                Task list (TL)
    checklists/             Quality checklists
  config/rates.yaml         Fixed rates (PO approves changes)
  converter/
    checker.py              Checks amount and country
    rates.py                Reads and validates rates.yaml
    calculator.py           Decimal maths and rounding
    cli.py                  Command line, errors, logging
    __main__.py             Lets you run: python -m converter
  tests/                    Automated tests (incl. constitution guards)
  logs/conversions.log      Created at run time (not in Git)
  requirements.txt          PyYAML and pytest
```

---

## Status

- [x] Step 0: Project set up with Spec Kit
- [x] Step 1: Constitution (EA)
- [x] Step 2: Spec (PO)
- [x] Step 3: Clarifications (PO + QA)
- [x] Step 4: Plan (SA)
- [x] Step 5: Tasks (TL)
- [x] Step 6: Analyze and fixes
- [x] Step 7: Implement (35 tasks, 88 tests at first build)
- [x] Step 8: Converge, review and release

## What to try next

- Practise a **business change**: ask to change the CA rate to 105. Only `config/rates.yaml` should change, with a PO-approved commit.
- Practise a **feature change**: add a third country with `/speckit-specify` as feature `002`, and see which roles and rules it touches.
- Use the same 8 steps on your real project.