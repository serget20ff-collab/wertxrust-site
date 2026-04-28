from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from shop.models import Order

from .models import (
    SteamLoginEvent,
    SteamProfile,
    WalletTransaction,
)
from .utils import (
    build_steam_login_url,
    fetch_steam_player_summary,
    get_client_ip,
    verify_steam_response,
)


@require_GET
def steam_login(request):
    return redirect(build_steam_login_url())


@require_GET
def steam_callback(request):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    try:
        steam_id = verify_steam_response(request.GET)
    except Exception as exc:
        SteamLoginEvent.objects.create(
            ip_address=ip,
            user_agent=user_agent,
            success=False,
            reason=f'OpenID error: {exc}',
        )
        return redirect('core:home')

    if not steam_id:
        SteamLoginEvent.objects.create(
            ip_address=ip,
            user_agent=user_agent,
            success=False,
            reason='Invalid OpenID response',
        )
        return redirect('core:home')

    summary = {}

    try:
        summary = fetch_steam_player_summary(steam_id)
    except Exception as exc:
        SteamLoginEvent.objects.create(
            steam_id=steam_id,
            ip_address=ip,
            user_agent=user_agent,
            success=False,
            reason=f'Steam API profile fetch failed: {exc}',
        )

    user, _ = User.objects.get_or_create(
        username=f'steam_{steam_id}',
        defaults={
            'first_name': summary.get('personaname', '')[:150],
        },
    )

    if not user.has_usable_password():
        user.set_unusable_password()
        user.save(update_fields=['password'])

    profile, _ = SteamProfile.objects.get_or_create(
        steam_id=steam_id,
        defaults={
            'user': user,
        },
    )

    profile.user = user
    profile.nickname = summary.get('personaname', profile.nickname)
    profile.profile_url = summary.get('profileurl', profile.profile_url)
    profile.avatar_small = summary.get('avatar', profile.avatar_small)
    profile.avatar_medium = summary.get('avatarmedium', profile.avatar_medium)
    profile.avatar_full = summary.get('avatarfull', profile.avatar_full)
    profile.real_name = summary.get('realname', profile.real_name)
    profile.country_code = summary.get('loccountrycode', profile.country_code)
    profile.persona_state = summary.get('personastate', profile.persona_state or 0)
    profile.save()
    profile.touch_login(ip=ip, user_agent=user_agent)

    SteamLoginEvent.objects.create(
        profile=profile,
        steam_id=steam_id,
        ip_address=ip,
        user_agent=user_agent,
        success=True,
        reason='OK',
    )

    login(request, user)
    return redirect('core:home')


def logout_view(request):
    logout(request)
    return redirect('core:home')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:steam_login')

    return redirect('shop:shop_index')
from django.contrib.auth.decorators import login_required


