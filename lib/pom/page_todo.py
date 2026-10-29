from playwright.sync_api import Locator, Page

from lib.pom.page_base import BasePage
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import TestLogger as log
from lib.utils.text import exact_text


class TodoPage(BasePage):
    PATH = "./"  # relative to base_url

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.new_todo_input = self.pw_page.get_by_placeholder("What needs to be done?")
        self.todo_items = self.pw_page.get_by_test_id("todo-item")
        self.todo_titles_lbl = self.pw_page.get_by_test_id("todo-title")
        self.items_left_lbl = self.pw_page.get_by_test_id("todo-count")

    def todo_title_lbl(self, title: str) -> Locator:
        return self.todo_titles_lbl.filter(has_text=exact_text(title))

    def todo_item(self, title: str) -> Locator:
        return self.todo_items.filter(has=self.todo_title_lbl(title))

    def completed_checkbox(self, title: str) -> Locator:
        return self.todo_item(title).get_by_role("checkbox")

    def delete_btn(self, title: str) -> Locator:
        return self.todo_item(title).get_by_role("button", name="Delete")

    def view_link(self, view: TodoView) -> Locator:
        return self.pw_page.get_by_role("link", name=view, exact=True)

    def add_todo(self, title: str) -> None:
        log.debug(f"Fill the new todo input with '{title}' and press Enter")
        self.new_todo_input.fill(title)
        self.new_todo_input.press("Enter")

    def complete_todo(self, title: str) -> None:
        log.debug(f"Check the checkbox of '{title}'")
        self.completed_checkbox(title).check()

    def uncomplete_todo(self, title: str) -> None:
        log.debug(f"Uncheck the checkbox of '{title}'")
        self.completed_checkbox(title).uncheck()

    def delete_todo(self, title: str) -> None:
        log.debug(f"Hover '{title}' and click its Delete button")
        self.todo_item(title).hover()  # the Delete button is only shown on hover
        self.delete_btn(title).click()

    def open_view(self, view: TodoView) -> None:
        log.debug(f"Click the '{view}' filter link")
        self.view_link(view).click()
