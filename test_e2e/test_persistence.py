import allure

from lib.keywords.todo_keywords import TodoKeywords
from lib.utils.constants.todo_view import TodoView


@allure.feature("Persistence")
class TestPersistence:
    @allure.title("Todos and their completed state survive a page reload")
    def test_persistence_reload_keeps_todos_and_state(self, todo_app: TodoKeywords) -> None:
        """The app saves todos in the browser (localStorage). After a reload the list, the completed state
        and the counter must be the same as before."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")

        # When
        todo_app.reload_app()

        # Then
        todo_app.expect_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.expect_todo_completed("Walk dog")
        todo_app.expect_items_left(2)

    @allure.title("The selected filter survives a page reload")
    def test_persistence_reload_keeps_selected_filter(self, todo_app: TodoKeywords) -> None:
        """The filter is part of the URL (#/active), so a reload must keep the same view and the same todos."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")
        todo_app.open_view(TodoView.ACTIVE)

        # When
        todo_app.reload_app()

        # Then
        todo_app.expect_view_opened(TodoView.ACTIVE)
        todo_app.expect_todos(["Buy milk", "Pay rent"])

    @allure.title("A new browser session starts with an empty list")
    def test_persistence_new_browser_context_starts_empty(
        self, todo_app: TodoKeywords, fresh_todo_app: TodoKeywords
    ) -> None:
        """Data is stored per browser profile. A separate browser context must not see todos from another one."""
        # Given
        todo_app.add_todo("Buy milk")
        todo_app.expect_todos(["Buy milk"])

        # When
        fresh_todo_app.open_todo_app()
        fresh_todo_app.add_todo("Walk dog")  # a real todo, so an empty page cannot pass by accident

        # Then
        fresh_todo_app.expect_todos(["Walk dog"])
