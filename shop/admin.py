from django.contrib import admin

from .models import (
    Entitlement,
    Order,
    OrderItem,
    PaymentTransaction,
    Product,
    ProductCategory,
    ProductContentItem,
)


class ProductContentItemInline(admin.TabularInline):
    model = ProductContentItem
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'icon',
        'is_active',
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'name',
        'slug',
        'description',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'product_type',
        'price_rub',
        'old_price_rub',
        'duration_days',
        'promo_duration_days',
        'is_active',
        'is_featured',
        'created_at',
    )
    list_filter = (
        'product_type',
        'category',
        'is_active',
        'is_featured',
        'created_at',
    )
    search_fields = (
        'name',
        'slug',
        'short_description',
        'description',
        'detail_lines',
        'how_to_get',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (
            'Основное',
            {
                'fields': (
                    'category',
                    'name',
                    'slug',
                    'product_type',
                    'image',
                    'is_active',
                    'is_featured',
                )
            },
        ),
        (
            'Описание и отображение',
            {
                'fields': (
                    'short_description',
                    'description',
                    'detail_lines',
                    'how_to_get',
                    'display_amount',
                )
            },
        ),
        (
            'Цена и акция',
            {
                'fields': (
                    'price_rub',
                    'old_price_rub',
                    'duration_days',
                    'promo_duration_days',
                )
            },
        ),
        (
            'Системное',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            },
        ),
    )
    inlines = [
        ProductContentItemInline,
    ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'profile',
        'status',
        'total_rub',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'status',
        'created_at',
    )
    search_fields = (
        'profile__steam_id',
        'profile__nickname',
        'customer_email',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    inlines = [
        OrderItemInline,
        PaymentTransactionInline,
    ]


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'product',
        'status',
        'starts_at',
        'expires_at',
    )
    list_filter = (
        'status',
        'product',
    )
    search_fields = (
        'profile__steam_id',
        'profile__nickname',
        'product__name',
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'provider',
        'status',
        'amount_rub',
        'created_at',
    )
    list_filter = (
        'provider',
        'status',
        'created_at',
    )
    search_fields = (
        'provider_payment_id',
        'order__profile__steam_id',
        'order__profile__nickname',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )