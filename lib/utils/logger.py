import logging

_logger = logging.getLogger("todomvc")


class TestLogger:
    __test__ = False  # not a test class, even though the name starts with "Test"

    # stacklevel=2: the log shows the caller's file and line, not this file.
    @staticmethod
    def info(message: str) -> None:
        _logger.info(message, stacklevel=2)

    @staticmethod
    def debug(message: str) -> None:
        _logger.debug(f"   {message}", stacklevel=2)  # indented: a detail of the INFO step above
