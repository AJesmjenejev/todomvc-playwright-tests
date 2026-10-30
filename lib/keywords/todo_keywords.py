import allure
from playwright.sync_api import expect

from lib.pom.page_todo import TodoPage
from lib.utils.constants.todo_view import TodoView
from lib.utils.logger import Log as log
from lib.utils.text import exact_text, quoted, which


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
        if not self.todo_page.reload():  # not `assert`: python -O would remove it
            raise AssertionError("The page did not reload, so the persistence checks would prove nothing")

    @allure.step("Add todo {title}")
    def add_todo(self, title: str) -> None:
        log.info(f"Add todo '{title}'")
        self.todo_page.add_todo(title)

    def add_todos(self, titles: list[str]) -> None:
        with allure.step(f"Add todos {quoted(titles)}"):
            for title in titles:
                self.add_todo(title)

    # `with allure.step(...)`, not the decorator: only this way the step can show which duplicate (nth) is meant.
    def complete_todo(self, title: str, nth: int | None = None) -> None:
        message = f"Complete todo {which(title, nth)}"
        with allure.step(message):
            log.info(message)
            self.todo_page.complete_todo(title, nth)

    def uncomplete_todo(self, title: str, nth: int | None = None) -> None:
        message = f"Mark todo {which(title, nth)} as not completed"
        with allure.step(message):
            log.info(message)
            self.todo_page.uncomplete_todo(title, nth)

    def delete_todo(self, title: str, nth: int | None = None) -> None:
        message = f"Delete todo {which(title, nth)}"
        with allure.step(message):
            log.info(message)
            self.todo_page.delete_todo(title, nth)

    @allure.step("Open the {view} view")
    def open_view(self, view: TodoView) -> None:
        log.info(f"Open the '{view}' view")
        self.todo_page.open_view(view)

    @allure.step("Open the {view} view by its URL")
    def open_view_by_url(self, view: TodoView) -> None:
        log.info(f"Open the '{view}' view by its URL")
        self.todo_page.goto_view(view)

    @allure.step("Go back in the browser history")
    def go_back(self) -> None:
        log.info("Go back in the browser history")
        self.todo_page.go_back()

    @allure.step("Go forward in the browser history")
    def go_forward(self) -> None:
        log.info("Go forward in the browser history")
        self.todo_page.go_forward()

    def expect_todos(self, titles: list[str]) -> None:
        message = f"Expect the visible todos to be exactly: {quoted(titles)}"
        with allure.step(message):
            log.info(message)
            expect(self.todo_page.todo_titles_lbl).to_have_text([exact_text(title) for title in titles])

    def expect_todo_completed(self, title: str, nth: int | None = None) -> None:
        message = f"Expect todo {which(title, nth)} to be completed"
        with allure.step(message):
            log.info(message)
            expect(self.todo_page.completed_checkbox(title, nth)).to_be_checked()
            # What the user sees: a completed todo is crossed out (not the name of a CSS class).
            expect(self.todo_page.todo_item_title_lbl(title, nth)).to_have_css("text-decoration-line", "line-through")

    @allure.step("Expect the new todo input to be empty")
    def expect_new_todo_input_empty(self) -> None:
        log.info("Expect the new todo input to be empty")
        expect(self.todo_page.new_todo_input).to_have_value("")

    @allure.step("Expect the todo list and the footer to be hidden")
    def expect_list_and_footer_hidden(self) -> None:
        log.info("Expect the todo list and the footer to be hidden")
        expect(self.todo_page.todo_items).to_have_count(0)
        expect(self.todo_page.items_left_lbl).to_be_hidden()
        expect(self.todo_page.view_link(TodoView.ALL)).to_be_hidden()

    @allure.step("Expect the counter to show {count} left")
    def expect_items_left(self, count: int) -> None:
        log.info(f"Expect the counter to show {count} left")
        text = f"{count} item left" if count == 1 else f"{count} items left"
        expect(self.todo_page.items_left_lbl).to_have_text(exact_text(text))

    @allure.step("Expect the URL to show the {view} view")
    def expect_view_opened(self, view: TodoView) -> None:
        log.info(f"Expect the URL to show the '{view}' view")
        if not self.todo_page.wait_for_view_url(view):  # not `assert`: python -O would remove it
            raise AssertionError(f"URL should end with '{view.route}' but is '{self.todo_page.current_url}'")

    @allure.step("Expect todo titles to contain no HTML elements")
    def expect_titles_are_plain_text(self) -> None:
        log.info("Expect todo titles to contain no HTML elements")
        # Without a visible title there is nothing to inspect, and "no child elements" would pass on an empty page.
        expect(self.todo_page.todo_titles_lbl.first).to_be_visible()
        # Any child element inside a title label means the input was rendered as HTML.
        expect(self.todo_page.todo_titles_lbl.locator("*")).to_have_count(0)

    def expect_todo_title_fits_in_list(self, title: str, nth: int | None = None) -> None:
        message = f"Expect the todo title ({len(title)} characters) to fit inside the list"
        with allure.step(message):
            log.info(message)
            if not self.todo_page.title_text_stays_inside_item(title, nth):
                position = self.todo_page.title_text_position(title, nth)
                raise AssertionError(f"The todo title sticks out of the list: it does not wrap ({position})")
