import allure
import pytest

from lib.keywords.todo_keywords import TodoKeywords
from lib.utils.constants.todo_view import TodoView


@allure.feature("Filter todos")
class TestFilters:
    @allure.title("The Active filter shows only incomplete todos")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_filter_active_shows_only_incomplete_todos(self, todo_app: TodoKeywords) -> None:
        """Requirement: the "Active" filter correctly shows only items that are not completed."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")

        # When
        todo_app.open_view(TodoView.ACTIVE)

        # Then
        todo_app.expect_view_opened(TodoView.ACTIVE)
        todo_app.expect_todos(["Buy milk", "Pay rent"])

    @allure.title("The Completed filter shows only completed todos")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_filter_completed_shows_only_completed_todos(self, todo_app: TodoKeywords) -> None:
        """Requirement: the "Completed" filter correctly shows only items that have been marked as completed."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")
        todo_app.complete_todo("Pay rent")

        # When
        todo_app.open_view(TodoView.COMPLETED)

        # Then
        todo_app.expect_view_opened(TodoView.COMPLETED)
        todo_app.expect_todos(["Walk dog", "Pay rent"])

    @allure.title("The All filter shows every todo again")
    def test_filter_all_shows_every_todo(self, todo_app: TodoKeywords) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog"])
        todo_app.complete_todo("Walk dog")
        todo_app.open_view(TodoView.ACTIVE)

        # When
        todo_app.open_view(TodoView.ALL)

        # Then
        todo_app.expect_view_opened(TodoView.ALL)
        todo_app.expect_todos(["Buy milk", "Walk dog"])

    @allure.title("The counter counts active todos in the {view} view")
    @pytest.mark.parametrize(
        ("view", "visible"),
        [
            pytest.param(TodoView.ALL, ["Buy milk", "Walk dog", "Pay rent"], id="all"),
            pytest.param(TodoView.ACTIVE, ["Buy milk", "Pay rent"], id="active"),
            pytest.param(TodoView.COMPLETED, ["Walk dog"], id="completed"),
        ],
    )
    def test_filter_counter_counts_active_todos_in_every_view(
        self, todo_app: TodoKeywords, view: TodoView, visible: list[str]
    ) -> None:
        """The counter shows active todos in every view, not the number of visible todos.
        The visible list is checked too: the counter reads the same before the view has switched."""
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")

        # When
        todo_app.open_view(view)

        # Then
        todo_app.expect_todos(visible)
        todo_app.expect_items_left(2)

    @allure.title("A filter opened by its URL shows the matching todos: {view}")
    @pytest.mark.parametrize(
        ("view", "visible"),
        [
            pytest.param(TodoView.ACTIVE, ["Buy milk", "Pay rent"], id="active"),
            pytest.param(TodoView.COMPLETED, ["Walk dog"], id="completed"),
        ],
    )
    def test_filter_opened_by_url_shows_matching_todos(
        self, todo_app: TodoKeywords, view: TodoView, visible: list[str]
    ) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")

        # When
        todo_app.open_view_by_url(view)

        # Then
        todo_app.expect_view_opened(view)
        todo_app.expect_todos(visible)

    @allure.title("Back returns to the previous filter")
    def test_filter_back_returns_to_previous_view(self, todo_app: TodoKeywords) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")
        todo_app.open_view(TodoView.ACTIVE)
        todo_app.open_view(TodoView.COMPLETED)

        # When
        todo_app.go_back()

        # Then
        todo_app.expect_view_opened(TodoView.ACTIVE)
        todo_app.expect_todos(["Buy milk", "Pay rent"])

    @allure.title("Forward returns to the next filter")
    def test_filter_forward_returns_to_next_view(self, todo_app: TodoKeywords) -> None:
        # Given
        todo_app.add_todos(["Buy milk", "Walk dog", "Pay rent"])
        todo_app.complete_todo("Walk dog")
        todo_app.open_view(TodoView.ACTIVE)
        todo_app.open_view(TodoView.COMPLETED)
        todo_app.go_back()

        # When
        todo_app.go_forward()

        # Then
        todo_app.expect_view_opened(TodoView.COMPLETED)
        todo_app.expect_todos(["Walk dog"])
