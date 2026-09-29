"""Sync the README install snippet's `rev` with the version in pyproject.toml.

Runs automatically as a commitizen post-bump hook so `cz bump` never leaves
the README advertising a stale tag.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
DECLARED_VERSION = re.compile(r'^version = "(?P<version>[^"]+)"', re.MULTILINE)
REV_REFERENCE = re.compile(r"(?<=rev: v)\d+\.\d+\.\d+")


def read_declared_version() -> str | None:
    """Return the project version declared in pyproject.toml."""
    match = DECLARED_VERSION.search(PYPROJECT.read_text(encoding="utf-8"))
    return match.group("version") if match else None


def main() -> int:
    """Rewrite every `rev: vX.Y.Z` in the README to the declared version."""
    declared = read_declared_version()
    if declared is None:
        print(f"error: no version entry found in {PYPROJECT}")
        return 1

    readme = README.read_text(encoding="utf-8")
    updated, count = REV_REFERENCE.subn(declared, readme)
    if count == 0:
        print(f"error: no `rev: vX.Y.Z` install snippet found in {README}")
        return 1

    if updated == readme:
        print(f"README already references v{declared}")
        return 0

    README.write_text(updated, encoding="utf-8")
    print(f"README rev synced to v{declared}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
