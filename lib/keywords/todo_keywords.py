import re

import allure
from playwright.sync_api import expect

from lib.pom.page_todo import TodoPage
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import TestLogger as log
from lib.utils.text import exact_text


def _quoted(titles: list[str]) -> str:
    # Readable list for step titles; a Python list would show 'Jerry\'s' with a backslash.
    return ", ".join(f"'{title}'" for title in titles) or "nothing"


class TodoKeywords:
    def __init__(self, page: TodoPage) -> None:
        self.page = page

    @allure.step("Open the TodoMVC app")
    def open_todo_app(self) -> None:
        log.info("Open the TodoMVC app")
        self.page.goto()

    @allure.step("Reload the page")
    def reload_app(self) -> None:
        log.info("Reload the page")
        self.page.reload()

    @allure.step("Add todo {title}")
    def add_todo(self, title: str) -> None:
        log.info(f"Add todo '{title}'")
        self.page.add_todo(title)

    def add_todos(self, titles: list[str]) -> None:
        with allure.step(f"Add todos {_quoted(titles)}"):
            for title in titles:
                self.add_todo(title)

    @allure.step("Complete todo {title}")
    def complete_todo(self, title: str) -> None:
        log.info(f"Complete todo '{title}'")
        self.page.complete_todo(title)

    @allure.step("Mark todo {title} as not completed")
    def uncomplete_todo(self, title: str) -> None:
        log.info(f"Mark todo '{title}' as not completed")
        self.page.uncomplete_todo(title)

    @allure.step("Delete todo {title}")
    def delete_todo(self, title: str) -> None:
        log.info(f"Delete todo '{title}'")
        self.page.delete_todo(title)

    @allure.step("Open the {view} view")
    def open_view(self, view: TodoView) -> None:
        log.info(f"Open the '{view}' view")
        self.page.open_view(view)

    def expect_todos(self, titles: list[str]) -> None:
        message = f"Expect the visible todos to be exactly: {_quoted(titles)}"
        with allure.step(message):
            log.info(message)
            expect(self.page.todo_titles_lbl).to_have_text([exact_text(title) for title in titles])

    @allure.step("Expect todo {title} to be completed")
    def expect_todo_completed(self, title: str) -> None:
        log.info(f"Expect todo '{title}' to be completed")
        expect(self.page.completed_checkbox(title)).to_be_checked()

    @allure.step("Expect the counter to show {count} left")
    def expect_items_left(self, count: int) -> None:
        log.info(f"Expect the counter to show {count} left")
        text = f"{count} item left" if count == 1 else f"{count} items left"
        expect(self.page.items_left_lbl).to_have_text(exact_text(text))

    @allure.step("Expect the URL of the {view} view")
    def expect_view_opened(self, view: TodoView) -> None:
        log.info(f"Expect the URL of the '{view}' view")
        route = "" if view is TodoView.ALL else view.lower()
        expect(self.page.pw_page).to_have_url(re.compile(rf"/todomvc/#/{route}$"))

    @allure.step("Expect todo titles to contain no HTML elements")
    def expect_titles_are_plain_text(self) -> None:
        log.info("Expect todo titles to contain no HTML elements")
        # Any child element inside a title label means the input was rendered as HTML.
        expect(self.page.todo_titles_lbl.locator("*")).to_have_count(0)

    @allure.step("Expect todo title to fit inside the list")
    def expect_todo_title_fits_in_list(self, title: str) -> None:
        log.info(f"Expect todo title '{title[:20]}...' to fit inside the list")
        label = self.page.todo_title_lbl(title)
        overflows = label.evaluate("label => label.scrollWidth > label.clientWidth")
        assert not overflows, "The todo title is wider than the list: it does not wrap"
