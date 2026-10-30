import os

# One timeout for expect(...), for page actions (click, fill, ...) and for the waits in the page objects,
# in milliseconds. On a slow machine: TODO_TIMEOUT_MS=15000 python -m pytest
CHECK_TIMEOUT_MS = float(os.environ.get("TODO_TIMEOUT_MS", "5000"))

# Loading the public demo site can be slow, so page loads keep Playwright's default of 30 seconds.
NAVIGATION_TIMEOUT_MS = 30_000.0
