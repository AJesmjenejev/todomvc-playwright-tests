# TodoMVC Playwright tests (Python)

[![Tests](https://github.com/AJesmjenejev/todomvc-playwright-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/AJesmjenejev/todomvc-playwright-tests/actions/workflows/tests.yml)

Automated end-to-end tests for https://demo.playwright.dev/todomvc/#/
using Playwright, pytest and the Python synchronous API. Results are written for an Allure report.

**Latest test report (Chromium, Firefox, WebKit):** https://ajesmjenejev.github.io/todomvc-playwright-tests/

## What is tested

| Requirement | Tests |
|---|---|
| Add a todo with English text | `test_add_todo_english_text_is_listed` |
| Add a todo with non-English characters | `test_add_todo_non_english_text_is_listed` (Czech, Russian, Japanese, Arabic, emoji) |
| Add a todo that includes numbers | `test_add_todo_text_with_numbers_is_listed` |
| Complete a todo, see it in "Completed" | `test_complete_todo_appears_in_completed_view` |
| Delete a todo, it is gone from every view | `test_delete_todo_is_gone_from_every_view` (All, Active, Completed) |
| "Active" shows only unfinished todos | `test_filter_active_shows_only_incomplete_todos` |
| "Completed" shows only finished todos | `test_filter_completed_shows_only_completed_todos` |

Extra tests cover blank input, trimming, un-completing a todo, the "All" view, the items-left counter
(which counts active todos in every view), HTML/script input, a very long title, duplicate titles, and persistence
(a reload keeps the todos, their state and the selected filter; a new browser session starts empty).

## Test approach

**Goal.** Cover the 7 requirements with tests that are easy to read and **can really fail**.
Each one was written to check the user-visible result, not an implementation detail.

**How the cases were chosen**

- **Input classes for titles.** English, then one representative per kind of text:
  Latin with diacritics (Czech), Cyrillic, Japanese, right-to-left Arabic, emoji, and digits in three positions.
- **Boundaries.** Empty and spaces-only titles (must be ignored), spaces around a title (must be trimmed),
  and a 300-character word without spaces (must wrap, not overflow).
- **States × views.** A todo is either active or completed, and there are three views (All, Active, Completed).
  The filter and delete tests use both states, so each view is checked with something that should and should not show.
- **Security mindset.** HTML and an `onerror` script in a title must be shown as text and never rendered (XSS).

**How the checks avoid false passes**

- The visible list is compared **exactly** (text and order), so anything extra, missing or untrimmed fails.
- "Gone" is never checked alone. The test checks the exact remaining list, which also proves the view rendered.
- The delete test removes one active and one completed todo, so each view showed one of them before the delete.
- Key checks are proven to fail when the app breaks. Each row below is one test in `proofs/`: it breaks the
  app (or our code) on purpose and expects the real check to fail.

| Break | How it is broken | Check that catches it |
|---|---|---|
| Delete does nothing | `monkeypatch.setattr(TodoPage, "delete_todo", ...)` (a no-op) | `expect_todos` (exact remaining list) |
| Title not trimmed | `label.evaluate("label => label.textContent = '   padded   '")` | `expect_todos` (exact text) |
| Title rendered as HTML | `label.evaluate("label => label.innerHTML = '<b>bold</b>'")` | `expect_titles_are_plain_text` |
| Long title does not wrap | `page.add_style_tag(...)` with `white-space: nowrap` or `width: max-content` | `expect_todo_title_fits_in_list` |
| Wrong duplicate completed | `monkeypatch.setattr(TodoPage, "complete_todo", ...)` (always the first) | `expect_todo_completed(..., nth=1)` |
| Wrong view URL | `page.evaluate("history.replaceState(null, '', '#/completed')")` | `expect_view_opened` |
| Completed todo not crossed out | `item.evaluate("item => item.classList.remove('completed')")` | `expect_todo_completed` |
| App does not save | `page.evaluate("localStorage.clear()")` before the reload | `expect_todos` after reload |
| Sessions share storage | a second page in the **same** context instead of a new one | `expect_todos` in the second session |

Run the proofs with `python -m pytest proofs` (about one minute: each failing check waits for its timeout).
They are not part of the normal run, because `pyproject.toml` sets `testpaths = ["test_e2e"]`.

**Out of scope, on purpose**

| Not tested | Why |
|---|---|
| Editing a todo (double-click, Enter, Escape) | Not in the 7 requirements; the next feature I would add |
| "Mark all as complete", "Clear completed" | Not in the requirements |
| Accessibility, visual layout, performance | Need other tools (axe-core, screenshot diffs, load tools) |
| Cross-tab sync | The demo does not claim to support it |

**Risks and limits**

- The tests use a **public demo site**. If it is down or changes, tests fail in setup, not because of a bug.
- Exact text checks are strict on purpose. A harmless text change (for example in the counter wording) fails a test.
- Every test starts with a fresh browser context, so the test **data** is parallel-safe.
  The **log file** is not yet: with pytest-xdist, all workers would write to the same `logs/tests.log` and mix
  their lines. To run in parallel, each worker would need its own file (for example `logs/tests-gw0.log`,
  named from the `PYTEST_XDIST_WORKER` environment variable). The suite takes about 15 seconds, so this is not needed yet.

**How I would extend it**

1. Editing, then "Clear completed" and "Mark all as complete".
2. An accessibility scan (axe-core) and a few visual snapshots.

## Requirements

- Python 3.12 or newer. CI runs on Python 3.12 in Chromium, Firefox and WebKit. Python 3.14 was checked once locally.
- Internet access (the tests use the public demo site)
- Optional, to build the Allure report: [Node.js](https://nodejs.org/) (Allure 3 runs on Node.js; no Java needed)

## Setup

Get the code:

```bash
git clone https://github.com/AJesmjenejev/todomvc-playwright-tests.git
cd todomvc-playwright-tests
```

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv   # or any newer installed version, e.g. py -3.14
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

macOS / Linux:

```bash
python3 -m venv .venv    # python3 --version must be 3.12 or newer
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium   # --with-deps adds system libraries on Linux
```

## Run the tests

Use the venv's Python. You do not need to activate the venv.

```powershell
# All tests (headless Chromium, the default browser)
.\.venv\Scripts\python.exe -m pytest

# Watch the browser
.\.venv\Scripts\python.exe -m pytest --headed

# Show each step live in the console
.\.venv\Scripts\python.exe -m pytest -o log_cli=true

# One test, or one file
.\.venv\Scripts\python.exe -m pytest -k test_filter_active
.\.venv\Scripts\python.exe -m pytest test_e2e/test_filters.py

# Other browsers (install them first: python -m playwright install firefox webkit)
.\.venv\Scripts\python.exe -m pytest --browser firefox
.\.venv\Scripts\python.exe -m pytest --browser chromium --browser firefox --browser webkit

# The Google Chrome installed on your PC instead of Playwright's Chromium (reported as "chromium")
.\.venv\Scripts\python.exe -m pytest --browser-channel chrome
```

On macOS / Linux, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`.

## Reports and logs

| What | Where |
|---|---|
| Allure raw results (replaced on every run) | `allure-results/` |
| Allure HTML report (one file) | `allure-report/index.html` |
| Text log: steps (INFO) and page actions (DEBUG) | `logs/tests.log` |
| Screenshot and trace of a failed test (one of each per browser context) | `test-results/`, and both are attached in Allure |

The log file has one block per test: a header, the business steps (INFO), the page actions under each step
(DEBUG, indented), and the result:

```
17:02:01 INFO  ==================== test_e2e/test_add_todo.py::TestAddTodo::test_add_todo_english_text_is_listed[chromium]
17:02:03 INFO  Open the TodoMVC app
17:02:03 DEBUG    Navigate to './'
17:02:03 INFO  Add todo 'Buy milk'
17:02:03 DEBUG    Fill the new todo input with 'Buy milk' and press Enter
17:02:03 INFO  Expect the visible todos to be exactly ['Buy milk']
17:02:03 INFO  -------------------- PASSED in 1.5 s
```

If the test body passes but the cleanup after it fails, an extra line follows the result:
`ERROR -------------------- TEARDOWN FAILED: <error message>`.

Choose the log level per output (a level shows itself and everything above it):

| Output | Default | Change it with |
|---|---|---|
| Log file `logs/tests.log` | DEBUG | `--log-file-level=INFO` |
| Log printed in the terminal for a failed test | DEBUG | `--log-level=INFO` |
| Live console | off | `-o log_cli=true --log-cli-level=INFO` (or `DEBUG`) |

Build the Allure report after a test run. This uses [Allure 3](https://allurereport.org/docs/v3/), which runs on Node.js.
`npx` downloads it on first use, so there is nothing to install:

```powershell
npx -y allure@3.22.1 generate allure-results
```

Then open `allure-report/index.html` by double-clicking it. It is a single file, so no server is needed.
The settings (report name, single file) are in `allurerc.json`.

What the report shows:

- **Grouping**: by browser first (chromium / firefox / webkit), then by feature
  (Add / Complete / Delete / Filter todos, Input edge cases, Persistence). Set with `groupBy` in `allurerc.json`.
- **Titles and descriptions**: each test has a readable title. The description says what it checks and why.
- **Severity**: the 7 required cases are marked *critical*, so you can filter on them.
- **Steps**: every business step (for example "Add todo 'Buy milk'") is shown. The step that failed is marked red.
- **Attachments on failure**: a screenshot and the Playwright trace.

Open a Playwright trace locally with `python -m playwright show-trace test-results/<test>/trace.zip`,
or upload the `trace.zip` from the report to https://trace.playwright.dev.

## Continuous integration (GitHub Actions)

`.github/workflows/tests.yml` runs on every push to `main`, on pull requests, and on demand:

1. **Lint and type check**: black, isort, flake8, mypy and the AAA linter.
2. **E2E tests** in Chromium, Firefox and WebKit, in parallel.
3. **Allure report**: one report for all three browsers. It is built even when tests fail.
   The `allure-report` artifact holds `index.html`. Download it and open it.
4. **Publish to GitHub Pages** (on `main`, after a push or a manual run; never for pull requests):
   the report is published at the link at the top of this page.
   In a fork, turn it on with **Settings → Pages → Source: GitHub Actions** and the repository variable
   `PAGES_ENABLED` = `true` (**Settings → Secrets and variables → Actions → Variables**). Without it, this step is skipped.

## Code quality

The tools are installed with `requirements.txt`. Their versions match `.pre-commit-config.yaml`.

```powershell
$env:PYTHONUTF8 = "1"   # Windows: the tests contain non-English text

.\.venv\Scripts\python.exe -m black lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe -m isort lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe -m flake8 lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe -m mypy lib test_e2e proofs tools conftest.py
.\.venv\Scripts\python.exe tools/aaa_structure_linter.py   # # Given / # When / # Then, in order
```

In a Git repository, `pre-commit install` runs the same checks before each commit.

## Project layout

```
test_e2e/                    Test classes, one file per topic (add, complete, delete, filters, input edge cases, persistence)
proofs/                      Tests that break the app on purpose to prove the checks can fail (not in the normal run)
lib/
  keywords/todo_keywords.py  Business actions and expect_* checks (@allure.step + log)
  pom/page_base.py           BasePage: PATH, goto() and reload()
  pom/page_todo.py           TodoPage: locators (suffix names: _input, _lbl, _btn, _checkbox, _link) and actions
  utils/logger.py            TestLogger (info / debug)
  utils/text.py              exact_text(): exact text matching
  utils/constants/           TodoView StrEnum: All, Active, Completed
tools/aaa_structure_linter.py  Checks the Given / When / Then comments
conftest.py                  Fixtures; attaches screenshot and trace to Allure on failure
pyproject.toml               pytest, black, isort and mypy settings
allurerc.json                Allure 3 report settings
.github/workflows/tests.yml  CI: lint, tests in 3 browsers, Allure report, GitHub Pages
```

## Design notes

- **Three layers.** Tests call keywords. Keywords call page objects. Only page objects hold locators
  and touch the Playwright `Page`. If the site changes, you fix one page object, not every test.
  The URL check is the one place that needs the `Page`, so `TodoPage.wait_for_view_url` waits for the
  `#/...` route (defined once on `TodoView`) and the keyword only asserts the result.
- **Stable locators.** Role, placeholder and test-id locators. No CSS selectors, no `sleep()`.
- **Todos are found by exact title.** When several todos have the same title, pass `nth` (0 = first) to pick one.
  Without `nth`, a duplicate title stops the test with Playwright's strict-mode error instead of guessing.
- **Retrying assertions.** `expect(...)` waits for the UI to reach the expected state. There are no fixed waits.
  The layout check (long title) has no `expect` matcher, so the page object uses `wait_for_function`:
  it re-runs a small JS check in the browser until the text box is inside its todo item, or times out.
- **Checks that can fail.** Exact text matching, and an exact remaining list instead of "item is absent".
  The delete tests and the exact-text check were verified by breaking the code on purpose and watching them fail.
- **AAA layout.** `# Given` (if needed), `# When`, `# Then` in every test, checked by a linter.
- **Readable reports.** Keyword methods have `@allure.step(...)` and a matching log line.
  Test classes have `@allure.feature`. Tests have `@allure.title`, `@allure.severity`, and a docstring that becomes the description.
- **Independent tests.** Each test gets a new browser context, so `localStorage` starts empty and tests can run in any order.
- **External site.** The tests use the public demo site. If every test fails in setup, the site is probably unreachable.

## License

MIT. See [LICENSE](LICENSE).
