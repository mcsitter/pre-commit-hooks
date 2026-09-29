from __future__ import annotations

import tomllib
from importlib.metadata import version
from pathlib import Path

from pre_commit_hooks import __version__

ROOT = Path(__file__).resolve().parent.parent


def declared_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def test_version_is_not_hardcoded() -> None:
    assert __version__ == version("pre-commit-hooks"), (
        "pre_commit_hooks.__version__ must come from importlib.metadata; "
        "pyproject.toml is the single source of truth"
    )


def test_readme_rev_matches_version() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"rev: v{declared_version()}" in readme, (
        f"README is not pinned to v{declared_version()}; run 'make sync-readme'"
    )
