"""Put every Markdown sentence on its own line.

Keeping one sentence per line makes diffs readable, because a rewritten
sentence shows up as a single changed line instead of being buried in a
rewrapped paragraph. Structural Markdown (code fences, headings, lists,
tables, block quotes, and MkDocs admonitions) is left untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

SENTENCE_END = re.compile(r"(?<=[.!?])[ \t]+(?=[A-Z0-9])")
CODE_SPAN = re.compile(r"`+[^`]*`+")
FENCE = re.compile(r"^(```|~~~)")
ADMONITION = re.compile(r"^(?:!!!|\?\?\?|===)")
HEADING = re.compile(r"^#{1,6}\s")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
THEMATIC_BREAK = re.compile(r"^\s*(?:([-*_])\s*)+\1\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
QUOTE = re.compile(r"^\s*>")
PLACEHOLDER = "\x00{}\x00"


def _split_sentences(line: str) -> list[str]:
    """Split one prose line into sentences, ignoring inline code spans."""
    spans: list[str] = []

    def hide(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return PLACEHOLDER.format(len(spans) - 1)

    masked = CODE_SPAN.sub(hide, line)
    parts = SENTENCE_END.split(masked)
    restored: list[str] = []
    for part in parts:
        for position, span in enumerate(spans):
            part = part.replace(PLACEHOLDER.format(position), span)  # noqa: PLW2901
        restored.append(part)
    return restored


def _indent_of(line: str) -> str:
    """Return the leading whitespace of a line."""
    return line[: len(line) - len(line.lstrip())]


def _is_structural(line: str) -> bool:
    """Return whether a line is Markdown structure rather than prose."""
    stripped = line.lstrip()
    return bool(
        FENCE.match(stripped)
        or ADMONITION.match(stripped)
        or HEADING.match(stripped)
        or LIST_ITEM.match(line)
        or THEMATIC_BREAK.match(stripped)
        or TABLE_ROW.match(stripped)
        or QUOTE.match(stripped)
    )


def _prose_lines(line: str) -> list[str]:
    """Return the sentences a prose line expands to.

    An indented line keeps that indentation on every sentence, not just the
    first. An unindented line after a bullet is a new paragraph, so a dropped
    indent silently ends the list item part-way through its own sentence, which
    is the one thing this hook must never do.
    """
    indent = _indent_of(line)
    return [indent + part for part in _split_sentences(line[len(indent) :])]


def format_markdown(content: str) -> str:
    """Return the content with one sentence per line."""
    output: list[str] = []
    fence: str | None = None
    admonition = False

    for line in content.splitlines():
        stripped = line.lstrip()
        if fence is not None:
            output.append(line)
            if stripped.startswith(fence):
                fence = None
            continue
        if FENCE.match(stripped):
            fence = stripped[:3]
            output.append(line)
            continue
        if admonition:
            # Indented continuation lines belong to the admonition body.
            if not line.strip() or line.startswith((" ", "\t")):
                output.append(line)
                continue
            admonition = False
        if _is_structural(line):
            admonition = bool(ADMONITION.match(stripped))
            output.append(line)
            continue
        if not line.strip():
            output.append(line)
            continue
        output.extend(_prose_lines(line))

    return "\n".join(output) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the sentence-per-line hook."""
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report files that need reformatting without writing them.",
    )
    args = parser.parse_args(argv)
    paths = cast("list[str]", args.paths)
    check = bool(args.check)
    changed: list[str] = []
    try:
        for raw_path in paths:
            path = Path(raw_path)
            if path.suffix.lower() not in {".md", ".markdown"}:
                continue
            original = path.read_text(encoding="utf-8")
            updated = format_markdown(original)
            if updated == original:
                continue
            changed.append(raw_path)
            if not check:
                path.write_text(updated, encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"sentence-per-line: {exc}\n")
        return 1
    if changed:
        verb = "would update" if check else "updated"
        sys.stderr.write(f"sentence-per-line: {verb} {len(changed)} file(s)\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
