from __future__ import annotations

import asyncio
import random

from apps.base.decorators import OnError
from apps.base.repositories.base import BasePlaywrightRepository


class HumanPlaywrightRepository(BasePlaywrightRepository):
    """Repository with human-like mouse movements and typing behaviour.

    All mouse.move() calls dispatch real mousemove events inside the browser,
    so from social's perspective the cursor moves exactly like a real user
    would move it. The OS cursor on the local screen does not move — that is
    only a visual limitation of the local machine and has no effect on what
    the site observes.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        slow_mo: float = 0,
        timeout: float = 30_000,
    ) -> None:
        super().__init__(headless=headless, slow_mo=slow_mo, timeout=timeout)
        self._mouse_x: float = 0.0
        self._mouse_y: float = 0.0

    async def _move_to(self, x: float, y: float) -> None:
        """Move mouse from current position to (x, y) through a random midpoint, step by step."""
        mid_x = (self._mouse_x + x) / 2 + random.uniform(-80, 80)  # noqa: S311
        mid_y = (self._mouse_y + y) / 2 + random.uniform(-80, 80)  # noqa: S311

        for segment_x, segment_y in ((mid_x, mid_y), (x, y)):
            steps = 10
            for i in range(1, steps + 1):
                curr_x = self._mouse_x + (segment_x - self._mouse_x) * i / steps
                curr_y = self._mouse_y + (segment_y - self._mouse_y) * i / steps
                await self.page.mouse.move(curr_x, curr_y)
                await asyncio.sleep(0.01)
            self._mouse_x = segment_x
            self._mouse_y = segment_y

        self._mouse_x = x
        self._mouse_y = y

    @OnError.playwright_errors
    async def click(self, *, selector: str) -> None:
        """Move mouse smoothly to a random point inside the element, then click."""
        element = await self.page.query_selector(selector)
        if element is None:
            await self.page.click(selector)
            return

        box = await element.bounding_box()
        if box is None:
            await self.page.click(selector)
            return

        x = box['x'] + random.uniform(box['width'] * 0.2, box['width'] * 0.8)  # noqa: S311
        y = box['y'] + random.uniform(box['height'] * 0.2, box['height'] * 0.8)  # noqa: S311

        await self._move_to(x, y)
        await asyncio.sleep(random.uniform(0.05, 0.15))  # noqa: S311
        await self.page.mouse.click(x, y)

    @OnError.playwright_errors
    async def fill(self, *, selector: str, value: str) -> None:
        """Click the field and type each character with a random delay."""
        await self.click(selector=selector)
        for char in value:
            await self.page.keyboard.type(char)
            await asyncio.sleep(random.uniform(0.05, 0.2))  # noqa: S311

    @staticmethod
    async def human_delay() -> None:
        """Random pause between actions (0.3-1.2 s)."""
        await asyncio.sleep(random.uniform(0.3, 1.2))  # noqa: S311
