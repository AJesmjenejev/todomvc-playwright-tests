import allure
import pytest

from lib.keywords.todo_keywords import TodoKeywords


@allure.feature("Add a todo")
class TestAddTodo:
    @allure.title("Add a todo with English text")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_todo_english_text_is_listed(self, todo_app: TodoKeywords) -> None:
        """Requirement: a new todo item can be added using English text."""
        # When
        todo_app.add_todo("Buy milk")

        # Then
        todo_app.expect_todos(["Buy milk"])

    @allure.title("Add a todo with non-English text: {title}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "title",
        [
            pytest.param("Koupit mléko, žluťoučký kůň", id="czech"),
            pytest.param("Купить молоко", id="russian"),
            pytest.param("牛乳を買う", id="japanese"),
            pytest.param("شراء الحليب", id="arabic"),
            pytest.param("Buy 🥛 milk", id="emoji"),
        ],
    )
    def test_add_todo_non_english_text_is_listed(self, todo_app: TodoKeywords, title: str) -> None:
        """Requirement: a new todo item can be added using non-English characters (diacritics, Cyrillic,
        Japanese, right-to-left Arabic, emoji)."""
        # When
        todo_app.add_todo(title)

        # Then
        todo_app.expect_todos([title])

    @allure.title("Add a todo that includes numbers: {title}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "title",
        [
            pytest.param("Call 555 0199", id="number-inside-text"),
            pytest.param("2026", id="only-digits"),
            pytest.param("Buy 3 apples and 12 eggs", id="several-numbers"),
        ],
    )
    def test_add_todo_text_with_numbers_is_listed(self, todo_app: TodoKeywords, title: str) -> None:
        """Requirement: a new todo item can be added that includes numbers."""
        # When
        todo_app.add_todo(title)

        # Then
        todo_app.expect_todos([title])

    @allure.title("Adding todos updates the items-left counter")
    def test_add_todo_counter_shows_items_left(self, todo_app: TodoKeywords) -> None:
        # When
        todo_app.add_todos(["One", "Two"])

        # Then
        todo_app.expect_items_left(2)

    @allure.title("The input is cleared after a todo is added")
    def test_add_todo_input_is_cleared(self, todo_app: TodoKeywords) -> None:
        """The todo is listed first, so an empty input shows that the title was accepted, not lost."""
        # When
        todo_app.add_todo("Buy milk")

        # Then
        todo_app.expect_todos(["Buy milk"])
        todo_app.expect_new_todo_input_empty()

    @allure.title("A blank title is ignored: {blank!r}")
    @pytest.mark.parametrize("blank", ["", "   "], ids=["empty", "spaces-only"])
    def test_add_todo_blank_title_is_ignored(self, todo_app: TodoKeywords, blank: str) -> None:
        """An empty or spaces-only title creates no todo. A real todo is added after it,
        so the exact-list check cannot pass on an empty page."""
        # When
        todo_app.add_todo(blank)
        todo_app.add_todo("Buy milk")

        # Then
        todo_app.expect_todos(["Buy milk"])

    @allure.title("Spaces around a title are trimmed")
    def test_add_todo_surrounding_spaces_are_trimmed(self, todo_app: TodoKeywords) -> None:
        """The saved title has no leading or trailing spaces (the check compares text exactly)."""
        # When
        todo_app.add_todo("   padded   ")

        # Then
        todo_app.expect_todos(["padded"])
