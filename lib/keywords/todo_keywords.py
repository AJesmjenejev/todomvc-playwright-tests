import re

import allure
from playwright.sync_api import expect

from lib.pom.page_todo import TodoPage
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import TestLogger as log
from lib.utils.text import exact_text, which


def _quoted(titles: list[str]) -> str:
    # Readable list for step titles; a Python list would show 'Jerry\'s' with a backslash.
    return ", ".join(f"'{title}'" for title in titles) or "nothing"


class TodoKeywords:
    def __init__(self, todo_page: TodoPage) -> None:
        self.todo_page = todo_page

    @allure.step("Open the TodoMVC app")
    def open_todo_app(self) -> None:
        log.info("Open the TodoMVC app")
        self.todo_page.goto()

    @allure.step("Reload the page")
    def reload_app(self) -> None:
        log.info("Reload the page")
        self.todo_page.reload()

    @allure.step("Add todo {title}")
    def add_todo(self, title: str) -> None:
        log.info(f"Add todo '{title}'")
        self.todo_page.add_todo(title)

    def add_todos(self, titles: list[str]) -> None:
        with allure.step(f"Add todos {_quoted(titles)}"):
            for title in titles:
                self.add_todo(title)

    @allure.step("Complete todo {title}")
    def complete_todo(self, title: str, nth: int | None = None) -> None:
        log.info(f"Complete todo {which(title, nth)}")
        self.todo_page.complete_todo(title, nth)

    @allure.step("Mark todo {title} as not completed")
    def uncomplete_todo(self, title: str, nth: int | None = None) -> None:
        log.info(f"Mark todo {which(title, nth)} as not completed")
        self.todo_page.uncomplete_todo(title, nth)

    @allure.step("Delete todo {title}")
    def delete_todo(self, title: str, nth: int | None = None) -> None:
        log.info(f"Delete todo {which(title, nth)}")
        self.todo_page.delete_todo(title, nth)

    @allure.step("Open the {view} view")
    def open_view(self, view: TodoView) -> None:
        log.info(f"Open the '{view}' view")
        self.todo_page.open_view(view)

    def expect_todos(self, titles: list[str]) -> None:
        message = f"Expect the visible todos to be exactly: {_quoted(titles)}"
        with allure.step(message):
            log.info(message)
            expect(self.todo_page.todo_titles_lbl).to_have_text([exact_text(title) for title in titles])

    @allure.step("Expect todo {title} to be completed")
    def expect_todo_completed(self, title: str, nth: int | None = None) -> None:
        log.info(f"Expect todo {which(title, nth)} to be completed")
        expect(self.todo_page.completed_checkbox(title, nth)).to_be_checked()
        # What the user sees: the "completed" class makes the todo crossed out.
        expect(self.todo_page.todo_item(title, nth)).to_have_class(re.compile(r"\bcompleted\b"))

    @allure.step("Expect the counter to show {count} left")
    def expect_items_left(self, count: int) -> None:
        log.info(f"Expect the counter to show {count} left")
        text = f"{count} item left" if count == 1 else f"{count} items left"
        expect(self.todo_page.items_left_lbl).to_have_text(exact_text(text))

    @allure.step("Expect the URL of the {view} view")
    def expect_view_opened(self, view: TodoView) -> None:
        log.info(f"Expect the URL of the '{view}' view")
        url_matches = self.todo_page.wait_for_view_url(view)
        assert url_matches, f"URL should end with '{view.route}' but is '{self.todo_page.current_url}'"

    @allure.step("Expect todo titles to contain no HTML elements")
    def expect_titles_are_plain_text(self) -> None:
        log.info("Expect todo titles to contain no HTML elements")
        # Any child element inside a title label means the input was rendered as HTML.
        expect(self.todo_page.todo_titles_lbl.locator("*")).to_have_count(0)

    @allure.step("Expect todo title to fit inside the list")
    def expect_todo_title_fits_in_list(self, title: str) -> None:
        log.info(f"Expect todo title '{title[:20]}...' to fit inside the list")
        fits = self.todo_page.title_text_stays_inside_item(title)
        assert fits, "The todo title sticks out of the list: it does not wrap"
