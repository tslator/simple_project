"""Shared test configuration."""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Set offscreen platform for headless CI and local non-display environments."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