@login_required
def wallet_view(request):
    profile = getattr(request.user, 'steam_profile', None)
    if not profile:
        return redirect('accounts:steam_login')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'prepare_transfer':
            recipient_steam_id = (request.POST.get('recipient_steam_id', '') or '').strip()
            amount = _parse_money(request.POST.get('amount_rub', ''))

            if not recipient_steam_id or not recipient_steam_id.isdigit():
                messages.error(request, 'Укажи корректный Steam ID получателя.')
                return redirect('accounts:wallet')

            if recipient_steam_id == profile.steam_id:
                messages.error(request, 'Нельзя переводить самому себе.')
                return redirect('accounts:wallet')

            recipient = SteamProfile.objects.filter(steam_id=recipient_steam_id).first()
            if not recipient:
                messages.error(request, 'Получатель с таким Steam ID не найден.')
                return redirect('accounts:wallet')

            if not amount or amount <= 0:
                messages.error(request, 'Укажи корректную сумму перевода.')
                return redirect('accounts:wallet')

            sender_balance = SteamProfile.objects.filter(pk=profile.pk).values_list('balance_rub', flat=True).first() or Decimal('0')
            if sender_balance < amount:
                messages.error(request, 'Недостаточно средств на балансе.')
                return redirect('accounts:wallet')

            request.session['pending_wallet_transfer'] = {
                'recipient_steam_id': recipient.steam_id,
                'recipient_nickname': recipient.nickname,
                'amount_rub': str(amount),
            }
            request.session.modified = True
            messages.info(request, 'Проверь перевод и нажми подтверждение.')
            return redirect('accounts:wallet')

        if action == 'cancel_transfer':
            request.session.pop('pending_wallet_transfer', None)
            request.session.modified = True
            messages.info(request, 'Перевод отменен.')
            return redirect('accounts:wallet')

        if action == 'confirm_transfer':
            pending = request.session.get('pending_wallet_transfer')
            if not pending:
                messages.error(request, 'Нет перевода для подтверждения.')
                return redirect('accounts:wallet')

            amount = _parse_money(pending.get('amount_rub', ''))
            recipient_steam_id = pending.get('recipient_steam_id', '')

            try:
                reference_code = _perform_wallet_transfer(
                    sender_steam_id=profile.steam_id,
                    recipient_steam_id=recipient_steam_id,
                    amount=amount,
                )
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect('accounts:wallet')

            request.session.pop('pending_wallet_transfer', None)
            request.session.modified = True
            messages.success(request, f'Перевод выполнен. Код операции: {reference_code}.')
            return redirect('accounts:wallet')

    profile = SteamProfile.objects.filter(pk=profile.pk).first()
    transactions = (
        WalletTransaction.objects
        .select_related('counterparty_profile', 'order')
        .filter(profile=profile)
        .order_by('-created_at')[:40]
    )
    pending_transfer = request.session.get('pending_wallet_transfer')
    return render(
        request,
        'accounts/wallet.html',
        {
            'profile': profile,
            'transactions': transactions,
            'pending_transfer': pending_transfer,
        },
    )


@login_required
def purchases_view(request):
    profile = getattr(request.user, 'steam_profile', None)
    if not profile:
        return redirect('accounts:steam_login')

    orders = (
        Order.objects
        .filter(profile=profile)
        .prefetch_related('items__product', 'payments')
        .order_by('-created_at')
    )
    topups = (
        WalletTransaction.objects
        .filter(profile=profile, tx_type=WalletTransaction.TX_TOPUP_CREDIT)
        .order_by('-created_at')[:40]
    )

    return render(
        request,
        'accounts/purchases.html',
        {
            'profile': profile,
            'orders': orders,
            'topups': topups,
        },
    )


@login_required
def support_view(request):
    return render(request, 'accounts/support.html')


def _parse_money(value):
    try:
        parsed = Decimal(str(value).replace(',', '.')).quantize(Decimal('1'))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return parsed


def _perform_wallet_transfer(sender_steam_id, recipient_steam_id, amount):
    if not amount or amount <= 0:
        raise ValueError('Некорректная сумма перевода.')

    if sender_steam_id == recipient_steam_id:
        raise ValueError('Нельзя переводить самому себе.')

    with transaction.atomic():
        sender = SteamProfile.objects.select_for_update().filter(steam_id=sender_steam_id).first()
        recipient = SteamProfile.objects.select_for_update().filter(steam_id=recipient_steam_id).first()

        if not sender or not recipient:
            raise ValueError('Отправитель или получатель не найден.')

        if sender.balance_rub < amount:
            raise ValueError('Недостаточно средств на балансе.')

        sender.balance_rub = (sender.balance_rub - amount).quantize(Decimal('1'))
        recipient.balance_rub = (recipient.balance_rub + amount).quantize(Decimal('1'))
        sender.save(update_fields=['balance_rub'])
        recipient.save(update_fields=['balance_rub'])

        ref_code = uuid4().hex[:12].upper()
        WalletTransaction.objects.create(
            profile=sender,
            tx_type=WalletTransaction.TX_TRANSFER_OUT,
            amount_rub=-amount,
            balance_after_rub=sender.balance_rub,
            counterparty_profile=recipient,
            reference_code=ref_code,
            description='Перевод другому игроку',
        )
        WalletTransaction.objects.create(
            profile=recipient,
            tx_type=WalletTransaction.TX_TRANSFER_IN,
            amount_rub=amount,
            balance_after_rub=recipient.balance_rub,
            counterparty_profile=sender,
            reference_code=ref_code,
            description='Перевод от игрока',
        )

        return ref_code