from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from apps.base.exceptions import BrowserPageError, BrowserTimeoutError
from apps.base.repositories.base import BasePlaywrightRepository
from tests.base.conftest import ConcreteRepository, make_mock_browser


# ---------------------------------------------------------------------------
# Tests: press_enter
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_press_enter_calls_keyboard_press():
    playwright, browser, context, page = make_mock_browser()

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.press_enter()
            page.keyboard.press.assert_awaited_once_with('Enter')


# ---------------------------------------------------------------------------
# Tests: save_cookies / load_cookies
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_save_cookies_writes_json_file(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.base.repositories.base.COOKIES_DIR', tmp_path)
    playwright, browser, context, page = make_mock_browser()
    cookies = [{'name': 'sessionid', 'value': 'abc123'}]
    context.cookies = AsyncMock(return_value=cookies)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            await repo.save_cookies(username='testuser')

    saved = json.loads((tmp_path / 'testuser.json').read_text())
    assert saved == cookies


@pytest.mark.asyncio
async def test_load_cookies_returns_true_and_adds_cookies(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.base.repositories.base.COOKIES_DIR', tmp_path)
    cookies = [{'name': 'sessionid', 'value': 'abc123'}]
    (tmp_path / 'testuser.json').write_text(json.dumps(cookies))
    playwright, browser, context, page = make_mock_browser()

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            result = await repo.load_cookies(username='testuser')

    assert result is True
    context.add_cookies.assert_awaited_once_with(cookies)


@pytest.mark.asyncio
async def test_load_cookies_returns_false_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr('apps.base.repositories.base.COOKIES_DIR', tmp_path)
    repo = ConcreteRepository()
    result = await repo.load_cookies(username='nonexistent')
    assert result is False


@pytest.mark.asyncio
async def test_navigate_raises_browser_timeout_error_on_playwright_timeout():
    playwright, browser, context, page = make_mock_browser()
    page.goto = AsyncMock(side_effect=PlaywrightTimeoutError('timeout'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            with pytest.raises(BrowserTimeoutError):
                await repo.navigate(url='https://example.com')


@pytest.mark.asyncio
async def test_navigate_raises_browser_page_error_on_playwright_error():
    playwright, browser, context, page = make_mock_browser()
    page.goto = AsyncMock(side_effect=PlaywrightError('nav failed'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            with pytest.raises(BrowserPageError):
                await repo.navigate(url='https://example.com')


@pytest.mark.asyncio
async def test_click_raises_browser_timeout_error_on_playwright_timeout():
    playwright, browser, context, page = make_mock_browser()
    page.click = AsyncMock(side_effect=PlaywrightTimeoutError('timeout'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            with pytest.raises(BrowserTimeoutError):
                await repo.click(selector='button')


@pytest.mark.asyncio
async def test_fill_raises_browser_page_error_on_playwright_error():
    playwright, browser, context, page = make_mock_browser()
    page.fill = AsyncMock(side_effect=PlaywrightError('fill failed'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with ConcreteRepository() as repo:
            with pytest.raises(BrowserPageError):
                await repo.fill(selector='input', value='text')
