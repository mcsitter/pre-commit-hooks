"""Add canonical Ruff rule documentation links to pyproject.toml files."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

RULE_CODE_PATTERN = re.compile(r"\b[A-Z]+\d{3,}\b")
RULE_HEADER_PATTERN = re.compile(
    r"^#\s+(?P<slug>[a-z0-9-]+)\s+\((?P<code>[A-Z]+\d+)\)",
    re.MULTILINE,
)
RULE_LINK_PATTERN = re.compile(r"https://docs\.astral\.sh/ruff/rules/[a-z0-9-]+/")
RULE_LINK_TEMPLATE = "https://docs.astral.sh/ruff/rules/{slug}/"


class RuleLinkError(RuntimeError):
    """Report a rule lookup or TOML parsing failure."""


def _string_values(value: object) -> Iterator[str]:
    """Yield string values from a parsed TOML document."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _string_values(item)


def rule_codes(text: str) -> set[str]:
    """Return Ruff rule codes referenced by TOML string values."""
    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        msg = f"cannot parse TOML: {exc}"
        raise RuleLinkError(msg) from exc
    return {
        value
        for value in _string_values(document)
        if RULE_CODE_PATTERN.fullmatch(value)
    }


def resolve_rule_link(code: str) -> str:
    """Resolve one Ruff rule code to its documentation URL."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "ruff", "rule", code],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        msg = f"ruff could not resolve {code}: {detail}"
        raise RuleLinkError(msg)
    match = RULE_HEADER_PATTERN.search(result.stdout)
    if match is None:
        msg = f"ruff returned no rule header for {code}"
        raise RuleLinkError(msg)
    return RULE_LINK_TEMPLATE.format(slug=match.group("slug"))


def _line_codes(line: str, codes: set[str]) -> list[str]:
    """Return referenced rule codes that occur in a line."""
    return [code for code in sorted(codes) if re.search(rf"\b{code}\b", line)]


def add_rule_links(
    path: Path,
    resolver: Callable[[str], str] = resolve_rule_link,
    *,
    write: bool = True,
) -> bool:
    """Add missing rule links to one pyproject.toml file."""
    if path.name != "pyproject.toml":
        return False
    text = path.read_text(encoding="utf-8")
    codes = rule_codes(text)
    if not codes:
        return False
    links = {code: resolver(code) for code in sorted(codes)}
    lines = text.splitlines(keepends=True)
    updated: list[str] = []
    changed = False
    for line in lines:
        ending = "\n" if line.endswith("\n") else ""
        content = line[:-1] if ending else line
        referenced = _line_codes(content, codes)
        if not referenced:
            updated.append(line)
            continue
        existing = set(RULE_LINK_PATTERN.findall(content))
        missing = [links[code] for code in referenced if links[code] not in existing]
        if not missing:
            updated.append(line)
            continue
        suffix = "  # " + " ".join(missing)
        updated.append(f"{content}{suffix}{ending}")
        changed = True
    if changed and write:
        path.write_text("".join(updated), encoding="utf-8")
    return changed


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Ruff rule-link hook."""
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report files that need links without writing them.",
    )
    args = parser.parse_args(argv)
    paths = cast("list[str]", args.paths)
    check = bool(args.check)
    changed: list[str] = []
    try:
        for raw_path in paths:
            path = Path(raw_path)
            if add_rule_links(path, resolve_rule_link, write=not check):
                changed.append(raw_path)
    except (OSError, RuleLinkError) as exc:
        sys.stderr.write(f"ruff-rule-links: {exc}\n")
        return 1
    if changed:
        verb = "would update" if check else "updated"
        sys.stderr.write(f"ruff-rule-links: {verb} {len(changed)} file(s)\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
