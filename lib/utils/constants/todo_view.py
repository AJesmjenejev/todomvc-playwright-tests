from enum import StrEnum


class TodoView(StrEnum):
    ALL = "All"
    ACTIVE = "Active"
    COMPLETED = "Completed"

    @property
    def route(self) -> str:
        # The end of the URL that the app shows for this view.
        return {TodoView.ALL: "#/", TodoView.ACTIVE: "#/active", TodoView.COMPLETED: "#/completed"}[self]
