from django.contrib import admin
from .models import Entitlement, Order, OrderItem, PaymentTransaction, Product, ProductCategory
class OrderItemInline(admin.TabularInline): model=OrderItem; extra=0
class PaymentTransactionInline(admin.TabularInline): model=PaymentTransaction; extra=0; readonly_fields=('created_at','updated_at')
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin): list_display=('name','slug','sort_order'); prepopulated_fields={'slug':('name',)}
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): list_display=('name','product_type','price_rub','duration_days','is_active','is_featured','sort_order'); list_filter=('product_type','is_active','is_featured','category'); search_fields=('name','description'); prepopulated_fields={'slug':('name',)}
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): list_display=('id','profile','status','total_rub','customer_email','created_at'); list_filter=('status','created_at'); search_fields=('profile__steam_id','profile__nickname','customer_email'); inlines=[OrderItemInline,PaymentTransactionInline]
@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin): list_display=('order','provider','provider_payment_id','status','amount_rub','created_at'); search_fields=('provider_payment_id','order__profile__steam_id'); list_filter=('provider','status')
@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin): list_display=('profile','product','status','starts_at','expires_at'); search_fields=('profile__steam_id','profile__nickname','product__name'); list_filter=('status','product')
