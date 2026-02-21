from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractBrowserRepository(ABC):
    async def __aenter__(self) -> AbstractBrowserRepository:
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    @abstractmethod
    async def start(self) -> None:
        """Launch browser and open page."""

    @abstractmethod
    async def close(self) -> None:
        """Close browser and release resources."""

    @abstractmethod
    async def navigate(self, *, url: str, wait_until: str = 'networkidle') -> None:
        """Navigate to url."""

    @abstractmethod
    async def screenshot(self, *, path: str) -> None:
        """Take a full-page screenshot and save to path."""

    @abstractmethod
    async def wait_for_selector(self, *, selector: str, timeout: float | None = None) -> None:
        """Wait until selector appears on the page."""

    @abstractmethod
    async def fill(self, *, selector: str, value: str) -> None:
        """Fill input field."""

    @abstractmethod
    async def click(self, *, selector: str) -> None:
        """Click element."""

    @abstractmethod
    async def get_text(self, *, selector: str) -> str:
        """Return inner text of element."""

    @abstractmethod
    async def save_cookies(self, *, username: str) -> None:
        """Save current browser cookies to a JSON file keyed by username."""

    @abstractmethod
    async def load_cookies(self, *, username: str) -> bool:
        """Load cookies from JSON file into browser context. Returns True if file exists."""
