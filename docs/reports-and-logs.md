# Reports and logs

Back to the [README](../README.md).

| What | Where |
|---|---|
| Allure raw results (replaced on every run) | `allure-results/` |
| Allure HTML report (one file) | `allure-report/index.html` |
| Text log: steps (INFO) and page actions (DEBUG) | `logs/tests.log` (with `pytest-xdist`: `logs/tests-gw0.log`, ... one per worker) |
| Screenshot and trace of a failed test (one of each per browser context) | `test-results/`, and both are attached in Allure |

The log file has one block per test: a header, the steps (INFO), the page actions under each step
(DEBUG, indented), and the result:

```
17:02:01 INFO  ==================== test_e2e/test_add_todo.py::TestAddTodo::test_add_todo_english_text_is_listed[chromium]
17:02:03 INFO  Open the TodoMVC app
17:02:03 DEBUG    Navigate to './'
17:02:03 INFO  Add todo 'Buy milk'
17:02:03 DEBUG    Fill the new todo input with 'Buy milk' and press Enter
17:02:03 INFO  Expect the visible todos to be exactly: 'Buy milk'
17:02:03 INFO  -------------------- PASSED in 1.5 s
```

When a test does not pass, the result line gives the reason, at ERROR level for failures and errors:

| Outcome | Result line |
|---|---|
| Passed | `INFO  -------------------- PASSED in 1.5 s` |
| Check failed | `ERROR -------------------- FAILED in 5.2 s: AssertionError: Locator expected to have text ...` |
| Setup failed (pytest: error) | `ERROR -------------------- ERROR in setup: RuntimeError: ...` |
| Test passed, cleanup failed | `PASSED` line, then `ERROR -------------------- TEARDOWN FAILED: RuntimeError: ...` |
| Skipped | `INFO  -------------------- SKIPPED: <reason>` |
| Expected failure (`xfail`) | `INFO  -------------------- XFAIL (expected failure): <reason>` |

Each output has its own log level. A level shows itself and everything above it:

| Output | Default | Change it with |
|---|---|---|
| Log file `logs/tests.log` | DEBUG | `--log-file-level=INFO` |
| Log printed in the terminal for a failed test | DEBUG | `--log-level=INFO` |
| Live console | off | `-o log_cli=true --log-cli-level=INFO` (or `DEBUG`) |

Build the Allure report after a test run with [Allure 3](https://allurereport.org/docs/v3/), which runs on Node.js.
`npx` downloads it on first use:

```powershell
npx -y allure@3.22.1 generate allure-results
```

Then open `allure-report/index.html` by double-clicking it. It is a single file, so no server is needed.
The report name and the single-file setting are in `allurerc.json`.

In the report, tests are grouped by browser and then by feature (Add / Complete / Delete / Filter todos,
Input edge cases, Persistence), set with `groupBy` in `allurerc.json`. Each test has a readable title, and
tests that need more explanation also have a description. The 7 required tests are marked critical, so you can
filter on them. Every step is listed, for example "Add todo 'Buy milk'", and the step that failed is marked red.
A failed test has a screenshot and the Playwright trace attached.

Open a Playwright trace locally with `python -m playwright show-trace test-results/<test>/trace.zip`,
or upload the `trace.zip` from the report to https://trace.playwright.dev.
