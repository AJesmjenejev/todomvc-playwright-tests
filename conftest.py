import os
from collections.abc import Callable, Generator
from pathlib import Path

import allure
import pytest
from playwright.sync_api import BrowserContext, Page, expect

from lib.keywords.todo_keywords import TodoKeywords
from lib.pom.page_todo import TodoPage
from lib.utils.constants.timeouts import CHECK_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS

pytest_plugins = ["lib.utils.log_results"]

ARTIFACT_FOLDER = pytest.StashKey[Path]()


@pytest.hookimpl(tryfirst=True)  # before pytest's logging plugin opens the log file
def pytest_configure(config: pytest.Config) -> None:
    expect.set_options(timeout=CHECK_TIMEOUT_MS)
    worker = os.environ.get("PYTEST_XDIST_WORKER")  # set by pytest-xdist in each worker: gw0, gw1, ...
    if worker:  # one log file per worker, or the workers would mix their lines in one file
        config.option.log_file = f"logs/tests-{worker}.log"


def apply_timeouts(context: BrowserContext) -> None:
    # expect.set_options covers only expect(...). Without this, click, fill and check wait the 30 s default.
    context.set_default_timeout(CHECK_TIMEOUT_MS)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)


@pytest.fixture(autouse=True)
def set_context_timeouts(context: BrowserContext) -> None:
    apply_timeouts(context)


@pytest.fixture(autouse=True)
def group_report_by_browser(browser_name: str) -> None:
    # Otherwise the runs of one test in different browsers look identical in the Allure tree.
    allure.dynamic.parent_suite(browser_name)
    allure.dynamic.tag(browser_name)


@pytest.fixture(autouse=True)
def remember_artifact_folder(request: pytest.FixtureRequest, output_path: str) -> None:
    request.node.stash[ARTIFACT_FOLDER] = Path(output_path)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item: pytest.Item) -> Generator[None, None, None]:
    # pytest-playwright saves the screenshot and trace only when the browser closes, so attach them after teardown.
    try:
        yield
    finally:
        folder = item.stash.get(ARTIFACT_FOLDER, None)
        if folder is not None:
            for screenshot in sorted(folder.glob("*.png")):
                allure.attach.file(str(screenshot), name=screenshot.name, attachment_type=allure.attachment_type.PNG)
            for trace in sorted(folder.glob("*.zip")):
                allure.attach.file(str(trace), name=trace.name, extension="zip")


@pytest.fixture
def todo_app(page: Page) -> TodoKeywords:
    todo_app = TodoKeywords(TodoPage(page))
    todo_app.open_todo_app()
    return todo_app


@pytest.fixture
def fresh_todo_app(new_context: Callable[..., BrowserContext]) -> TodoKeywords:
    # A second, separate session; pytest-playwright's new_context records and closes it like the first.
    context = new_context()
    apply_timeouts(context)
    return TodoKeywords(TodoPage(context.new_page()))
