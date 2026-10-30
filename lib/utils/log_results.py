"""pytest plugin: writes a header and a result line for every test to the log (loaded from conftest.py)."""

import logging
import time

import pytest

from lib.utils.logger import Log as log

_HEADER = "=" * 20
_RESULT = "-" * 20
_started_at: dict[str, float] = {}


def pytest_configure() -> None:
    logging.getLogger("asyncio").setLevel(logging.WARNING)  # hide "Using proactor: ..." noise


def pytest_runtest_logstart(nodeid: str) -> None:
    _started_at[nodeid] = time.monotonic()
    log.info(f"{_HEADER} {nodeid}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    # One result line per test: after the test body, or after setup if the test never started.
    if report.when == "call" or (report.when == "setup" and not report.passed):
        seconds = time.monotonic() - _started_at.pop(report.nodeid, time.monotonic())
        if report.passed:
            log.info(f"{_RESULT} PASSED in {seconds:.1f} s\n")
        elif hasattr(report, "wasxfail"):  # pytest stores an expected failure as "skipped"
            log.info(f"{_RESULT} XFAIL (expected failure): {report.wasxfail}\n")
        elif report.skipped:
            log.info(f"{_RESULT} SKIPPED: {_reason(report)}\n")
        elif report.when == "setup":
            log.error(f"{_RESULT} ERROR in setup: {_reason(report)}\n")
        else:
            log.error(f"{_RESULT} FAILED in {seconds:.1f} s: {_reason(report)}\n")
    if report.when == "teardown" and report.failed:  # the body passed, but the cleanup after it failed
        log.error(f"{_RESULT} TEARDOWN FAILED: {_reason(report)}\n")


def _reason(report: pytest.TestReport) -> str:
    # pytest has no public API for a short reason, so its internals are read here, in one place.
    if report.skipped and isinstance(report.longrepr, tuple):
        return report.longrepr[2].removeprefix("Skipped: ")
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash:
        lines = str(crash.message).splitlines()[:1]
    else:
        lines = report.longreprtext.strip().splitlines()[-1:]
    return lines[0] if lines else "no reason given"  # the text can be empty, e.g. after a bare setup error
