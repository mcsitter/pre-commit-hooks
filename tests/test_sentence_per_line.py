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


def test_keeps_list_continuations_indented() -> None:
    content = (
        "- Full type hints, modern syntax: `X | None`, and\n"
        "  `from __future__ import annotations`. Runtime-only types go behind\n"
        "  `TYPE_CHECKING`.\n"
        "- Keyword-only arguments get a bare `*`.\n"
    )

    assert format_markdown(content) == (
        "- Full type hints, modern syntax: `X | None`, and\n"
        "  `from __future__ import annotations`.\n"
        "  Runtime-only types go behind\n"
        "  `TYPE_CHECKING`.\n"
        "- Keyword-only arguments get a bare `*`.\n"
    )


def test_keeps_nested_list_continuations_indented() -> None:
    content = "- Outer item.\n  - Inner item. Still inner.\n    And deeper.\n"

    # The bullet line itself is structure and stays as written; only its
    # continuation is reflowed.
    assert format_markdown(content) == (
        "- Outer item.\n  - Inner item. Still inner.\n    And deeper.\n"
    )


def test_keeps_list_continuation_indented_across_a_blank_line() -> None:
    content = "- First item.\n\n  Continues in a loose list.\n\nAfter.\n"

    assert format_markdown(content) == (
        "- First item.\n\n  Continues in a loose list.\n\nAfter.\n"
    )


def test_leaving_a_list_clears_the_list_context() -> None:
    content = "- Item.\n\nNot in the list. Still not.\n"

    assert format_markdown(content) == ("- Item.\n\nNot in the list.\nStill not.\n")


def test_list_context_does_not_survive_a_fenced_block() -> None:
    content = "- Item.\n\n```\n  x = 1. y = 2.\n```\n\n  After the fence. And more.\n"

    assert format_markdown(content) == (
        "- Item.\n\n```\n  x = 1. y = 2.\n```\n\n  After the fence.\n  And more.\n"
    )


def test_indented_code_block_keeps_its_indent_on_every_line() -> None:
    content = "Intro. More.\n\n    x = 1. Y = 2.\n\nOutro.\n"

    assert format_markdown(content) == (
        "Intro.\nMore.\n\n    x = 1.\n    Y = 2.\n\nOutro.\n"
    )


def test_list_continuation_formatting_is_idempotent() -> None:
    content = "- Item. Second.\n  Third. Fourth.\n"

    assert format_markdown(format_markdown(content)) == format_markdown(content)
