from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from apps.base.decorators import OnError
from apps.base.exceptions import BrowserNotStartedError
from apps.base.repositories.abstract import AbstractBrowserRepository
from apps.base.repositories.container import BaseContainer
from apps.instagram.utils import safe_cookie_filename
from core.settings import COOKIES_DIR

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page

    from apps.base.typing import WaitUntil


class BasePlaywrightRepository(AbstractBrowserRepository):
    """Base repository — gets browser from the singleton container.
    Each instance manages its own BrowserContext and Page.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        slow_mo: float = 0,
        timeout: float = 30_000,
    ) -> None:
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        """Get browser from container and open a new context and page."""
        browser: Browser = await BaseContainer().get_browser(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self._context = await browser.new_context()
        self._context.set_default_timeout(self.timeout)
        self._page = await self._context.new_page()

    async def close(self) -> None:
        """Close this instance's context and page."""
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None

    @property
    def page(self) -> Page:
        """Return the current page, raise if not started."""
        if self._page is None:
            raise BrowserNotStartedError
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Return the current browser context, raise if not started."""
        if self._context is None:
            raise BrowserNotStartedError
        return self._context

    @property
    def browser(self) -> Browser:
        """Return the shared browser from the container, raise if not started."""
        browser = BaseContainer().browser
        if browser is None:
            raise BrowserNotStartedError
        return browser

    @OnError.playwright_errors
    async def navigate(self, *, url: str, wait_until: WaitUntil = 'domcontentloaded') -> None:
        """Navigate to url."""
        await self.page.goto(url, wait_until=wait_until)

    @OnError.playwright_errors
    async def reload(self) -> None:
        """Reload the current page."""
        await self.page.reload()

    @OnError.playwright_errors
    async def screenshot(self, *, path: str) -> None:
        """Take a full-page screenshot and save to path."""
        await self.page.screenshot(path=path, full_page=True)

    @OnError.playwright_errors
    async def wait_for_selector(self, *, selector: str, timeout: float | None = None) -> None:
        """Wait until selector appears on the page."""
        await self.page.wait_for_selector(selector, timeout=timeout or self.timeout)

    @OnError.playwright_errors
    async def fill(self, *, selector: str, value: str) -> None:
        """Fill input field."""
        await self.page.fill(selector, value)

    @OnError.playwright_errors
    async def click(self, *, selector: str) -> None:
        """Click element."""
        await self.page.click(selector)

    @OnError.playwright_errors
    async def get_text(self, *, selector: str) -> str:
        """Return inner text of element."""
        return await self.page.inner_text(selector)

    @OnError.playwright_errors
    async def press_enter(self) -> None:
        """Press the Enter key on the current page.

        Useful for accepting cookie consent dialogs or submitting forms
        when a visible submit button is not available.
        """
        await self.page.keyboard.press('Enter')

    async def get_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    @OnError.playwright_errors
    async def wait_for_url_change(self, *, away_from: str, timeout: float | None = None) -> None:
        """Wait until the current URL no longer contains away_from."""
        await self.page.wait_for_url(
            lambda url: away_from not in url,
            timeout=timeout or self.timeout,
        )

    @OnError.playwright_errors
    async def save_cookies(self, *, username: str) -> None:
        """Save current browser cookies to cookies/<username>.json."""
        COOKIES_DIR.mkdir(exist_ok=True)
        path = COOKIES_DIR / f'{safe_cookie_filename(username)}.json'
        cookies = await self.context.cookies()
        # Open with O_CREAT + mode=0o600 atomically to avoid a race between
        # write and chmod that would leave the file world-readable momentarily.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(json.dumps(cookies))

    @OnError.playwright_errors
    async def upload_file(self, *, trigger_selector: str, file_path: str) -> None:
        """Click trigger_selector and set file_path on the file chooser that opens."""
        async with self.page.expect_file_chooser() as fc_info:
            await self.page.click(trigger_selector)
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)

    @OnError.playwright_errors
    async def count_elements(self, *, selector: str) -> int:
        """Return the number of elements matching selector currently in the DOM."""
        elements = await self.page.query_selector_all(selector)
        return len(elements)

    @OnError.playwright_errors
    async def load_cookies(self, *, username: str) -> bool:
        """Load cookies from cookies/<username>.json into browser context.

        Returns True if the file existed and cookies were applied, False otherwise.
        """
        path = COOKIES_DIR / f'{safe_cookie_filename(username)}.json'
        if not path.exists():
            return False
        cookies = json.loads(path.read_text())
        await self.context.add_cookies(cookies)
        return True
