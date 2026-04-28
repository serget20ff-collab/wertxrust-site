from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import SteamProfile, WalletTransaction
from .models import Product, ProductCategory
from .models import Entitlement, Order, OrderItem, PaymentTransaction
from servers.models import RustServer


def shop_index(request):
    selected_category = request.GET.get('category', 'all')

    categories = ProductCategory.objects.filter(
        is_active=True,
    ).order_by('name')

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .prefetch_related('content_items', 'servers', 'server_categories')
        .order_by('name')
    )

    if selected_category != 'all':
        products = products.filter(category__slug=selected_category)

    return render(
        request,
        'shop/index.html',
        {
            'categories': categories,
            'products': products,
            'selected_category': selected_category,
            'servers': RustServer.objects.filter(is_public=True).order_by('sort_order', 'name'),
        },
    )


@login_required
def buy_with_wallet(request):
    if request.method != 'POST':
        return redirect('shop:shop_index')

    profile = getattr(request.user, 'steam_profile', None)
    if not profile:
        messages.error(request, 'Для покупки нужно войти через Steam.')
        return redirect('accounts:steam_login')

    try:
        product_id = int(request.POST.get('product_id', '0'))
        quantity = int(request.POST.get('quantity', '1'))
        server_id = int(request.POST.get('server_id', '0'))
    except ValueError:
        messages.error(request, 'Некорректные данные покупки.')
        return redirect('shop:shop_index')

    if quantity < 1 or quantity > 99:
        messages.error(request, 'Количество товара должно быть от 1 до 99.')
        return redirect('shop:shop_index')

    with transaction.atomic():
        locked_profile = SteamProfile.objects.select_for_update().filter(pk=profile.pk).first()
        product = Product.objects.select_for_update().filter(pk=product_id, is_active=True).first()
        selected_server = RustServer.objects.filter(pk=server_id, is_public=True).first()

        if not locked_profile or not product:
            messages.error(request, 'Товар не найден или недоступен.')
            return redirect('shop:shop_index')

        if not selected_server:
            messages.error(request, 'Выбери сервер для покупки.')
            return redirect('shop:shop_index')

        if not product.is_available_for_server(selected_server):
            messages.error(request, 'Этот товар недоступен для выбранного сервера.')
            return redirect('shop:shop_index')

        unit_price = Decimal(product.price_rub).quantize(Decimal('1'))
        total_price = (unit_price * quantity).quantize(Decimal('1'))

        if locked_profile.balance_rub < total_price:
            messages.error(
                request,
                f'Недостаточно средств. Нужно {total_price} ₽, у тебя {locked_profile.balance_rub} ₽.',
            )
            return redirect('shop:shop_index')

        locked_profile.balance_rub = (locked_profile.balance_rub - total_price).quantize(Decimal('1'))
        locked_profile.save(update_fields=['balance_rub'])

        order = Order.objects.create(
            profile=locked_profile,
            status='granting',
            selected_server=selected_server,
            total_rub=total_price,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_rub=unit_price,
        )
        PaymentTransaction.objects.create(
            order=order,
            provider='manual',
            status='wallet_paid',
            amount_rub=total_price,
            raw_payload={
                'source': 'wallet_balance',
                'quantity': quantity,
                'product_id': product.pk,
            },
        )

        now = order.created_at
        expires_at = None
        if product.duration_days and product.product_type in [Product.PRODUCT_PRIVILEGE, Product.PRODUCT_SERVICE]:
            expires_at = now + timezone.timedelta(days=product.duration_days)

        for _ in range(quantity):
            Entitlement.objects.create(
                profile=locked_profile,
                product=product,
                order=order,
                server=selected_server,
                status='pending',
                starts_at=now,
                expires_at=expires_at,
                server_payload={
                    'product_slug': product.slug,
                    'product_type': product.product_type,
                    'price_rub': str(unit_price),
                    'server_slug': selected_server.slug,
                    'steam_id': locked_profile.steam_id,
                },
            )

        WalletTransaction.objects.create(
            profile=locked_profile,
            tx_type=WalletTransaction.TX_PURCHASE,
            amount_rub=-total_price,
            balance_after_rub=locked_profile.balance_rub,
            order=order,
            description=f'Покупка: {product.name} x{quantity}',
        )

    messages.success(request, f'Покупка оформлена: {product.name} x{quantity}.')
    return redirect('accounts:purchases')


def refund_order_to_wallet(order, reason='Ошибка выдачи'):
    with transaction.atomic():
        locked_order = Order.objects.select_for_update().select_related('profile').get(pk=order.pk)

        if locked_order.status == 'refunded':
            return locked_order

        profile = SteamProfile.objects.select_for_update().get(pk=locked_order.profile_id)
        profile.balance_rub = (profile.balance_rub + locked_order.total_rub).quantize(Decimal('1'))
        profile.save(update_fields=['balance_rub'])

        locked_order.status = 'refunded'
        locked_order.delivery_error = reason
        locked_order.save(update_fields=['status', 'delivery_error', 'updated_at'])

        locked_order.entitlements.update(status='refunded', delivery_error=reason)

        WalletTransaction.objects.create(
            profile=profile,
            tx_type=WalletTransaction.TX_PURCHASE_REFUND,
            amount_rub=locked_order.total_rub,
            balance_after_rub=profile.balance_rub,
            order=locked_order,
            description=f'Возврат: {reason}',
        )

        return locked_order