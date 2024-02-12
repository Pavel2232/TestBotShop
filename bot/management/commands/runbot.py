import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from django.core.management import BaseCommand
from TestBotShop.settings import env
from bot.tg_aiogram.heandlers.catalog import catalog_router
from bot.tg_aiogram.heandlers.faq import faq_router
from bot.tg_aiogram.heandlers.shop_cart import shop_cart_router
from bot.tg_aiogram.middleware.apched_middleware import SchedulerMiddleware


async def main():
    logger = logging.getLogger('Tg')
    logger.setLevel(logging.CRITICAL)  # Установка уровня логирования на CRITICAL

    # Создание обработчика
    handler = RotatingFileHandler('critical_errors.txt', maxBytes=1024, backupCount=5)
    handler.setLevel(logging.CRITICAL)  # Установка уровня логирования на CRITICAL

    # Создание форматтера
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Добавление обработчика к логгеру


    bot = Bot(env.str('TG_TOKEN_BOT'))
    storage = RedisStorage.from_url(env.str('REDIS_URL'))
    dp = Dispatcher(storage=storage)

    jobstores = {
        'default': RedisJobStore(

            host=env('REDIS_HOST'),

            port=env('REDIS_PORT')
        )
    }

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(
            timezone="Europe/Moscow",
            jobstores=jobstores
        )
    )

    scheduler.ctx.add_instance(bot, declared_class=Bot)

    scheduler.start()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    dp.include_routers(catalog_router)
    dp.include_routers(shop_cart_router)
    dp.include_routers(faq_router)

    try:
        await dp.start_polling(bot)
    except TelegramNetworkError:
        logging.critical('Нет интернета')
    logger.addHandler(handler)

class Command(BaseCommand):

    def handle(self, *args, **options):
        asyncio.run(main())
