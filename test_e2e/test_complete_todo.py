import allure

from lib.keywords.todo_keywords import TodoKeywords
from lib.utils.constants.todo_view import TodoView


@allure.feature("Complete a todo")
class TestCompleteTodo:
    @allure.title("A completed todo appears in the Completed view")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_todo_appears_in_completed_view(self, todo_app: TodoKeywords) -> None:
        """Requirement: a todo item can be marked as completed and appears correctly in the "Completed" view
        (URL #/completed, only that todo listed, checkbox checked and shown crossed out)."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])

        # When
        todo_app.complete_todo("Buy milk")
        todo_app.open_view(TodoView.COMPLETED)

        # Then
        todo_app.expect_view_opened(TodoView.COMPLETED)
        todo_app.expect_todos(["Buy milk"])
        todo_app.expect_todo_completed("Buy milk")

    @allure.title("A completed todo stays in the All view, checked")
    def test_complete_todo_stays_in_all_view_as_completed(self, todo_app: TodoKeywords) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])

        # When
        todo_app.complete_todo("Buy milk")

        # Then
        todo_app.expect_todos(["Buy milk", "Walk dog"])
        todo_app.expect_todo_completed("Buy milk")

    @allure.title("A completed todo is not in the Active view")
    def test_complete_todo_is_not_in_active_view(self, todo_app: TodoKeywords) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])

        # When
        todo_app.complete_todo("Buy milk")
        todo_app.open_view(TodoView.ACTIVE)

        # Then
        todo_app.expect_todos(["Walk dog"])

    @allure.title("Un-completing a todo returns it to the Active view")
    def test_complete_todo_unchecked_todo_returns_to_active_view(self, todo_app: TodoKeywords) -> None:
        """Two todos are completed and only one is un-completed, so the Active list differs from the All list.
        Otherwise the check could pass on the All list, before the view has switched."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Buy milk")
        todo_app.complete_todo("Walk dog")

        # When
        todo_app.uncomplete_todo("Buy milk")
        todo_app.open_view(TodoView.ACTIVE)

        # Then
        todo_app.expect_todos(["Buy milk", "Pay rent"])

    @allure.title("Completing a todo decreases the items-left counter")
    def test_complete_todo_counter_decreases_by_one(self, todo_app: TodoKeywords) -> None:
        """The counter counts active todos only (and uses the singular "1 item left")."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])

        # When
        todo_app.complete_todo("Buy milk")

        # Then
        todo_app.expect_items_left(1)
