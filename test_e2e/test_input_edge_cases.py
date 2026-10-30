import allure
import pytest

from lib.keywords.todo_keywords import TodoKeywords


@allure.feature("Input edge cases")
class TestInputEdgeCases:
    @allure.title("HTML in a title is shown as plain text: {title}")
    @pytest.mark.parametrize(
        "title",
        [
            pytest.param("<b>bold</b>", id="html-tag"),
            pytest.param('<img src=x onerror="alert(1)">', id="script-in-attribute"),
            pytest.param('Tom & Jerry\'s "quote" <tag>', id="special-characters"),
        ],
    )
    def test_input_html_is_shown_as_text(self, todo_app: TodoKeywords, title: str) -> None:
        """If user input became HTML, a title could run a script (XSS).
        The title must appear exactly as typed, with no HTML element inside it."""
        # When
        todo_app.add_todo(title)

        # Then
        todo_app.expect_todos([title])
        todo_app.expect_titles_are_plain_text()

    @allure.title("A very long title is kept in full and wraps inside the list")
    def test_input_long_title_wraps_inside_the_list(self, todo_app: TodoKeywords) -> None:
        """A 300-character word has no spaces, so the browser has no place to break the line.
        The full text must be kept, and it must not stick out of the list."""
        # Given
        long_title = "x" * 300

        # When
        todo_app.add_todo(long_title)

        # Then
        todo_app.expect_todos([long_title])
        todo_app.expect_todo_title_fits_in_list(long_title)

    @allure.title("Duplicate titles: completing one completes only that one")
    def test_input_duplicate_title_complete_one(self, todo_app: TodoKeywords) -> None:
        """Two todos may have the same title. The second one is chosen by position (nth=1),
        so the counter proves the first one is still active."""
        # Given
        todo_app.add_todos(["Buy milk", "Buy milk", "Walk dog"])

        # When
        todo_app.complete_todo("Buy milk", nth=1)

        # Then
        todo_app.expect_todos(["Buy milk", "Buy milk", "Walk dog"])
        todo_app.expect_todo_completed("Buy milk", nth=1)
        todo_app.expect_items_left(2)

    @allure.title("Duplicate titles: deleting one keeps the other")
    def test_input_duplicate_title_delete_one(self, todo_app: TodoKeywords) -> None:
        """The two titles look the same, so the list alone cannot show which one was deleted.
        Only the second one is completed: if it is the one that remains, the first one was deleted."""
        # Given
        todo_app.add_todos(["Buy milk", "Buy milk", "Walk dog"])
        todo_app.complete_todo("Buy milk", nth=1)

        # When
        todo_app.delete_todo("Buy milk", nth=0)

        # Then
        todo_app.expect_todos(["Buy milk", "Walk dog"])
        todo_app.expect_todo_completed("Buy milk")
        todo_app.expect_items_left(1)
