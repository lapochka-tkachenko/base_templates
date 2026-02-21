from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.base.exceptions import BrowserNotStartedError
from apps.base.repositories.base import BasePlaywrightRepository
from apps.base.repositories.container import BaseContainer


# ---------------------------------------------------------------------------
# Concrete stub
# ---------------------------------------------------------------------------

class ConcreteRepository(BasePlaywrightRepository):
    async def run(self) -> Any:
        return "ok"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_container():
    """Reset singleton container state between tests."""
    container = BaseContainer()
    container._playwright = None
    container._browser = None
    container._lock = None
    yield
    container._playwright = None
    container._browser = None
    container._lock = None


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


# ---------------------------------------------------------------------------
# Tests: lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_creates_browser():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        repo = ConcreteRepository()
        await repo.start()

        assert BaseContainer().browser is browser
        assert repo._page is page

        await repo.close()


@pytest.mark.asyncio
async def test_singleton_browser_shared_between_instances():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        repo1 = ConcreteRepository()
        repo2 = ConcreteRepository()

        await repo1.start()
        await repo2.start()

        # Browser launched only once
        playwright.chromium.launch.assert_awaited_once()

        await repo1.close()
        await repo2.close()


@pytest.mark.asyncio
async def test_context_manager():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            assert repo._page is not None

        assert repo._page is None


@pytest.mark.asyncio
async def test_close_does_not_stop_browser():
    """Container browser stays alive after individual repo closes."""
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository():
            pass

        # Browser is still alive — only container.close() shuts it down
        assert BaseContainer().browser is not None


# ---------------------------------------------------------------------------
# Tests: properties raise before start
# ---------------------------------------------------------------------------

def test_page_raises_before_start():
    repo = ConcreteRepository()
    with pytest.raises(BrowserNotStartedError):
        _ = repo.page


def test_context_raises_before_start():
    repo = ConcreteRepository()
    with pytest.raises(BrowserNotStartedError):
        _ = repo.context


def test_browser_raises_before_start():
    repo = ConcreteRepository()
    with pytest.raises(BrowserNotStartedError):
        _ = repo.browser


# ---------------------------------------------------------------------------
# Tests: helpers delegate to page
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_navigate_calls_goto():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.navigate(url="https://example.com")
            page.goto.assert_awaited_once_with("https://example.com", wait_until="networkidle")


@pytest.mark.asyncio
async def test_fill_calls_page_fill():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.fill(selector="#input", value="hello")
            page.fill.assert_awaited_once_with("#input", "hello")


@pytest.mark.asyncio
async def test_click_calls_page_click():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.click(selector="button#submit")
            page.click.assert_awaited_once_with("button#submit")


@pytest.mark.asyncio
async def test_get_text_returns_inner_text():
    playwright, browser, context, page = make_mock_browser()
    page.inner_text = AsyncMock(return_value="Hello World")

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            result = await repo.get_text(selector="h1")
            assert result == "Hello World"


@pytest.mark.asyncio
async def test_screenshot_calls_page_screenshot():
    playwright, browser, context, page = make_mock_browser()

    with patch("apps.base.repositories.container.async_playwright") as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.screenshot(path="/tmp/screen.png")
            page.screenshot.assert_awaited_once_with(path="/tmp/screen.png", full_page=True)