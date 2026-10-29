import allure
import pytest

from lib.keywords.todo_keywords import TodoKeywords


@allure.feature("Input edge cases")
class TestInputEdgeCases:
    @allure.title("HTML in a title is shown as text, not rendered: {title}")
    @pytest.mark.parametrize(
        "title",
        [
            pytest.param("<b>bold</b>", id="html-tag"),
            pytest.param('<img src=x onerror="alert(1)">', id="script-in-attribute"),
            pytest.param('Tom & Jerry\'s "quote" <tag>', id="special-characters"),
        ],
    )
    def test_input_html_is_shown_as_text(self, todo_app: TodoKeywords, title: str) -> None:
        """User input must never become HTML. If it did, a title could run a script (XSS).
        The title must be shown exactly as typed, and no element may be created inside it."""
        # When
        todo_app.add_todo(title)

        # Then
        todo_app.expect_todos([title])
        todo_app.expect_titles_are_plain_text()

    @allure.title("A very long title is kept in full and wraps inside the list")
    def test_input_long_title_wraps_inside_the_list(self, todo_app: TodoKeywords) -> None:
        """A 300-character word without spaces is the hardest case for wrapping.
        The full text must be kept, and it must not stick out of the list."""
        # Given
        long_title = "x" * 300

        # When
        todo_app.add_todo(long_title)

        # Then
        todo_app.expect_todos([long_title])
        todo_app.expect_todo_title_fits_in_list(long_title)
