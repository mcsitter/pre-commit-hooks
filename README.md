# pre-commit-hooks

Reusable pre-commit hooks for Python projects.

## Hooks

### `ruff-rule-links`

Adds canonical [Ruff rule documentation](https://docs.astral.sh/ruff/) links to Ruff rule codes referenced by `pyproject.toml`.

The hook is intentionally limited to files named exactly `pyproject.toml`.
It is idempotent and can be run in check-only mode with `--check`.

### `sentence-per-line`

Rewrites Markdown prose so that every sentence starts on a new line.
Rewrapped sentences produce noisy diffs; with one sentence per line a change
shows up as a single modified line.

Code fences, headings, lists, tables, block quotes, and MkDocs admonitions are left untouched, and text inside inline code spans is never split.
The hook is idempotent and supports `--check`.

## Installation

Enable whichever hooks you want:

```yaml
repos:
  - repo: https://github.com/mcsitter/pre-commit-hooks
    rev: v0.0.2
    hooks:
      - id: ruff-rule-links
      - id: sentence-per-line
```
