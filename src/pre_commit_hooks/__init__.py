"""Reusable pre-commit hooks for Python projects."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pre-commit-hooks")
except PackageNotFoundError:
    __version__ = "0.0.0"
