import allure
import pytest

from lib.keywords.todo_keywords import TodoKeywords
from lib.utils.constants.todo_view import TodoView


@allure.feature("Delete a todo")
class TestDeleteTodo:
    @allure.title("Deleted todos are gone from the {view} view")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        ("view", "remaining"),
        [
            pytest.param(TodoView.ALL, ["Walk dog", "Call mom"], id="all"),
            pytest.param(TodoView.ACTIVE, ["Walk dog"], id="active"),
            pytest.param(TodoView.COMPLETED, ["Call mom"], id="completed"),
        ],
    )
    def test_delete_todo_is_gone_from_every_view(
        self, todo_app: TodoKeywords, view: TodoView, remaining: list[str]
    ) -> None:
        """Requirement: a todo item can be deleted and no longer appears in any view.
        One active and one completed todo are deleted, so every view showed one of them before."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent", "Call mom"])
        todo_app.complete_todo("Pay rent")
        todo_app.complete_todo("Call mom")

        # When
        todo_app.delete_todo("Buy milk")
        todo_app.delete_todo("Pay rent")
        todo_app.open_view(view)

        # Then
        todo_app.expect_todos(remaining)
