"""Proofs that our checks can fail: each test breaks the app (or our code) on purpose and expects the check to fail.

Not part of the normal run: pyproject.toml sets testpaths = ["test_e2e"]. Run them with: python -m pytest proofs
These tests touch the Playwright page directly, because breaking the app is their job.
"""

import allure
import pytest
from playwright.sync_api import Page

from lib.keywords.todo_keywords import TodoKeywords
from lib.pom.page_todo import TodoPage
from lib.utils.constants.todo_view import TodoView


@allure.feature("Proofs: checks can fail")
class TestChecksCanFail:
    def test_delete_that_does_nothing_is_caught(self, todo_app: TodoKeywords, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])
        monkeypatch.setattr(TodoPage, "delete_todo", lambda self, title, nth=None: None)

        # When
        todo_app.delete_todo("Buy milk")

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todos(["Walk dog"])

    def test_untrimmed_title_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todo("padded")

        # When
        page.get_by_test_id("todo-title").evaluate("label => label.textContent = '   padded   '")

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todos(["padded"])

    def test_title_rendered_as_html_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todo("<b>bold</b>")

        # When
        page.get_by_test_id("todo-title").evaluate("label => label.innerHTML = '<b>bold</b>'")

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_titles_are_plain_text()

    @pytest.mark.parametrize(
        "css",
        [
            pytest.param("[data-testid=todo-title] { white-space: nowrap !important; }", id="nowrap"),
            pytest.param("[data-testid=todo-title] { width: max-content !important; }", id="max-content"),
        ],
    )
    def test_title_that_does_not_wrap_is_caught(self, todo_app: TodoKeywords, page: Page, css: str) -> None:
        # Given
        todo_app.add_todo("x" * 300)

        # When
        page.add_style_tag(content=css)

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todo_title_fits_in_list("x" * 300)

    def test_wrong_duplicate_completed_is_caught(self, todo_app: TodoKeywords, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Buy milk"])
        monkeypatch.setattr(
            TodoPage, "complete_todo", lambda self, title, nth=None: self.completed_checkbox(title, 0).check()
        )

        # When
        todo_app.complete_todo("Buy milk", nth=1)

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todo_completed("Buy milk", nth=1)

    def test_wrong_view_url_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todo("Buy milk")
        todo_app.open_view(TodoView.ACTIVE)

        # When
        page.evaluate("history.replaceState(null, '', '#/completed')")

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_view_opened(TodoView.ACTIVE)

    def test_todo_not_crossed_out_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todo("Buy milk")
        todo_app.complete_todo("Buy milk")

        # When
        page.get_by_test_id("todo-item").evaluate("item => item.classList.remove('completed')")

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todo_completed("Buy milk")

    def test_app_that_does_not_save_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])

        # When
        page.evaluate("localStorage.clear()")
        todo_app.reload_app()

        # Then
        with pytest.raises(AssertionError):
            todo_app.expect_todos(["Buy milk", "Walk dog"])

    def test_shared_storage_between_sessions_is_caught(self, todo_app: TodoKeywords, page: Page) -> None:
        # Given
        todo_app.add_todo("Buy milk")
        same_session_app = TodoKeywords(TodoPage(page.context.new_page()))  # same context = same storage

        # When
        same_session_app.open_todo_app()
        same_session_app.add_todo("Walk dog")

        # Then
        with pytest.raises(AssertionError):
            same_session_app.expect_todos(["Walk dog"])
