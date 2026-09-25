from __future__ import annotations

from pathlib import Path

import pytest

from pre_commit_hooks.ruff_rule_links import (
    RuleLinkError,
    add_rule_links,
    rule_codes,
)


def _resolver(code: str) -> str:
    slugs = {"COM812": "missing-trailing-comma", "D203": "one-blank-line-before-class"}
    return f"https://docs.astral.sh/ruff/rules/{slugs[code]}/"


def test_adds_links_and_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(
        '[tool.ruff.lint]\nignore = [\n  "COM812",\n  "D203",\n]\n',
        encoding="utf-8",
    )

    assert add_rule_links(path, _resolver) is True
    content = path.read_text(encoding="utf-8")

    assert "missing-trailing-comma" in content
    assert "one-blank-line-before-class" in content
    assert add_rule_links(path, _resolver) is False


def test_check_mode_does_not_write(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    original = '[tool.ruff.lint]\nselect = ["COM812"]\n'
    path.write_text(original, encoding="utf-8")

    assert add_rule_links(path, _resolver, write=False) is True
    assert path.read_text(encoding="utf-8") == original


def test_only_pyproject_toml_is_processed(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml.jinja"
    path.write_text('[tool.ruff.lint]\nselect = ["COM812"]\n', encoding="utf-8")

    assert add_rule_links(path, _resolver) is False


def test_rule_codes_only_reads_exact_rule_values() -> None:
    text = (
        '[project]\ndescription = "Uses D203 in prose"\n'
        '[tool.ruff.lint]\nselect = ["COM812", "E4"]\n'
    )

    assert rule_codes(text) == {"COM812"}


def test_invalid_toml_reports_a_clear_error() -> None:
    with pytest.raises(RuleLinkError, match="cannot parse TOML"):
        rule_codes("[tool.ruff\n")
