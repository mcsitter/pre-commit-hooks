# pre-commit-hooks

Reusable pre-commit hooks for Python projects.

## Hooks

### `ruff-rule-links`

Adds canonical [Ruff rule documentation](https://docs.astral.sh/ruff/) links to Ruff rule codes referenced by `pyproject.toml`.

The hook is intentionally limited to files named exactly `pyproject.toml`. It is idempotent and can be run in check-only mode with `--check`.

```yaml
repos:
  - repo: https://github.com/mcsitter/pre-commit-hooks
    rev: v0.0.1
    hooks:
      - id: ruff-rule-links
```
