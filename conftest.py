import logging
import time
from pathlib import Path
from typing import Any, Generator

import allure
import pytest
from playwright.sync_api import Browser, Page

from lib.keywords.todo_keywords import TodoKeywords
from lib.pom.page_todo import TodoPage
from lib.utils.logger import TestLogger as log

ARTIFACT_FOLDER = pytest.StashKey[Path]()


def pytest_configure() -> None:
    logging.getLogger("asyncio").setLevel(logging.WARNING)  # hide "Using proactor: ..." noise


_test_started_at: dict[str, float] = {}


def pytest_runtest_logstart(nodeid: str) -> None:
    _test_started_at[nodeid] = time.monotonic()
    log.info(f"{'=' * 20} {nodeid}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    # One result line per test: after the test body, or after setup if the test never started.
    if report.when == "call" or (report.when == "setup" and not report.passed):
        seconds = time.monotonic() - _test_started_at.pop(report.nodeid, time.monotonic())
        log.info(f"{'-' * 20} {report.outcome.upper()} in {seconds:.1f} s\n")


@pytest.fixture(autouse=True)
def group_report_by_browser(browser_name: str) -> None:
    # Without this, the runs of one test in different browsers look identical in the Allure tree.
    allure.dynamic.parent_suite(browser_name)
    allure.dynamic.tag(browser_name)


@pytest.fixture(autouse=True)
def remember_artifact_folder(request: pytest.FixtureRequest, output_path: str) -> None:
    request.node.stash[ARTIFACT_FOLDER] = Path(output_path)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item: pytest.Item) -> Generator[None, None, None]:
    # pytest-playwright saves the screenshot and trace of a failed test when the browser closes,
    # so they only exist after teardown. Attach them to the Allure report then.
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
def fresh_todo_app(browser: Browser, browser_context_args: dict[str, Any]) -> Generator[TodoKeywords, None, None]:
    # A second, separate browser context: like another user or a new browser profile. Not opened yet.
    context = browser.new_context(**browser_context_args)
    try:
        yield TodoKeywords(TodoPage(context.new_page()))
    finally:
        context.close()
