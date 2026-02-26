from __future__ import annotations

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from apps.base.decorators import OnError
from apps.base.exceptions import BrowserPageError, BrowserTimeoutError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _SentinelError(Exception):
    """Arbitrary domain exception used in tests below."""


class _SubSentinelError(_SentinelError):
    """Subclass of _SentinelError to test isinstance ordering."""


_PLAYWRIGHT_MAP: dict[type[Exception], type[Exception]] = {
    PlaywrightTimeoutError: BrowserTimeoutError,
    PlaywrightError: BrowserPageError,
}


# ---------------------------------------------------------------------------
# Tests: OnError.reraise_mapping with Playwright errors
# ---------------------------------------------------------------------------

@OnError.reraise_mapping(_PLAYWRIGHT_MAP)
async def _raises_timeout() -> None:
    raise PlaywrightTimeoutError('timed out')


@OnError.reraise_mapping(_PLAYWRIGHT_MAP)
async def _raises_playwright_error() -> None:
    raise PlaywrightError('something went wrong')


@OnError.reraise_mapping(_PLAYWRIGHT_MAP)
async def _returns_value() -> int:
    return 42


@pytest.mark.asyncio
async def test_wraps_playwright_timeout_as_browser_timeout_error():
    with pytest.raises(BrowserTimeoutError):
        await _raises_timeout()


@pytest.mark.asyncio
async def test_wraps_playwright_error_as_browser_page_error():
    with pytest.raises(BrowserPageError):
        await _raises_playwright_error()


@pytest.mark.asyncio
async def test_preserves_original_exception_as_cause():
    with pytest.raises(BrowserTimeoutError) as exc_info:
        await _raises_timeout()
    assert isinstance(exc_info.value.__cause__, PlaywrightTimeoutError)


@pytest.mark.asyncio
async def test_passes_through_return_value():
    result = await _returns_value()
    assert result == 42


@pytest.mark.asyncio
async def test_exception_message_contains_function_name():
    with pytest.raises(BrowserTimeoutError) as exc_info:
        await _raises_timeout()
    assert '_raises_timeout' in str(exc_info.value)


# ---------------------------------------------------------------------------
# Tests: OnError.returns
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_returns_default_when_exception_is_caught():
    @OnError.returns(default=-1, catch=_SentinelError)
    async def _func() -> int:
        raise _SentinelError

    assert await _func() == -1


@pytest.mark.asyncio
async def test_returns_default_for_subclass_of_caught_exception():
    @OnError.returns(default='fallback', catch=_SentinelError)
    async def _func() -> str:
        raise _SubSentinelError

    assert await _func() == 'fallback'


@pytest.mark.asyncio
async def test_returns_passes_through_return_value_on_success():
    @OnError.returns(default=-1, catch=_SentinelError)
    async def _func() -> int:
        return 99

    assert await _func() == 99


@pytest.mark.asyncio
async def test_returns_does_not_suppress_unrelated_exceptions():
    @OnError.returns(default=-1, catch=_SentinelError)
    async def _func() -> int:
        raise ValueError('unrelated')

    with pytest.raises(ValueError):
        await _func()


@pytest.mark.asyncio
async def test_returns_accepts_tuple_of_exception_types():
    @OnError.returns(default=0, catch=(ValueError, TypeError))
    async def _raises_value_error() -> int:
        raise ValueError

    @OnError.returns(default=0, catch=(ValueError, TypeError))
    async def _raises_type_error() -> int:
        raise TypeError

    assert await _raises_value_error() == 0
    assert await _raises_type_error() == 0


@pytest.mark.asyncio
async def test_returns_preserves_function_name():
    @OnError.returns(default=None, catch=_SentinelError)
    async def my_special_function() -> None:
        pass

    assert my_special_function.__name__ == 'my_special_function'


# ---------------------------------------------------------------------------
# Tests: OnError.suppress
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_suppress_swallows_caught_exception():
    @OnError.suppress(catch=_SentinelError)
    async def _func() -> None:
        raise _SentinelError

    await _func()  # must not raise


@pytest.mark.asyncio
async def test_suppress_swallows_subclass_of_caught_exception():
    @OnError.suppress(catch=_SentinelError)
    async def _func() -> None:
        raise _SubSentinelError

    await _func()  # must not raise


@pytest.mark.asyncio
async def test_suppress_returns_none_on_suppressed_exception():
    @OnError.suppress(catch=_SentinelError)
    async def _func() -> str:
        raise _SentinelError

    result = await _func()
    assert result is None


@pytest.mark.asyncio
async def test_suppress_passes_through_return_value_on_success():
    @OnError.suppress(catch=_SentinelError)
    async def _func() -> str:
        return 'ok'

    assert await _func() == 'ok'


@pytest.mark.asyncio
async def test_suppress_does_not_swallow_unrelated_exceptions():
    @OnError.suppress(catch=_SentinelError)
    async def _func() -> None:
        raise RuntimeError('unrelated')

    with pytest.raises(RuntimeError):
        await _func()


@pytest.mark.asyncio
async def test_suppress_preserves_function_name():
    @OnError.suppress(catch=_SentinelError)
    async def my_special_function() -> None:
        pass

    assert my_special_function.__name__ == 'my_special_function'


# ---------------------------------------------------------------------------
# Tests: OnError.reraise_mapping
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reraise_mapping_converts_exception_to_target_type():
    @OnError.reraise_mapping({_SentinelError: ValueError})
    async def _func() -> None:
        raise _SentinelError('original')

    with pytest.raises(ValueError):
        await _func()


@pytest.mark.asyncio
async def test_reraise_mapping_preserves_cause():
    @OnError.reraise_mapping({_SentinelError: ValueError})
    async def _func() -> None:
        raise _SentinelError('original')

    with pytest.raises(ValueError) as exc_info:
        await _func()
    assert isinstance(exc_info.value.__cause__, _SentinelError)


@pytest.mark.asyncio
async def test_reraise_mapping_message_contains_function_name():
    @OnError.reraise_mapping({_SentinelError: ValueError})
    async def my_func() -> None:
        raise _SentinelError('details')

    with pytest.raises(ValueError) as exc_info:
        await my_func()
    assert 'my_func' in str(exc_info.value)


@pytest.mark.asyncio
async def test_reraise_mapping_respects_isinstance_ordering_for_subclass():
    # _SubSentinelError is listed first — must map to ValueError, not TypeError
    @OnError.reraise_mapping({
        _SubSentinelError: ValueError,
        _SentinelError: TypeError,
    })
    async def _func() -> None:
        raise _SubSentinelError

    with pytest.raises(ValueError):
        await _func()


@pytest.mark.asyncio
async def test_reraise_mapping_passes_through_return_value_on_success():
    @OnError.reraise_mapping({_SentinelError: ValueError})
    async def _func() -> int:
        return 7

    assert await _func() == 7


@pytest.mark.asyncio
async def test_reraise_mapping_does_not_catch_unmapped_exceptions():
    @OnError.reraise_mapping({_SentinelError: ValueError})
    async def _func() -> None:
        raise RuntimeError('not in mapping')

    with pytest.raises(RuntimeError):
        await _func()
