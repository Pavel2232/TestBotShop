import textwrap

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from TestBotShop.settings import env
from bot.models import ProductQuantity, Product, ShopCart, TgUser
from bot.tg_aiogram.callback_factory import RemoveProductCartCallback, AddCart
from bot.tg_aiogram.heandlers.apchendler import check_status_pay
from bot.tg_aiogram.keyboards.inline import get_price_subscribe
from bot.tg_aiogram.keyboards.reply import delivery, submit
from create_pay import create_pay_iokassa
from save_to_excel import save_emails_and_ids

shop_cart_router = Router(name=__name__)


@sync_to_async
def get_quantity_products(shop_cart_id: int):
    quantity_products = ProductQuantity.objects.filter(
        shop_cart_id=shop_cart_id
    ).exclude(shop_cart__status=False)
    return list(quantity_products)


class ShopCartState(StatesGroup):
    start = State()
    remove_product = State()
    shop_cart = State()
    confirm = State()
    delivery = State()
    waiting_email = State()
    confirm_email = State()
    quantity_product = State()


@shop_cart_router.message(F.text == '🗑Корзина')
async def shop_cart(message: Message, state: FSMContext):
    await state.set_state(ShopCartState.shop_cart)
    shop_cart = await ShopCart.objects.exclude(
        status=False
    ).aget(
        owner__telegram_id=message.chat.id
    )

    quantity_products = await get_quantity_products(shop_cart.id)
    sum_products = []
    answer = '''
    Ваша корзина:
    '''

    markup = InlineKeyboardBuilder()
    await state.set_state(ShopCartState.delivery)
    for quantity_product in quantity_products:
        product = await Product.objects.filter(
            product_quantity=quantity_product
        ).afirst()

        answer += f'{product.name}-{quantity_product.quantity}'
        sum_products.append(quantity_product.quantity * quantity_product.price)

        markup.button(
            text=f'Убрать {product.name}',
            callback_data=RemoveProductCartCallback(
                remove_id_quantity_product=quantity_product.id
            )
        )
    markup.adjust(1)
    shop_cart.total_price = sum(sum_products)
    await shop_cart.asave()

    answer += f'Общая сумма: {shop_cart.total_price}'

    await message.answer(
        textwrap.dedent(
            text=answer
        ),
        reply_markup=markup.as_markup()
    )
    await message.answer('Оформить доставку', reply_markup=delivery())


@shop_cart_router.callback_query(RemoveProductCartCallback.filter())
async def delete_product(
        call: CallbackQuery, callback_data: RemoveProductCartCallback,
        state: FSMContext):
    quantity_product = await ProductQuantity.objects.aget(
        id=callback_data.remove_id_quantity_product
    )

    await state.set_state(ShopCartState.remove_product)
    await quantity_product.adelete()
    await shop_cart(call.message, state)


@shop_cart_router.message(ShopCartState.delivery)
async def survey_user(message: Message,
                      state: FSMContext):
    await message.answer('Введите вашу почту')
    await state.set_state(ShopCartState.waiting_email)


@shop_cart_router.message(ShopCartState.waiting_email)
async def get_email(message: Message,
                    state: FSMContext,
                    apscheduler: AsyncIOScheduler):
    try:
        validate_email(message.text)
        await state.clear()
        await state.set_state(ShopCartState.start)
        filename = f'{env.str("FILE_NAME")}.xlsx'
        save_emails_and_ids(
            [(f'{message.from_user.id}', f'{message.from_user.username}')],
            filename
        )

        url, payment_id = create_pay_iokassa(100)
        apscheduler.add_job(
            check_status_pay,
            kwargs={'chat_id': message.from_user.id, 'payment_id': payment_id},
            replace_existing=True)
        await message.answer('''
       Спасибо за заказ!
       Ожидайте подтверждения по почте!''',
                             reply_markup=get_price_subscribe(
                                 url, 100
                             )
                             )

    except ValidationError:
        await message.answer(textwrap.dedent('''
Некорректная почта.
Введите почту в формате: user@mail.ru''')
                             )


@shop_cart_router.callback_query(AddCart.filter())
async def add_product(call: CallbackQuery,
                      callback_data: AddCart,
                      state: FSMContext):
    product = await Product.objects.aget(id=callback_data.product_id)

    user, _ = await TgUser.objects.aget_or_create(
        telegram_id=call.from_user.id
    )
    shop_cart, _ = await ShopCart.objects.exclude(status=False).aget_or_create(
        owner=user,
    )
    product_quantity, _ = await ProductQuantity.objects.aget_or_create(
        product=product,
        quantity=1,
        price=product.price,
        shop_cart=shop_cart
    )
    await state.update_data(product_id=product.id)
    await state.set_state(ShopCartState.quantity_product)
    await call.message.answer('Введите количество')


@shop_cart_router.message(ShopCartState.quantity_product)
async def get_quantity(message: Message, state: FSMContext):
    try:
        await state.set_state(ShopCartState.confirm)
        await message.answer(
            text=textwrap.dedent(
                f'''
        Подтвердите:
        {int(message.text)}
                    '''
            ),
            reply_markup=submit()
        )
        await state.update_data(quantity=int(message.text))
    except:
        await message.answer(
            f'Вы ввели не число {message.text}',
            reply_markup=submit()
        )


@shop_cart_router.message(ShopCartState.confirm)
async def confirm_quantity(message: Message, state: FSMContext):
    match message.text:
        case '✅Подтвердить':
            data = await state.get_data()
            product_quantity = await ProductQuantity.objects.filter(
                shop_cart__owner__telegram_id=message.from_user.id
            ).exclude(
                shop_cart__status=False
            ).filter(
                product_id=data.get('product_id')
            ).afirst()
            product_quantity.quantity = data.get('quantity')
            await product_quantity.asave()
            await message.answer(
                'Товар добавлен'
            )

        case '🔄Изменить':
            await state.set_state(ShopCartState.quantity_product)
            await message.answer('Введите количество')
