"""Check the AAA structure of every test.

Rules:
- `# When` and `# Then` comments are required.
- `# Given` is optional (only when there is setup).
- The order must be Given -> When -> Then.

Usage: python tools/aaa_structure_linter.py [tests_dir ...]   (default: test_e2e and proofs, found from this file)
Exit code 1 if any test breaks a rule, or if a folder has no test files (so a wrong path never passes silently).
"""

import ast
import re
import sys
from pathlib import Path

SECTION_ORDER = ("Given", "When", "Then")
REQUIRED_SECTIONS = ("When", "Then")
SECTION_COMMENT = re.compile(r"^\s*#\s*(Given|When|Then)\b")
DEFAULT_DIRS = [Path(__file__).resolve().parent.parent / name for name in ("test_e2e", "proofs")]


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


def main(tests_dirs: list[Path]) -> int:
    violations = []
    for tests_dir in tests_dirs:
        test_files = sorted(tests_dir.rglob("test_*.py"))
        if not test_files:
            violations.append(f"{tests_dir}: no test files found, nothing was checked")
        for test_file in test_files:
            violations.extend(find_violations(test_file))
    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main([Path(arg) for arg in sys.argv[1:]] or DEFAULT_DIRS))
