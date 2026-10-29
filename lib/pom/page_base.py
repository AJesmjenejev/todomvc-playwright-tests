from playwright.sync_api import Page

from lib.utils.logger import TestLogger as log


class BasePage:
    PATH = ""

    def __init__(self, page: Page) -> None:
        self._page = page

    @property
    def pw_page(self) -> Page:
        return self._page

    def goto(self) -> None:
        log.debug(f"Navigate to '{self.PATH}'")
        self.pw_page.goto(self.PATH)

    def reload(self) -> None:
        log.debug("Reload the page")
        self.pw_page.reload()
