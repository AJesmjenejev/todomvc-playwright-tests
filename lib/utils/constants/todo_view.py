from enum import StrEnum


class TodoView(StrEnum):
    ALL = "All"
    ACTIVE = "Active"
    COMPLETED = "Completed"

    @property
    def route(self) -> str:
        return _ROUTES[self]


# The end of the URL that the app shows for each view. Keyed by the members, so renaming one fails on import.
_ROUTES = {
    TodoView.ALL: "#/",
    TodoView.ACTIVE: "#/active",
    TodoView.COMPLETED: "#/completed",
}
