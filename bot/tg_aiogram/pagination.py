from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import ceil

from TestBotShop.settings import env
from bot.tg_aiogram.callback_factory import PaginationCallbackData, MenuCallbackData


async def paginate_markup(
    markup: InlineKeyboardMarkup, page: int = None,
        category: bool = False, sub_category: bool = False,
        category_id: int = None
) -> InlineKeyboardMarkup:
    """
    Universal function for paginating InlineKeyboardMarkup
    :param markup: InlineKeyboardMarkup to paginate
    :param page: Current page
    :return: Paginated InlineKeyboardMarkup
    """
    items_per_page = env.int('DEFAULT_PAGINATION')
    if not page:
        page = 1
    if not category_id:
        category_id = 0
    total_items = len(markup.inline_keyboard)
    total_pages = ceil(total_items / items_per_page)
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    buttons = markup.inline_keyboard[start_index:end_index]

    # Add current page / total pages
    pagination_buttons = [
        InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data='ignore')
    ]

    # Previous button
    if page > 1:
        pagination_buttons.insert(
            0, InlineKeyboardButton(text='⬅️', callback_data=PaginationCallbackData(
                page=page-1,
                category=category,
                sub_category=sub_category,
                category_id=category_id
            ).pack()
                                    )
        )
    else:
        pagination_buttons.insert(0, InlineKeyboardButton(text='⬅️', callback_data='ignore'))

    # Next button
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text="➡️", callback_data=PaginationCallbackData(
                page=page + 1,
                category=category,
                sub_category=sub_category,
                category_id=category_id
            ).pack()
                                 )
        )
    else:
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data="ignore"
        )
        )

    buttons.append(pagination_buttons)

    buttons.append([InlineKeyboardButton(
        text="Вернуться в меню",
        callback_data=MenuCallbackData(back=True).pack()
    )
    ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)



