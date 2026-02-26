from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from apps.base.exceptions import BrowserPageError, BrowserTimeoutError
from apps.base.repositories.human import HumanPlaywrightRepository
from tests.base.conftest import make_mock_browser


class HumanConcreteRepository(HumanPlaywrightRepository):
    pass


SELECTOR = 'button#submit'
BOX = {'x': 100.0, 'y': 200.0, 'width': 80.0, 'height': 40.0}

# With random.uniform patched to return 0.5 always:
#   x = box['x'] + uniform(width*0.2, width*0.8)  → 100 + 0.5 = 100.5
#   y = box['y'] + uniform(height*0.2, height*0.8) → 200 + 0.5 = 200.5
#   mid_x = (0 + EXPECTED_X) / 2 + 0.5           → 50.75
#   mid_y = (0 + EXPECTED_Y) / 2 + 0.5           → 100.75
EXPECTED_X = BOX['x'] + 0.5
EXPECTED_Y = BOX['y'] + 0.5
EXPECTED_MID_X = EXPECTED_X / 2 + 0.5
EXPECTED_MID_Y = EXPECTED_Y / 2 + 0.5

# _move_to uses 2 segments × 10 steps = 20 mouse.move calls total
MOVE_STEPS_PER_SEGMENT = 10
TOTAL_MOVE_CALLS = MOVE_STEPS_PER_SEGMENT * 2


# ---------------------------------------------------------------------------
# Tests: click — happy path (element + bounding box found)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_click_moves_mouse_via_midpoint_and_clicks():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.5), \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.click(selector=SELECTOR)

    # 10 steps to midpoint + 10 steps to target = 20 mouse.move calls
    assert page.mouse.move.await_count == TOTAL_MOVE_CALLS
    # last move reaches the target
    page.mouse.move.assert_any_await(EXPECTED_X, EXPECTED_Y)
    page.mouse.click.assert_awaited_once_with(EXPECTED_X, EXPECTED_Y)
    page.click.assert_not_awaited()


@pytest.mark.asyncio
async def test_click_sleeps_between_move_and_click():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    sleep_mock = AsyncMock()
    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.1), \
         patch('apps.base.repositories.human.asyncio.sleep', sleep_mock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.click(selector=SELECTOR)

    # 20 step-sleeps (0.01 each) + 1 pre-click sleep (0.1) = 21 total
    assert sleep_mock.await_count == 21
    sleep_mock.assert_any_await(0.1)


# ---------------------------------------------------------------------------
# Tests: click — fallback when element not found
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_click_falls_back_to_page_click_when_element_is_none():
    playwright, browser, context, page = make_mock_browser()
    page.query_selector = AsyncMock(return_value=None)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.click(selector=SELECTOR)

    page.click.assert_awaited_once_with(SELECTOR)
    page.mouse.move.assert_not_awaited()


@pytest.mark.asyncio
async def test_click_falls_back_to_page_click_when_bounding_box_is_none():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=None)
    page.query_selector = AsyncMock(return_value=element)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.click(selector=SELECTOR)

    page.click.assert_awaited_once_with(SELECTOR)
    page.mouse.move.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests: click — Playwright errors are converted to domain errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_click_raises_browser_timeout_error_on_playwright_timeout():
    playwright, browser, context, page = make_mock_browser()
    page.query_selector = AsyncMock(side_effect=PlaywrightTimeoutError('timeout'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            with pytest.raises(BrowserTimeoutError):
                await repo.click(selector=SELECTOR)


@pytest.mark.asyncio
async def test_click_raises_browser_page_error_on_playwright_error():
    playwright, browser, context, page = make_mock_browser()
    page.query_selector = AsyncMock(side_effect=PlaywrightError('element error'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            with pytest.raises(BrowserPageError):
                await repo.click(selector=SELECTOR)


# ---------------------------------------------------------------------------
# Tests: fill — types each character with delay 0.05–0.2
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fill_types_each_character_separately():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.5), \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.fill(selector='#input', value='hi')

    assert page.keyboard.type.await_count == 2
    page.keyboard.type.assert_any_await('h')
    page.keyboard.type.assert_any_await('i')


@pytest.mark.asyncio
async def test_fill_sleeps_after_each_character():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    sleep_mock = AsyncMock()
    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.1), \
         patch('apps.base.repositories.human.asyncio.sleep', sleep_mock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.fill(selector='#input', value='ab')

    # 20 step-sleeps from _move_to + 1 pre-click sleep + 2 typing sleeps = 23
    assert sleep_mock.await_count == 23


@pytest.mark.asyncio
async def test_fill_does_not_call_page_fill():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.5), \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.fill(selector='#input', value='hi')

    page.fill.assert_not_awaited()


@pytest.mark.asyncio
async def test_fill_clicks_before_typing():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    call_order: list[str] = []
    page.mouse.click = AsyncMock(side_effect=lambda *_: call_order.append('mouse_click'))
    page.keyboard.type = AsyncMock(side_effect=lambda _: call_order.append('type'))

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.5), \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.fill(selector='#input', value='a')

    assert call_order[0] == 'mouse_click'
    assert call_order[1] == 'type'


@pytest.mark.asyncio
async def test_fill_empty_string_types_nothing():
    playwright, browser, context, page = make_mock_browser()

    element = AsyncMock()
    element.bounding_box = AsyncMock(return_value=BOX)
    page.query_selector = AsyncMock(return_value=element)

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.5), \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.fill(selector='#input', value='')

    page.keyboard.type.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests: human_delay
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_human_delay_sleeps_with_random_duration():
    playwright, browser, context, page = make_mock_browser()

    sleep_mock = AsyncMock()
    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform', return_value=0.75), \
         patch('apps.base.repositories.human.asyncio.sleep', sleep_mock):
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.human_delay()

    sleep_mock.assert_awaited_once_with(0.75)


@pytest.mark.asyncio
async def test_human_delay_uses_range_0_3_to_1_2():
    """Verify uniform is called with the correct (0.3, 1.2) bounds."""
    playwright, browser, context, page = make_mock_browser()

    with patch('apps.base.repositories.container.async_playwright') as mock_pw, \
         patch('apps.base.repositories.human.random.uniform') as uniform_mock, \
         patch('apps.base.repositories.human.asyncio.sleep', new_callable=AsyncMock):
        uniform_mock.return_value = 0.5
        mock_pw.return_value.start = AsyncMock(return_value=playwright)

        async with HumanConcreteRepository() as repo:
            await repo.human_delay()

    uniform_mock.assert_called_once_with(0.3, 1.2)
