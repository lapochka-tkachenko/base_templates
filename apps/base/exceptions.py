from __future__ import annotations


class BrowserError(Exception):
    """Base class for all browser-related errors."""


class BrowserNotStartedError(BrowserError):
    """Raised when accessing page/context/browser before calling start()."""


class BrowserTimeoutError(BrowserError):
    """Raised when a Playwright action exceeds the configured timeout."""


class BrowserPageError(BrowserError):
    """Raised when a Playwright page action fails (element not found, navigation error, etc.)."""


class BrowserLaunchError(BrowserError):
    """Raised when the browser process fails to start."""
