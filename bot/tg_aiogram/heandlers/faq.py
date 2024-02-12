import textwrap

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.db.models import Q

from bot.models import FAQ

faq_router = Router(name=__name__)


@sync_to_async
def get_questions(words: list[str]):
    query = Q()
    for word in words:
        query |= Q(question__icontains=word)
    return list(FAQ.objects.filter(query))


class FAQState(StatesGroup):
    ask = State()


@faq_router.message(F.text == '💬FAQ')
async def question(message: Message, state: FSMContext):
    await state.set_state(FAQState.ask)
    await message.answer('Задайте вопрос')


@faq_router.message(FAQState.ask)
async def return_qua(message: Message):
    faqs = await get_questions(message.text.split(' '))
    if faqs:
        for faq in faqs:
            await message.answer(
                textwrap.dedent(
                    text=f'''
        {faq.question}?
        {faq.answer}
        '''
                )
            )
    if not faqs:
        await FAQ.objects.aget_or_create(
            question=message.text,
            answer='Надо ответить!'
        )
        await message.answer('Вопрос отправлен')
