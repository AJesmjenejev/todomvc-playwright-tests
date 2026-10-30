import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from lib.pom.page_base import BasePage
from lib.utils.constants.timeouts import CHECK_TIMEOUT_MS
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import Log as log
from lib.utils.text import exact_text, which

_LAYOUT_SETTLED_JS = """async () => {
    await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}"""

# True when the rendered text of the label (not only the label box) is inside its todo item, left and right.
# A detached element or a box without size has no layout at all (all zeros), so it must not count as "inside".
# Not async on purpose: wait_for_function does not await a Promise, it treats the Promise itself as true.
_TEXT_INSIDE_ITEM_JS = """([label, item]) => {
    if (!label.isConnected || !item.isConnected) return false;
    const text = document.createRange();
    text.selectNodeContents(label);
    const t = text.getBoundingClientRect();
    const i = item.getBoundingClientRect();
    return t.width > 0 && i.width > 0 && t.left >= i.left && t.right <= i.right;
}"""

# The same two boxes as text, for the error message: "text x 249..717, item x 189..739" (left..right, in pixels).
_TEXT_POSITION_JS = """([label, item]) => {
    const text = document.createRange();
    text.selectNodeContents(label);
    const t = text.getBoundingClientRect();
    const i = item.getBoundingClientRect();
    return `text x ${Math.round(t.left)}..${Math.round(t.right)}, item x ${Math.round(i.left)}..${Math.round(i.right)}`;
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

    def todo_item_title_lbl(self, title: str, nth: int | None = None) -> Locator:
        return self.todo_item(title, nth).locator(self.todo_titles_lbl)

    def completed_checkbox(self, title: str, nth: int | None = None) -> Locator:
        return self.todo_item(title, nth).get_by_role("checkbox")

    def delete_btn(self, title: str, nth: int | None = None) -> Locator:
        return self.todo_item(title, nth).get_by_role("button", name="Delete")

    def view_link(self, view: TodoView) -> Locator:
        return self.pw_page.get_by_role("link", name=view, exact=True)

    def title_text_stays_inside_item(
        self, title: str, nth: int | None = None, timeout: float = CHECK_TIMEOUT_MS
    ) -> bool:
        # The sync API has no expect.poll: wait_for_function re-runs the check in the browser until it is true.
        item_locator = self.todo_item(title, nth)
        label = item_locator.locator(self.todo_titles_lbl).element_handle()
        item = item_locator.element_handle()
        try:
            # evaluate (unlike wait_for_function) waits for the promise: fonts and two paint frames, so a layout
            # that is still settling does not pass by luck.
            self.pw_page.evaluate(_LAYOUT_SETTLED_JS)
            self.pw_page.wait_for_function(_TEXT_INSIDE_ITEM_JS, arg=[label, item], timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
        finally:
            label.dispose()
            item.dispose()

    def title_text_position(self, title: str, nth: int | None = None) -> str:
        item_locator = self.todo_item(title, nth)
        label = item_locator.locator(self.todo_titles_lbl).element_handle()
        item = item_locator.element_handle()
        try:
            return str(self.pw_page.evaluate(_TEXT_POSITION_JS, [label, item]))
        finally:
            label.dispose()
            item.dispose()

    @property
    def current_url(self) -> str:
        return self.pw_page.url

    def wait_for_view_url(self, view: TodoView, timeout: float = CHECK_TIMEOUT_MS) -> bool:
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

    def goto_view(self, view: TodoView) -> None:
        log.debug(f"Navigate to the '{view}' route '{view.route}'")
        self.pw_page.goto(f"{self.PATH}{view.route}")
