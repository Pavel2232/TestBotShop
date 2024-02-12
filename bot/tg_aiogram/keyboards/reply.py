from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_start_buttons() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardBuilder()

    markup.button(text='🗑Корзина')

    markup.button(text='💬FAQ')

    return markup.as_markup(resize_keyboard=True)


def submit() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardBuilder()

    markup.button(text='✅Подтвердить')
    markup.button(text='🔄Изменить')

    return markup.as_markup(resize_keyboard=True, one_time_keyboard=True)


def delivery() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardBuilder()

    markup.button(text='Оформить доставку')

    return markup.as_markup(resize_keyboard=True, one_time_keyboard=True)
