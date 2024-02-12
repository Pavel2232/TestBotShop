from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from bot.models import Category, SubCategory, Product
from bot.tg_aiogram.callback_factory import CategoryCallbackData, SubCategoryCallbackData, AddCart, MenuCallbackData



@sync_to_async
def get_categories() -> list[QuerySet]:
    categories = Category.objects.all()
    return list(categories)


@sync_to_async
def get_sub_category(category_id: int) -> list[QuerySet[SubCategory]]:
    sub_categories = SubCategory.objects.filter(category_id=category_id)
    return list(sub_categories)


@sync_to_async
def get_products(sub_category_id: int) -> list[QuerySet[Product]]:
    sub_categories = Product.objects.filter(subcategory_id=sub_category_id)
    return list(sub_categories)


async def get_category_inline() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()

    categories = await get_categories()
    for category in categories:
        markup.button(
            text=category.name,
            callback_data=CategoryCallbackData(id=category.id)
        )

    markup.adjust(1)

    return markup.as_markup()


async def get_sub_category_inline(category_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()

    sub_categories = await get_sub_category(category_id=category_id)

    for sub_category in sub_categories:
        markup.button(
            text=sub_category.name,
            callback_data=SubCategoryCallbackData(id=sub_category.id)
        )

    markup.adjust(1)

    return markup.as_markup()


def add_product_shop_cart(product_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()

    markup.button(
        text='Добавить в корзину',
        callback_data=AddCart(
            product_id=product_id
        )
    )


    markup.button(
        text="Вернуться в меню",
        callback_data=MenuCallbackData(back=True).pack()
    )

    markup.adjust(1)
    return markup.as_markup()


def get_price_subscribe(url: str, price: int) -> InlineKeyboardMarkup:
    """
    Create inline keyboards with payment link
    :param url: url payment link
    :return: keyboards
    """
    markup = InlineKeyboardBuilder()

    cost = price
    markup.button(
        text=f'Tggg {cost} руб.',
        url=url
    )

    return markup.as_markup()