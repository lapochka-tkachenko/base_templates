from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from apps.base.exceptions import BrowserPageError, BrowserTimeoutError

if TYPE_CHECKING:
    from apps.base.typing import AnyCallable


def handle_playwright_errors(func: AnyCallable) -> AnyCallable:
    """Wrap async methods to convert Playwright exceptions into domain exceptions."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(func.__name__) from e
        except PlaywrightError as e:
            raise BrowserPageError(func.__name__) from e

    return wrapper  # type: ignore[return-value]
