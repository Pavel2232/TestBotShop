import asyncio
import textwrap
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from yookassa import Payment

from bot.models import ShopCart


async def check_status_pay(bot: Bot, chat_id: int, payment_id: str):
    """Async task to check whether the payment went through"""
    payment = Payment.find_one(payment_id)

    while payment.status == 'pending':
        payment = Payment.find_one(payment_id)
        await asyncio.sleep(5)

    if payment.status == 'succeeded':
        try:
            shop_cart = await ShopCart.objects.exclude(
                status=False
            ).filter(
                owner_id=chat_id
            ).afirst()
            shop_cart.status = False
            await shop_cart.asave()
            await bot.send_message(chat_id=chat_id, text=textwrap.dedent(f'''
Оплата прошла успешно
'''
                                                                         )
                                   )
        except TelegramForbiddenError:
            pass
    else:
        try:
            await bot.send_message(chat_id=chat_id, text=f'Оплата не прошла, попробуйте ещё раз')
        except TelegramForbiddenError:
            pass
