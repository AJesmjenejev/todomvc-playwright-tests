# Test approach

Back to the [README](../README.md).

The tests cover the 7 requirements of the task and check what the user sees on the page.
Extra tests cover blank input, trimming, un-completing a todo, the "All" view, filters opened by their URL and with
Back / Forward, the items-left counter (which counts active todos in every view, and after a delete), the input
being cleared after an add, deleting the last todo (the list and the footer hide), HTML/script input, a very long
title, duplicate titles, and persistence (a reload keeps the todos, their state and the selected filter;
a new browser session starts empty).

## How the cases were chosen

- Titles: English first, then one example of each kind of text: Latin with diacritics (Czech), Cyrillic,
  Japanese, right-to-left Arabic, emoji, and digits in three positions.
- Boundaries: empty and spaces-only titles must be ignored, spaces around a title must be trimmed,
  and a 300-character word without spaces must wrap inside the list.
- States and views: a todo is either active or completed, and there are three views (All, Active, Completed).
  The filter and delete tests use both states, so each view shows some todos and hides others.
- HTML input: HTML and an `onerror` script in a title must be shown as plain text (an XSS check).

## How the checks avoid false passes

- The visible list is compared exactly, text and order, so anything extra, missing or untrimmed fails.
- A deleted todo is checked through the exact remaining list. That also proves the view rendered.
- The delete test removes one active and one completed todo, so each view showed one of them before the delete.
- "Hidden" checks come after a positive check. The last-todo test checks the counter before the delete,
  and the input test checks the list first, so neither can pass on an empty page.
- Where the expected list equals the list of the previous view, a check could pass before the view switches.
  Such tests are set up so the expected list is different (see the un-complete test).
- A reload is verified: a flag set on `window` must be gone afterwards. Otherwise a reload that did nothing
  would pass the persistence tests, because the page already shows the right data.
- Each row below is one test in `proofs/`. It breaks the app (or our code) on purpose and expects the real check to fail.

| Break | How it is broken | Check that catches it |
|---|---|---|
| Delete does nothing | `monkeypatch.setattr(TodoPage, "delete_todo", ...)` (a no-op) | `expect_todos` (exact remaining list) |
| Footer stays after the last delete | the same no-op delete, with one todo | `expect_list_and_footer_hidden` |
| Input not cleared after an add | `fill("leftover")` after the add | `expect_new_todo_input_empty` |
| Title not trimmed | `label.evaluate("label => label.textContent = '   padded   '")` | `expect_todos` (exact text) |
| Title rendered as HTML | `label.evaluate("label => label.innerHTML = '<b>bold</b>'")` | `expect_titles_are_plain_text` |
| Long title does not wrap | `page.add_style_tag(...)` with `white-space: nowrap` or `width: max-content` | `expect_todo_title_fits_in_list` (the message shows where the text and the item are) |
| Wrong duplicate completed | `monkeypatch.setattr(TodoPage, "complete_todo", ...)` (always the first) | `expect_todo_completed(..., nth=1)` |
| Wrong duplicate deleted | `monkeypatch.setattr(TodoPage, "delete_todo", ...)` (deletes the second, not the first) | `expect_todo_completed(...)` (the one left must be the completed one) |
| Wrong view URL | `page.evaluate("history.replaceState(null, '', '#/completed')")` | `expect_view_opened` |
| Completed todo not crossed out | `page.add_style_tag(...)` with `text-decoration: none` | `expect_todo_completed` (the title must have `line-through`) |
| App does not save | `page.evaluate("localStorage.clear()")` before the reload | `expect_todos` after reload |
| Reload does nothing | `monkeypatch.setattr(Page, "reload", ...)` (a no-op) | `reload_app` (a flag set on `window` must be gone) |
| Sessions share storage | a second page in the same context, where a new context should be used | `expect_todos` in the second session |

Run the proofs with `python -m pytest proofs`. They take about a minute, because each failing check waits for its timeout.
The normal run skips them: `pyproject.toml` sets `testpaths = ["test_e2e"]`.

## Out of scope

| Not tested | Why |
|---|---|
| Editing a todo (double-click, Enter, Escape) | Not in the 7 requirements; the next feature I would add |
| "Mark all as complete", "Clear completed" | Not in the requirements |
| Accessibility, visual layout, performance | Need other tools (axe-core, screenshot diffs, load tools) |
| Cross-tab sync | The demo does not claim to support it |

