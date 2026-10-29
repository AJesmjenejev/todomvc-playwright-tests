import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from lib.pom.page_base import BasePage
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import TestLogger as log
from lib.utils.text import exact_text, which

# True when the rendered text of the label (not only the label box) is inside its todo item, left and right.
_TEXT_INSIDE_ITEM_JS = """([label, item]) => {
    const text = document.createRange();
    text.selectNodeContents(label);
    const t = text.getBoundingClientRect();
    const i = item.getBoundingClientRect();
    return t.left >= i.left && t.right <= i.right;
}"""


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

    def todo_item(self, title: str, nth: int | None = None) -> Locator:
        # nth picks one of several todos with the same title (0 = first). Without it, a duplicate is an error.
        items = self.todo_items.filter(has=self.todo_title_lbl(title))
        return items if nth is None else items.nth(nth)

    def completed_checkbox(self, title: str, nth: int | None = None) -> Locator:
        return self.todo_item(title, nth).get_by_role("checkbox")

    def delete_btn(self, title: str, nth: int | None = None) -> Locator:
        return self.todo_item(title, nth).get_by_role("button", name="Delete")

    def view_link(self, view: TodoView) -> Locator:
        return self.pw_page.get_by_role("link", name=view, exact=True)

    def title_text_stays_inside_item(self, title: str, timeout: float = 5_000) -> bool:
        # The sync API has no expect.poll: wait_for_function re-runs the check in the browser until it is true.
        label = self.todo_title_lbl(title).element_handle()
        item = self.todo_item(title).element_handle()
        try:
            self.pw_page.wait_for_function(_TEXT_INSIDE_ITEM_JS, arg=[label, item], timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    @property
    def current_url(self) -> str:
        return self.pw_page.url

    def wait_for_view_url(self, view: TodoView, timeout: float = 5_000) -> bool:
        # Retries like expect: waits until the URL ends with the view's route (only the #/... part).
        try:
            self.pw_page.wait_for_url(re.compile(rf"{re.escape(view.route)}$"), timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def add_todo(self, title: str) -> None:
        log.debug(f"Fill the new todo input with '{title}' and press Enter")
        self.new_todo_input.fill(title)
        self.new_todo_input.press("Enter")

    def complete_todo(self, title: str, nth: int | None = None) -> None:
        log.debug(f"Check the checkbox of {which(title, nth)}")
        self.completed_checkbox(title, nth).check()

    def uncomplete_todo(self, title: str, nth: int | None = None) -> None:
        log.debug(f"Uncheck the checkbox of {which(title, nth)}")
        self.completed_checkbox(title, nth).uncheck()

    def delete_todo(self, title: str, nth: int | None = None) -> None:
        log.debug(f"Hover {which(title, nth)} and click its Delete button")
        self.todo_item(title, nth).hover()  # the Delete button is only shown on hover
        self.delete_btn(title, nth).click()

    def open_view(self, view: TodoView) -> None:
        log.debug(f"Click the '{view}' filter link")
        self.view_link(view).click()
