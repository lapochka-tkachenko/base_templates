from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from apps.base.typing import WaitUntil


class AbstractBrowserRepository(ABC):
    async def __aenter__(self) -> Self:
        """Initialize the async context manager by starting the browser."""
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        """Clean up resources when exiting the async context manager."""
        await self.close()

    @abstractmethod
    async def start(self) -> None:
        """Launch browser and open page."""

    @abstractmethod
    async def close(self) -> None:
        """Close browser and release resources."""

    @abstractmethod
    async def navigate(self, *, url: str, wait_until: WaitUntil = 'domcontentloaded') -> None:
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
    async def press_enter(self) -> None:
        """Press the Enter key on the current page.

        Useful for accepting cookie consent dialogs or submitting forms
        when a visible submit button is not available.
        """

    @abstractmethod
    async def save_cookies(self, *, username: str) -> None:
        """Save current browser cookies to a JSON file keyed by username."""

    @abstractmethod
    async def load_cookies(self, *, username: str) -> bool:
        """Load cookies from JSON file into browser context. Returns True if file exists."""

    @abstractmethod
    async def get_url(self) -> str:
        """Return the current page URL."""

    @abstractmethod
    async def wait_for_url_change(self, *, away_from: str, timeout: float | None = None) -> None:
        """Wait until the current URL no longer contains away_from."""

    @abstractmethod
    async def reload(self) -> None:
        """Reload the current page."""

    @abstractmethod
    async def upload_file(self, *, trigger_selector: str, file_path: str) -> None:
        """Click trigger_selector and set file_path on the file chooser that opens."""

    @abstractmethod
    async def count_elements(self, *, selector: str) -> int:
        """Return the number of elements matching selector currently in the DOM."""