## Risks and limits

- The tests use a public demo site. If it is down or changes, the tests fail in setup. If every test fails in setup,
  the site is probably unreachable.
- Exact text checks are strict on purpose. A harmless text change (for example in the counter wording) fails a test.
- Every test starts with a fresh browser context, so tests share no data and can run in parallel.
  `pytest-xdist` is installed with `requirements.txt` but is not used by default: `python -m pytest -n 3` runs
  the tests in 3 workers (all tests passed). CI uses it per browser (see
  [ci-and-code-quality.md](ci-and-code-quality.md)). `conftest.py` gives each worker its own log file
  (`logs/tests-gw0.log`, ...), named from the `PYTEST_XDIST_WORKER` environment variable.
  Then `logs/tests.log` holds only the header and result lines (its times are not exact).
  The suite takes about 25 seconds in one process and about 10 seconds with `-n 3` (Chromium, local machine).
- One timeout, 5 seconds by default, is used by `expect`, by page actions (click, fill, check) and by the waits
  in the page objects. A wrong locator fails after 5 seconds, not after Playwright's default of 30.
  Page loads keep 30 seconds, because the public site can be slow to open.
  Both values are in `lib/utils/constants/timeouts.py`. On a slow machine or network,
  set `TODO_TIMEOUT_MS` (milliseconds) instead of editing the code.

## How I would extend it

1. Editing, then "Clear completed" and "Mark all as complete".
2. An accessibility scan (axe-core) and a few visual snapshots.

## Design notes

- Tests call keywords, keywords call page objects, and only page objects hold locators and touch the
  Playwright `Page`. If the site changes, you fix one page object. The URL check needs the `Page`, so
  `TodoPage.wait_for_view_url` waits for the `#/...` route (defined once on `TodoView`) and the keyword
  asserts the result.
- Locators use roles, placeholders and test IDs. There are no CSS selectors and no `sleep()` calls.
- Todos are found by exact title. When several todos have the same title, pass `nth` (0 = first) to pick one.
  Without `nth`, a duplicate title stops the test with Playwright's strict-mode error.
- `expect(...)` retries until the UI reaches the expected state. The layout check (long title) has no
  `expect` matcher, so the page object uses `wait_for_function`, which re-runs a small JS check in the
  browser until the text is inside its todo item or the timeout passes.
- Every test has `# When` and `# Then` comments, plus `# Given` when there is setup. A linter checks them.
- Keyword methods have `@allure.step(...)` and a matching log line. Test classes have `@allure.feature`,
  and tests have `@allure.title`. The 7 required tests are marked critical, and a docstring becomes the
  Allure description where a test needs one.
- Each test gets a new browser context, so `localStorage` starts empty and tests can run in any order.

## Project layout

```
test_e2e/                    Test classes, one file per topic (add, complete, delete, filters, input edge cases, persistence)
proofs/                      Tests that break the app on purpose to prove the checks can fail (not in the normal run)
lib/
  keywords/todo_keywords.py  Business actions and expect_* checks (@allure.step + log)
  pom/page_base.py           BasePage: PATH, goto(), reload() (checks that it really reloaded), go_back(), go_forward()
  pom/page_todo.py           TodoPage: locators (suffix names: _input, _lbl, _btn, _checkbox, _link) and actions
  utils/logger.py            Log (info / error / debug)
  utils/log_results.py       pytest plugin: a header and a result line per test in the log
  utils/text.py              exact_text(): exact text matching; quoted() and which(): readable titles for messages
  utils/constants/           TodoView StrEnum (All, Active, Completed); the timeouts
tools/aaa_structure_linter.py  Checks the Given / When / Then comments
docs/                        Test approach, reports and logs, CI and code quality
conftest.py                  Fixtures, the timeouts, one log file per worker; attaches screenshot and trace to Allure on failure
pyproject.toml               pytest, ruff and mypy settings
allurerc.json                Allure 3 report settings
.github/workflows/tests.yml  CI: lint, tests in 3 browsers, Python 3.14, proofs, Allure report, GitHub Pages
```
