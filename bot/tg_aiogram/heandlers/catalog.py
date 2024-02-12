import textwrap
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from asgiref.sync import sync_to_async

from TestBotShop.settings import env
from bot.models import Product, TgUser
from bot.tg_aiogram.callback_factory import (PaginationCallbackData,
                                             CategoryCallbackData,
                                             MenuCallbackData,
                                             SubCategoryCallbackData)
from bot.tg_aiogram.configure_bot.commands import set_commands
from bot.tg_aiogram.keyboards.inline import (get_category_inline,
                                             get_sub_category_inline,
                                             add_product_shop_cart
                                             )
from bot.tg_aiogram.keyboards.reply import get_start_buttons
from bot.tg_aiogram.pagination import paginate_markup


catalog_router = Router(name=__name__)


class UserState(StatesGroup):
    back_manu = State()
    start = State()
    category = State()
    sub_category = State()
    product = State()



@sync_to_async
def get_products(sub_category_id: int):
    sub_categories = Product.objects.filter(subcategory_id=sub_category_id)
    return list(sub_categories)


@catalog_router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext):
    await state.set_state(UserState.start)
    await set_commands(message.bot)

    await TgUser.objects.aget_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    user_channel_status = await message.bot.get_chat_member(
        chat_id=env('CHANEL_ID'),
        user_id=message.from_user.id
    )

    user_group_chanel = await message.bot.get_chat_member(
        chat_id=env('GROUP_ID'),
        user_id=message.from_user.id
    )

    if user_channel_status.status and user_group_chanel.status != 'left':
        await message.answer(
            text='Добро пожаловать',
            reply_markup=get_start_buttons()
        )

        await message.answer(
            textwrap.dedent(
                '''
    Выберите категорию:
    '''
            ), reply_markup=await paginate_markup(
                markup=await get_category_inline(),
                category=True
            )
        )
    else:
        await message.answer('Вы еще не подписались!')


@catalog_router.callback_query(PaginationCallbackData.filter(F.category == True))
async def category_pagination(call: CallbackQuery,
                              callback_data: PaginationCallbackData,
                              state: FSMContext):
    await state.set_state(UserState.category)
    await call.message.edit_reply_markup(
        reply_markup=await paginate_markup(
            markup=await get_category_inline(),
            page=callback_data.page,
            category=True
        )
    )


@catalog_router.callback_query(PaginationCallbackData.filter(F.sub_category == True))
async def sub_category_pagination(call: CallbackQuery, callback_data: PaginationCallbackData, state: FSMContext):
    await state.set_state(UserState.sub_category)
    await call.message.edit_reply_markup(
        reply_markup=await paginate_markup(
            markup=await get_sub_category_inline(category_id=callback_data.category_id),
            page=callback_data.page,
            sub_category=True,
            category_id=callback_data.category_id
        )
    )


@catalog_router.callback_query(CategoryCallbackData.filter())
async def sub_category_query(call: CallbackQuery, callback_data: CategoryCallbackData, state: FSMContext):
    await state.set_state(UserState.sub_category)
    await call.message.edit_reply_markup(
        reply_markup=await paginate_markup(
            markup=await get_sub_category_inline(category_id=callback_data.id),
            sub_category=True,
            category_id=callback_data.id
        )
    )


@catalog_router.callback_query(SubCategoryCallbackData.filter())
async def get_product_query(call: CallbackQuery,
                            callback_data: SubCategoryCallbackData,
                            state: FSMContext):
    await state.set_state(UserState.product)
    products = await get_products(sub_category_id=callback_data.id)

    for product in products:
        image = FSInputFile(
            product.photo.path
        )

        await call.message.answer_photo(
            photo=image,
            caption=textwrap.dedent(
                '''
{name}
{descriprion}''').format(
                name=product.name,
                descriprion=product.description[:150]),
            reply_markup=add_product_shop_cart(product.id)
        )


@catalog_router.callback_query(MenuCallbackData.filter(F.back == True))
async def menu(call: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.back_manu)
    await call.message.edit_reply_markup(
        reply_markup=await paginate_markup(
            markup=await get_category_inline(),
            category=True
        )
    )
