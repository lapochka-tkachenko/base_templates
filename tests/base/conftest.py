from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.base.repositories.base import BasePlaywrightRepository
from apps.base.repositories.container import BaseContainer


class ConcreteRepository(BasePlaywrightRepository):
    async def run(self) -> Any:
        return 'ok'


@pytest.fixture(autouse=True)
def reset_container():
    """Reset singleton container state between tests."""
    container = BaseContainer()
    container._playwright = None
    container._browser = None
    container._lock = asyncio.Lock()
    yield
    container._playwright = None
    container._browser = None
    container._lock = asyncio.Lock()


def make_mock_browser() -> tuple:
    """Build a mock playwright/browser/context/page chain."""
    page = AsyncMock()
    context = AsyncMock()
    context.set_default_timeout = MagicMock()  # sync call
    context.new_page = AsyncMock(return_value=page)
    browser = AsyncMock()
    browser.new_context = AsyncMock(return_value=context)
    playwright = AsyncMock()
    playwright.chromium.launch = AsyncMock(return_value=browser)
    return playwright, browser, context, page
