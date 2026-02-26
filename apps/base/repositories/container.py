from __future__ import annotations

import asyncio

from playwright.async_api import Browser, Playwright, async_playwright

from apps.base.decorators import OnError
from apps.base.exceptions import BrowserLaunchError


class BaseContainer:
    """Singleton container for one browser."""

    _instance: BaseContainer | None = None
    _playwright: Playwright | None = None
    _browser: Browser | None = None
    _lock: asyncio.Lock

    def __new__(cls) -> BaseContainer:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._lock = asyncio.Lock()
            cls._instance = instance
        return cls._instance

    @property
    def browser(self) -> Browser | None:
        """Return the current browser instance or None if not started."""
        return self._browser

    async def get_browser(self, *, headless: bool = True, slow_mo: float = 0) -> Browser:
        """Return the shared browser, launching it on first call."""
        async with self._lock:
            if self._browser is None:
                try:
                    await self._launch_browser(headless=headless, slow_mo=slow_mo)
                except BrowserLaunchError:
                    if self._playwright is not None:
                        await self._playwright.stop()
                        self._playwright = None
                    raise
        return self._browser  # type: ignore[return-value]

    @OnError.reraise_as(catch=Exception, target=BrowserLaunchError)
    async def _launch_browser(self, *, headless: bool, slow_mo: float) -> None:
        """Start Playwright and launch Chromium. Raises BrowserLaunchError on any failure."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
        )

    async def close(self) -> None:
        """Shut down the browser and playwright process."""
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
