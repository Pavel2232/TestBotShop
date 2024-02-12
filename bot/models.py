from django.db.models import UniqueConstraint, Q
from django.db import models


class TgUser(models.Model):
    telegram_id = models.PositiveBigIntegerField(
        unique=True,
        verbose_name='Идентификатор Telegram'
    )
    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Имя пользователя'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'

    def __str__(self):
        return f'{self.username}'


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Категория'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название подкатегории'
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        constraints = [
            UniqueConstraint(fields=['category', 'name'], name='unique_subcategory_in_category')
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Подкатегория'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название товара'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание товара'
    )
    photo = models.ImageField(
        upload_to='product_photos',
        verbose_name='Фото товара'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class ShopCart(models.Model):
    owner = models.ForeignKey(
        TgUser,
        on_delete=models.CASCADE,
        related_name='shop_cart',
        verbose_name='Покупатель',
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма корзины',
        null=True,
    )
    status = models.BooleanField(
        default=True,
        verbose_name='Статус корзины'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            UniqueConstraint(
                fields=['owner', 'status'],
                condition=Q(status=True),
                name='unique_active_cart'
            )
        ]

    def __str__(self):
        return f'{self.owner.telegram_id}'


class ProductQuantity(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_quantity',
        verbose_name='Товар Кол-во'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Кол-во'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена товара'
    )

    shop_cart = models.ForeignKey(
        ShopCart,
        on_delete=models.CASCADE,
        related_name='product_quantity',
        verbose_name='Корзина',
    )

    class Meta:
        verbose_name = 'Товар Кол-во'
        verbose_name_plural = 'Товар Кол-во'

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'


from django.db import models


class Notification(models.Model):
    message = models.TextField(
        verbose_name='Сообщение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    sent = models.BooleanField(
        default=False,
        verbose_name='Отправлено'
    )

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'Уведомление  {self.message}'


class FAQ(models.Model):
    question = models.CharField(
        max_length=255,
        verbose_name='Вопрос',
        unique=True
    )
    answer = models.TextField(
        verbose_name='Ответ'
    )
    frequency = models.PositiveIntegerField(
        default=0,
        verbose_name='Частота запроса'
    )

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question