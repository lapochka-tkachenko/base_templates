from __future__ import annotations

import asyncio

from playwright.async_api import Browser, Playwright, async_playwright


class BaseContainer:
    """
    Singleton container for one browser.
    """

    _instance: BaseContainer | None = None
    _playwright: Playwright | None = None
    _browser: Browser | None = None
    _lock: asyncio.Lock | None = None

    def __new__(cls) -> BaseContainer:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def browser(self) -> Browser | None:
        """Return the current browser instance or None if not started."""
        return self._browser

    async def get_browser(self, headless: bool = True, slow_mo: float = 0) -> Browser:
        """Return the shared browser, launching it on first call."""
        if self._lock is None:
            self._lock = asyncio.Lock()

        lock = self._lock
        async with lock:
            if self._browser is None:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=headless,
                    slow_mo=slow_mo,
                )
        return self._browser

    async def close(self) -> None:
        """Shut down the browser and playwright process."""
        if self._lock is None:
            return

        lock = self._lock
        async with lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
