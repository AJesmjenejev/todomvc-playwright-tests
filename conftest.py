import logging
import time
from pathlib import Path
from typing import Callable, Generator

import allure
import pytest
from playwright.sync_api import BrowserContext, Page

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
    # The test body can pass while cleanup after it fails: say so, or the log would only show PASSED.
    if report.when == "teardown" and report.failed:
        crash = getattr(report.longrepr, "reprcrash", None)  # pytest's short "Error: message" summary
        reason = crash.message if crash else report.longreprtext.strip().splitlines()[-1]
        log.error(f"{'-' * 20} TEARDOWN FAILED: {reason}\n")


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
def fresh_todo_app(new_context: Callable[..., BrowserContext]) -> TodoKeywords:
    # A second, separate browser context: like another user or a new browser profile. Not opened yet.
    # pytest-playwright's new_context gives it the same base_url, records its screenshot and trace on
    # failure, and closes it after the test.
    return TodoKeywords(TodoPage(new_context().new_page()))
