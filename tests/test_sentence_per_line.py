from __future__ import annotations

from pre_commit_hooks.sentence_per_line import format_markdown


def test_splits_prose_into_one_sentence_per_line() -> None:
    content = "One. Two! Three? Four\n"

    assert format_markdown(content) == "One.\nTwo!\nThree?\nFour\n"


def test_is_idempotent() -> None:
    once = format_markdown("Alpha. Beta. Gamma.\n")

    assert format_markdown(once) == once


def test_leaves_fenced_code_blocks_untouched() -> None:
    content = "Intro. More.\n\n```python\nx = 1. y = 2.\n```\n\nOutro. Here.\n"

    assert format_markdown(content) == (
        "Intro.\nMore.\n\n```python\nx = 1. y = 2.\n```\n\nOutro.\nHere.\n"
    )


def test_leaves_structure_untouched() -> None:
    content = (
        "# Title. Subtitle\n"
        "\n"
        "- Item one. Item two.\n"
        "\n"
        "> Quoted. Text.\n"
        "\n"
        "| a. b | c. d |\n"
        "\n"
        "---\n"
    )

    assert format_markdown(content) == content


def test_leaves_admonition_bodies_untouched() -> None:
    content = '!!! note "A. B"\n    Body one. Body two.\n\nAfter. Text.\n'

    assert format_markdown(content) == (
        '!!! note "A. B"\n    Body one. Body two.\n\nAfter.\nText.\n'
    )


def test_does_not_split_inside_inline_code() -> None:
    content = "Run `make a. b` now. Then stop.\n"

    assert format_markdown(content) == "Run `make a. b` now.\nThen stop.\n"


def test_preserves_blank_lines() -> None:
    content = "One. Two.\n\n\nThree. Four.\n"

    assert format_markdown(content) == "One.\nTwo.\n\n\nThree.\nFour.\n"


def test_adds_trailing_newline() -> None:
    assert format_markdown("A. B.") == "A.\nB.\n"
