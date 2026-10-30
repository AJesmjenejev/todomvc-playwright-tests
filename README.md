# TodoMVC Playwright tests (Python)

[![Tests](https://github.com/AJesmjenejev/todomvc-playwright-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/AJesmjenejev/todomvc-playwright-tests/actions/workflows/tests.yml)

Automated end-to-end tests for https://demo.playwright.dev/todomvc/#/
using Playwright, pytest and the Python synchronous API.

Latest test report (Chromium, Firefox, WebKit): https://ajesmjenejev.github.io/todomvc-playwright-tests/

## How to run the tests

Needs Python 3.12 or newer and internet access. Windows (PowerShell):

```powershell
git clone https://github.com/AJesmjenejev/todomvc-playwright-tests.git
cd todomvc-playwright-tests
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux: use `python3 -m venv .venv`, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`,
and install the browser with `playwright install --with-deps chromium`.

Other ways to run (replace `python` with the venv's Python above):

```powershell
python -m pytest --headed                     # watch the browser
python -m pytest test_e2e/test_filters.py     # one file (or: -k test_filter_active)
python -m playwright install firefox webkit   # then:
python -m pytest --browser chromium --browser firefox --browser webkit
python -m pytest -n 3                         # in parallel
```

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

Extra tests cover blank input, trimming, the counter, filters by URL and Back / Forward, deleting the last todo,
HTML input, a long title, duplicate titles and persistence. In total: 43 tests.

## How it is built

Tests call keywords (`lib/keywords/todo_keywords.py`), keywords call page objects (`lib/pom/page_todo.py`),
and only page objects hold locators. Locators use roles, placeholders and test IDs, with no sleeps.
Checks compare the visible list exactly. `proofs/` breaks the app on purpose to show that the checks can fail.

More details:

- [docs/test-approach.md](docs/test-approach.md): how the cases were chosen, the proofs, scope, risks, design notes, project layout.
- [docs/reports-and-logs.md](docs/reports-and-logs.md): Allure report, logs and traces.
- [docs/ci-and-code-quality.md](docs/ci-and-code-quality.md): GitHub Actions, linters and type checks.

## License

MIT. See [LICENSE](LICENSE).
