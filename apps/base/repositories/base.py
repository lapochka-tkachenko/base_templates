from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from apps.base.decorators import handle_playwright_errors
from apps.base.exceptions import BrowserNotStartedError
from apps.base.repositories.abstract import AbstractBrowserRepository
from apps.base.repositories.container import BaseContainer
from core.settings import COOKIES_DIR

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page


class BasePlaywrightRepository(AbstractBrowserRepository):
    """
    Base repository — gets browser from the singleton container.
    Each instance manages its own BrowserContext and Page.
    """

    _context: BrowserContext | None = None
    _page: Page | None = None

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

    @handle_playwright_errors
    async def navigate(self, *, url: str, wait_until: str = 'networkidle') -> None:
        """Navigate to url."""
        await self.page.goto(url, wait_until=wait_until)  # type: ignore[arg-type]

    @handle_playwright_errors
    async def screenshot(self, *, path: str) -> None:
        """Take a full-page screenshot and save to path."""
        await self.page.screenshot(path=path, full_page=True)

    @handle_playwright_errors
    async def wait_for_selector(self, *, selector: str, timeout: float | None = None) -> None:
        """Wait until selector appears on the page."""
        await self.page.wait_for_selector(selector, timeout=timeout or self.timeout)

    @handle_playwright_errors
    async def fill(self, *, selector: str, value: str) -> None:
        """Fill input field."""
        await self.page.fill(selector, value)

    @handle_playwright_errors
    async def click(self, *, selector: str) -> None:
        """Click element."""
        await self.page.click(selector)

    @handle_playwright_errors
    async def get_text(self, *, selector: str) -> str:
        """Return inner text of element."""
        return await self.page.inner_text(selector)

    async def save_cookies(self, *, username: str) -> None:
        """Save current browser cookies to cookies/<username>.json."""
        COOKIES_DIR.mkdir(exist_ok=True)
        cookies = await self.context.cookies()
        (COOKIES_DIR / f'{username}.json').write_text(json.dumps(cookies))

    async def load_cookies(self, *, username: str) -> bool:
        """Load cookies from cookies/<username>.json into browser context.

        Returns True if the file existed and cookies were applied, False otherwise.
        """
        path = COOKIES_DIR / f'{username}.json'
        if not path.exists():
            return False
        cookies = json.loads(path.read_text())
        await self.context.add_cookies(cookies)
        return True

    async def run(self) -> Any:
        """Entry point for concrete repository logic."""
        raise NotImplementedError
