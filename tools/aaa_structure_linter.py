"""Check the AAA structure of every test.

Rules:
- `# When` and `# Then` comments are required.
- `# Given` is optional (only when there is setup).
- The order must be Given -> When -> Then.

Usage: python tools/aaa_structure_linter.py [tests_dir]   (default: test_e2e)
Exit code 1 if any test breaks a rule.
"""

import ast
import re
import sys
from pathlib import Path

SECTION_ORDER = ("Given", "When", "Then")
REQUIRED_SECTIONS = ("When", "Then")
SECTION_COMMENT = re.compile(r"^\s*#\s*(Given|When|Then)\b")


def find_violations(test_file: Path) -> list[str]:
    source = test_file.read_text(encoding="utf-8")
    lines = source.splitlines()
    violations = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        where = f"{test_file}:{node.lineno} {node.name}"
        found = []
        for line in lines[node.lineno - 1 : node.end_lineno]:
            match = SECTION_COMMENT.match(line)
            if match:
                found.append(match.group(1))
        for section in REQUIRED_SECTIONS:
            if section not in found:
                violations.append(f"{where}: missing '# {section}'")
        if found != sorted(found, key=SECTION_ORDER.index):
            violations.append(f"{where}: sections are in the wrong order {found}, expected Given -> When -> Then")
    return violations


def main(tests_dir: str = "test_e2e") -> int:
    violations = [v for test_file in sorted(Path(tests_dir).rglob("test_*.py")) for v in find_violations(test_file)]
    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
