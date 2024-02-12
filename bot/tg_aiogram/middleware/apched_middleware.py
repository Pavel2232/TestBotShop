from typing import Awaitable, Dict, Callable, Any
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from apscheduler_di import ContextSchedulerDecorator


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: ContextSchedulerDecorator):
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Add apscheduler in your handler """

        data['apscheduler'] = self.scheduler
        return await handler(event, data)