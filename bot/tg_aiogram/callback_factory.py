from typing import Optional

from aiogram.filters.callback_data import CallbackData


class CategoryCallbackData(CallbackData, prefix='catg'):
    id: int


class SubCategoryCallbackData(CallbackData, prefix='sub_catg'):
    id: int


class PaginationCallbackData(CallbackData, prefix='page'):
    category: bool = False
    sub_category: bool = False
    page: int = 1
    category_id: Optional[int]


class MenuCallbackData(CallbackData, prefix='menu'):
    back: bool = False


class AddCart(CallbackData, prefix='cart'):
    product_id: int


class RemoveProductCartCallback(CallbackData, prefix='remove'):
    remove_id_quantity_product: int