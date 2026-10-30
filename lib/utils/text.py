import re


def exact_text(text: str) -> re.Pattern[str]:
    # A plain string would let Playwright trim and collapse spaces before comparing.
    return re.compile(rf"^{re.escape(text)}$")


def quoted(titles: list[str]) -> str:
    # Readable list for step titles; a Python list would show 'Jerry\'s' with a backslash.
    return ", ".join(f"'{title}'" for title in titles) or "nothing"


def which(title: str, nth: int | None) -> str:
    # For log lines: 'Buy milk', or 'Buy milk' (#2) when one of several todos with that title is meant.
    return f"'{title}'" if nth is None else f"'{title}' (#{nth + 1})"
