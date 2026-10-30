from playwright.sync_api import Page

from lib.utils.logger import Log as log

_RELOAD_FLAG = "__reloadFlag"


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

    def reload(self) -> bool:
        # A flag on window is lost in a real reload, so a reload that did nothing can be told apart.
        log.debug("Reload the page")
        self.pw_page.evaluate("name => { window[name] = true; }", _RELOAD_FLAG)
        self.pw_page.reload()
        return not self.pw_page.evaluate("name => name in window", _RELOAD_FLAG)

    def go_back(self) -> None:
        log.debug("Go back in the browser history")
        self.pw_page.go_back()

    def go_forward(self) -> None:
        log.debug("Go forward in the browser history")
        self.pw_page.go_forward()
