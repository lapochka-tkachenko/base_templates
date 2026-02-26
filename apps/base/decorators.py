from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from apps.base.exceptions import BrowserPageError, BrowserTimeoutError

if TYPE_CHECKING:
    from collections.abc import Callable

    from apps.base.typing import AnyCallable


class OnError:
    """Namespace of composable async error-handling decorators.

    All factory methods use keyword-only arguments to keep call sites explicit:

        @OnError.returns(default=False, catch=BrowserTimeoutError)
        async def _is_authenticated(self) -> bool: ...

        @OnError.suppress(catch=BrowserTimeoutError)
        async def _accept_cookies(self) -> None: ...

        @OnError.reraise_as(catch=BrowserTimeoutError, target=InstagramLoginError)
        async def _password_login(self, ...) -> None: ...

        @OnError.playwright_errors
        async def navigate(self, ...) -> None: ...

    Note: in reraise_mapping pass more-specific subtypes before their base types.
    """

    @staticmethod
    def _wrap(
        func: AnyCallable,
        catch: type[Exception] | tuple[type[Exception], ...],
        on_catch: Callable[[Exception], Any],
    ) -> AnyCallable:
        if not asyncio.iscoroutinefunction(func):
            msg = f'OnError decorators require an async function, got {func!r}'
            raise TypeError(msg)

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except catch as error:
                return on_catch(error)

        return wrapper  # type: ignore[return-value]

    @staticmethod
    def returns(
        *,
        default: Any,
        catch: type[Exception] | tuple[type[Exception], ...],
    ) -> Callable[[AnyCallable], AnyCallable]:
        """Return *default* instead of propagating *catch* exception(s)."""

        def on_catch(_error: Exception) -> Any:
            return default

        def decorator(func: AnyCallable) -> AnyCallable:
            return OnError._wrap(func, catch, on_catch)

        return decorator

    @staticmethod
    def suppress(
        *,
        catch: type[Exception] | tuple[type[Exception], ...],
    ) -> Callable[[AnyCallable], AnyCallable]:
        """Silently suppress *catch* exception(s)."""

        def on_catch(_error: Exception) -> None:
            pass

        def decorator(func: AnyCallable) -> AnyCallable:
            return OnError._wrap(func, catch, on_catch)

        return decorator

    @staticmethod
    def reraise_as(
        *,
        catch: type[Exception],
        target: type[Exception],
    ) -> Callable[[AnyCallable], AnyCallable]:
        """Re-raise *catch* exception as *target*.

        Shorthand for ``reraise_mapping`` when only one exception type needs remapping.
        """
        return OnError.reraise_mapping({catch: target})

    @staticmethod
    def reraise_mapping(
        mapping: dict[type[Exception], type[Exception]],
    ) -> Callable[[AnyCallable], AnyCallable]:
        """Re-raise each caught exception as the mapped target type.

        The message ``'<func_name>: <original>'`` is preserved.
        More specific subtypes must appear before their base types in *mapping*.
        """
        catch_types = tuple(mapping)

        def decorator(func: AnyCallable) -> AnyCallable:
            def on_catch(error: Exception) -> None:
                for exc_type, target_type in mapping.items():
                    if isinstance(error, exc_type):
                        msg = f'{func.__name__}: {error}'
                        raise target_type(msg) from error
                raise error  # unreachable — satisfies type checker

            return OnError._wrap(func, catch_types, on_catch)

        return decorator

    @staticmethod
    def playwright_errors(func: AnyCallable) -> AnyCallable:
        """Convert Playwright exceptions to domain browser errors.

        PlaywrightTimeoutError -> BrowserTimeoutError
        PlaywrightError        -> BrowserPageError
        """
        return OnError.reraise_mapping(
            {
                PlaywrightTimeoutError: BrowserTimeoutError,
                PlaywrightError: BrowserPageError,
            }
        )(func)
