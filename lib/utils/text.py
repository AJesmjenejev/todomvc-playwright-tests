import re


def exact_text(text: str) -> re.Pattern[str]:
    # A plain string would let Playwright trim and collapse spaces before comparing.
    return re.compile(rf"^{re.escape(text)}$")
