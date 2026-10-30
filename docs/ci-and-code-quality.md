# CI and code quality

Back to the [README](../README.md).

## Continuous integration (GitHub Actions)

`.github/workflows/tests.yml` runs on every push to `main`, on pull requests, and on demand:

1. Lint and type check: ruff (lint and format check), mypy and the AAA linter.
2. E2E tests in Chromium, Firefox and WebKit, in parallel jobs (Python 3.12), and in Chromium on Python 3.14.
   Inside a job, the tests run in pytest-xdist workers: 4 for Chromium, 2 for Firefox, none for WebKit.
   The GitHub runner has 4 CPUs. With 4 or 6 workers, WebKit tests timed out on `check()`, and Firefox gained little.
3. Proofs: the tests in `proofs/` run in Chromium (4 workers), so they cannot stop working unnoticed.
   Each proof waits for a failing check to time out, so workers make this job about 3 times faster.
4. Allure report: one report for all three browsers, built even when tests fail.
   The `allure-report` artifact holds `index.html`. Download it and open it.
5. Publish to GitHub Pages, on `main` after a push or a manual run (never for pull requests).
   The report is published at the link at the top of the [README](../README.md).
   In a fork, turn it on with Settings → Pages → Source: GitHub Actions and the repository variable
   `PAGES_ENABLED` = `true` (Settings → Secrets and variables → Actions → Variables). Without it, this step is skipped.

## Code quality

The tools are installed with `requirements.txt`. Their versions match `.pre-commit-config.yaml`.
ruff replaces black, isort and flake8 (settings in `pyproject.toml`). CI installs the packages with
[uv](https://docs.astral.sh/uv/) (`uv pip install --system -r requirements.txt`). Locally, plain `pip` works the same way.

Run the commands from the project root.

```powershell
.\.venv\Scripts\python.exe -m ruff check lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe -m ruff format lib test_e2e proofs tools conftest.py   # add --check to only look
.\.venv\Scripts\python.exe -m mypy lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe tools/aaa_structure_linter.py   # checks the Given / When / Then comments
```

In a Git repository, `pre-commit install` runs the same checks before each commit.
