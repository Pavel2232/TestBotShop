import requests
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html

from TestBotShop.settings import env
from .models import (Category, SubCategory, Product,
                     ProductQuantity, ShopCart, TgUser, Notification, FAQ)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'image_preview')
    list_filter = ('subcategory__category', 'subcategory')
    search_fields = (
        'name',
        'subcategory__name',
        'subcategory__category__name'
    )

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.photo.url)
        else:
            return '(No photo)'

    image_preview.short_description = 'Preview'


class ProductQuantityInline(admin.TabularInline):
    model = ProductQuantity
    extra = 1


@admin.register(ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ('owner', 'total_price', 'status')
    list_filter = ('status',)
    search_fields = ('owner__telegram_id',)
    inlines = [ProductQuantityInline]


@admin.register(ProductQuantity)
class ProductQuantityAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price', 'shop_cart')
    list_filter = ('shop_cart__status',)
    search_fields = ('product__name',)


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('telegram_id', 'username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('telegram_id', 'username')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'created_at',
        'sent',
        'send_notification_via_telegram'
    )
    list_filter = ('sent',)

    def send_notification_via_telegram(self, obj):
        if obj.sent:
            return "Отправлено"
        else:
            url = reverse(
                'admin:send_notification_via_telegram',
                args=[obj.pk]
            )
            return format_html(
                '<a href="{}">Отправить через Telegram</a>',
                url
            )

    send_notification_via_telegram.allow_tags = True
    send_notification_via_telegram.short_description = "Отправка через Telegram"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'send_via_telegram/<int:pk>/',
                self.send_notification_via_telegram_view,
                name='send_notification_via_telegram'
            ),
        ]
        return custom_urls + urls

    def send_notification_via_telegram_view(self, request, pk):
        notification = Notification.objects.get(pk=pk)
        users = TgUser.objects.all()
        if notification.sent:
            self.message_user(
                request,
                f'Уведомление для уже отправлено через Telegram.'
            )
        else:
            for user in users:
                response = requests.post(
                    f'https://api.telegram.org/bot{env.str("TG_TOKEN_BOT")}/sendMessage',
                    json={
                        'chat_id': user.telegram_id,
                        'text': notification.message
                    }
                )
                response.raise_for_status()
                if response.status_code == 200:
                    notification.sent = True
                    notification.save()
                    self.message_user(
                        request,
                        f'Уведомление успешно отправлено через Telegram.'
                    )
                else:
                    pass
        return HttpResponseRedirect(
            reverse(
                'admin:bot_notification_changelist'
            )
        )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'frequency')
    search_fields = ('question', 'answer')
    list_filter = ('frequency',)
