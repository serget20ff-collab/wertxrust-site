from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import SteamProfile
from servers.models import RustServer, ServerApiToken, ServerPlayerConnection
from shop.models import Entitlement, Order, Product, ProductCategory

from core.models import LegalDocument
from .forms import (
    LegalDocumentForm,
    ProductCategoryForm,
    ProductForm,
    RustServerForm,
    ServerApiTokenForm,
)


PANEL_SECTIONS = [
    {
        'key': 'player_check',
        'title': 'Проверка игроков',
        'description': 'Steam ID, ник и серверный IP.',
        'url_name': 'panel:player_check',
        'icon_symbol': '🔎',
    },
    {
        'key': 'reports',
        'title': 'Жалобы и тикеты',
        'description': 'Обращения через Discord.',
        'url_name': 'panel:reports',
        'icon_symbol': '⚠',
    },
    {
        'key': 'moderation',
        'title': 'Модерация',
        'description': 'Будущий серверный скрипт.',
        'url_name': 'panel:moderation',
        'icon_symbol': '🛡',
    },
    {
        'key': 'players',
        'title': 'Игроки',
        'description': 'Полная база игроков.',
        'url_name': 'panel:players',
        'icon_symbol': '👥',
    },
    {
        'key': 'shop',
        'title': 'Магазин',
        'description': 'Категории, товары и заказы.',
        'url_name': 'panel:shop',
        'icon_symbol': '🛒',
    },
    {
        'key': 'servers',
        'title': 'Серверы',
        'description': 'Сервера, IP и подключения.',
        'url_name': 'panel:servers',
        'icon_symbol': '▰',
    },
    {
        'key': 'staff',
        'title': 'Команда',
        'description': 'Роли и сотрудники.',
        'url_name': 'panel:staff',
        'icon_symbol': '⭐',
    },
    {
        'key': 'developer',
        'title': 'Разработка',
        'description': 'API, платежи и интеграции.',
        'url_name': 'panel:settings',
        'icon_symbol': '</>',
    },
    {
        'key': 'documents',
        'title': 'Документы',
        'description': 'Оферта, политика, правила и юридические тексты.',
        'url_name': 'panel:documents',
        'icon_symbol': '📄',
    },
]


def get_profile_or_deny(request):
    if request.user.is_superuser:
        return None

    profile = getattr(request.user, 'steam_profile', None)

    if not profile or not profile.can_access_panel:
        raise PermissionDenied

    return profile


def user_can_access_section(request, profile, section_key):
    if request.user.is_superuser:
        return True

    if not profile:
        return False

    return profile.can_access_panel_section(section_key)


def request_can_manage_staff(request, profile):
    if request.user.is_superuser:
        return True

    if not profile:
        return False

    return profile.can_manage_staff()


def request_can_update_target(request, actor_profile, target_profile, new_role):
    if request.user.is_superuser:
        return True

    if not actor_profile:
        return False

    return actor_profile.can_manage_profile_role(target_profile, new_role)


def require_section(request, profile, *section_keys):
    for section_key in section_keys:
        if user_can_access_section(request, profile, section_key):
            return

    raise PermissionDenied


def get_allowed_sections(request, profile):
    return [
        section for section in PANEL_SECTIONS
        if user_can_access_section(request, profile, section['key'])
    ]


@login_required
def dashboard_view(request):
    profile = get_profile_or_deny(request)
    sections = get_allowed_sections(request, profile)

    stats = {
        'sections_count': len(sections),
        'players_count': SteamProfile.objects.count(),
        'staff_count': SteamProfile.objects.exclude(project_role=SteamProfile.ROLE_PLAYER).count(),
        'banned_count': SteamProfile.objects.filter(is_banned_on_site=True).count(),
        'products_count': Product.objects.count(),
        'orders_count': Order.objects.count(),
        'servers_count': RustServer.objects.count(),
    }

    return render(
        request,
        'panel/dashboard.html',
        {
            'profile': profile,
            'sections': sections,
            'stats': stats,
        },
    )


@login_required
def player_check_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'player_check', 'developer')

    query = request.GET.get('q', '').strip()

    connections = (
        ServerPlayerConnection.objects
        .select_related('profile', 'server')
        .order_by('-last_seen_at', '-updated_at')[:80]
    )

    found_profile = None
    linked_connections = ServerPlayerConnection.objects.none()

    if query:
        connections = (
            ServerPlayerConnection.objects
            .select_related('profile', 'server')
            .filter(
                Q(profile__steam_id__icontains=query)
                | Q(profile__nickname__icontains=query)
                | Q(server_ip__icontains=query)
                | Q(nickname_at_moment__icontains=query)
            )
            .order_by('-last_seen_at', '-updated_at')[:100]
        )

        if query.isdigit():
            found_profile = SteamProfile.objects.filter(steam_id=query).first()

            if found_profile:
                player_ips = list(
                    ServerPlayerConnection.objects
                    .filter(profile=found_profile)
                    .values_list('server_ip', flat=True)
                    .distinct()
                )

                linked_connections = (
                    ServerPlayerConnection.objects
                    .select_related('profile', 'server')
                    .filter(server_ip__in=player_ips)
                    .exclude(profile=found_profile)
                    .order_by('server_ip', '-last_seen_at')[:150]
                )

    return render(
        request,
        'panel/players.html',
        {
            'page_mode': 'check',
            'title': 'Проверка игроков',
            'description': 'Поиск по нику, Steam ID или серверному IP. Серверные IP будут приходить от игрового сервера через C# агент.',
            'profile': profile,
            'query': query,
            'connections': connections,
            'found_profile': found_profile,
            'linked_connections': linked_connections,
            'can_full_players': False,
        },
    )


@login_required
def players_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'players', 'developer')

    query = request.GET.get('q', '').strip()

    players = SteamProfile.objects.all().order_by('-last_seen_at', '-first_seen_at')

    if query:
        players = players.filter(
            Q(steam_id__icontains=query)
            | Q(nickname__icontains=query)
            | Q(last_server_ip__icontains=query)
            | Q(server_connections__server_ip__icontains=query)
            | Q(project_role__icontains=query)
        ).distinct()

    return render(
        request,
        'panel/players.html',
        {
            'page_mode': 'full',
            'title': 'Игроки',
            'description': 'Полная база игроков: Steam ID, роль, последний серверный IP и технические данные.',
            'profile': profile,
            'query': query,
            'players': players[:120],
            'connections': [],
            'found_profile': None,
            'linked_connections': [],
            'can_full_players': True,
        },
    )


@login_required
def shop_manage_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'shop', 'developer')

    category_form = ProductCategoryForm(prefix='category')
    product_form = ProductForm(prefix='product')

    if request.method == 'POST':
        form_kind = request.POST.get('form_kind')

        if form_kind == 'category':
            category_form = ProductCategoryForm(request.POST, prefix='category')

            if category_form.is_valid():
                category_form.save()
                return redirect('panel:shop')

        if form_kind == 'product':
            product_form = ProductForm(request.POST, request.FILES, prefix='product')

            if product_form.is_valid():
                product_form.save()
                return redirect('panel:shop')

    categories = ProductCategory.objects.all().order_by('name')

    products = (
        Product.objects
        .select_related('category')
        .prefetch_related('content_items')
        .order_by('name')[:120]
    )

    orders = Order.objects.select_related('profile').order_by('-created_at')[:40]

    entitlements = (
        Entitlement.objects
        .select_related('profile', 'product')
        .order_by('-created_at')[:40]
    )

    return render(
        request,
        'panel/shop_manage.html',
        {
            'profile': profile,
            'category_form': category_form,
            'product_form': product_form,
            'categories': categories,
            'products': products,
            'orders': orders,
            'entitlements': entitlements,
        },
    )


@login_required
def category_delete_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'shop', 'developer')

    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'POST':
        category.delete()

    return redirect('panel:shop')


@login_required
def product_delete_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'shop', 'developer')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()

    return redirect('panel:shop')


@login_required
def servers_manage_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'servers', 'developer')

    server_form = RustServerForm(prefix='server')

    if request.method == 'POST':
        server_form = RustServerForm(request.POST, prefix='server')

        if server_form.is_valid():
            server_form.save()
            return redirect('panel:servers')

    servers = RustServer.objects.all().order_by('sort_order', 'name')

    connections = (
        ServerPlayerConnection.objects
        .select_related('profile', 'server')
        .order_by('-last_seen_at', '-updated_at')[:80]
    )

    return render(
        request,
        'panel/servers_manage.html',
        {
            'profile': profile,
            'server_form': server_form,
            'servers': servers,
            'connections': connections,
        },
    )


@login_required
def server_delete_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'servers', 'developer')

    server = get_object_or_404(RustServer, pk=pk)

    if request.method == 'POST':
        server.delete()

    return redirect('panel:servers')


@login_required
def reports_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'reports', 'discord_tools', 'developer')

    return render(
        request,
        'panel/reports.html',
        {
            'profile': profile,
        },
    )


@login_required
def moderation_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'moderation', 'developer')

    return render(
        request,
        'panel/moderation.html',
        {
            'profile': profile,
        },
    )


@login_required
def staff_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'staff', 'developer')

    can_manage_staff = request_can_manage_staff(request, profile)
    selected_role = request.GET.get('role', '').strip()

    if request.method == 'POST':
        if not can_manage_staff:
            raise PermissionDenied

        target_steam_id = request.POST.get('steam_id', '').strip()
        new_role = request.POST.get('project_role', '').strip()
        new_balance_raw = request.POST.get('balance_rub', '').strip().replace(',', '.')

        target = get_object_or_404(SteamProfile, steam_id=target_steam_id)

        if not request_can_update_target(request, profile, target, new_role):
            raise PermissionDenied

        if new_role not in dict(SteamProfile.PROJECT_ROLE_CHOICES):
            raise PermissionDenied

        target.project_role = new_role
        target.is_project_staff = new_role != SteamProfile.ROLE_PLAYER

        if new_balance_raw:
            try:
                target.balance_rub = Decimal(new_balance_raw)
            except InvalidOperation:
                pass

        target.save()
        return redirect('panel:staff')

    staff_queryset = (
        SteamProfile.objects
        .exclude(project_role=SteamProfile.ROLE_PLAYER)
        .annotate(connections_total=Count('server_connections'))
    )

    if selected_role:
        staff_queryset = staff_queryset.filter(project_role=selected_role)

    staff_members = sorted(
        list(staff_queryset),
        key=lambda item: (item.role_order_index, item.nickname.lower() if item.nickname else item.steam_id),
    )

    role_cards = []

    for role_key in SteamProfile.STAFF_ROLE_ORDER:
        role_title = dict(SteamProfile.PROJECT_ROLE_CHOICES).get(role_key, role_key)
        count = SteamProfile.objects.filter(project_role=role_key).count()

        role_cards.append(
            {
                'key': role_key,
                'title': role_title,
                'count': count,
                'active': selected_role == role_key,
            }
        )

    return render(
        request,
        'panel/staff.html',
        {
            'profile': profile,
            'staff_members': staff_members,
            'roles': SteamProfile.PROJECT_ROLE_CHOICES,
            'role_cards': role_cards,
            'selected_role': selected_role,
            'can_manage_staff': can_manage_staff,
        },
    )


@login_required
def settings_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'settings', 'developer')

    api_token_form = ServerApiTokenForm(prefix='api')

    if request.method == 'POST':
        form_kind = request.POST.get('form_kind')

        if form_kind == 'api_token':
            api_token_form = ServerApiTokenForm(request.POST, prefix='api')

            if api_token_form.is_valid():
                token = api_token_form.save(commit=False)
                token.created_by = request.user
                token.save()
                return redirect('panel:settings')

    api_tokens = (
        ServerApiToken.objects
        .select_related('server', 'created_by')
        .order_by('-created_at')
    )

    return render(
        request,
        'panel/settings.html',
        {
            'profile': profile,
            'api_token_form': api_token_form,
            'api_tokens': api_tokens,
        },
    )


@login_required
def api_token_delete_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'settings', 'developer')

    token = get_object_or_404(ServerApiToken, pk=pk)

    if request.method == 'POST':
        token.delete()

    return redirect('panel:settings')
@login_required
def documents_manage_view(request):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'documents', 'developer')

    form = LegalDocumentForm()

    if request.method == 'POST':
        form = LegalDocumentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('panel:documents')

    documents = LegalDocument.objects.all().order_by('name')

    return render(
        request,
        'panel/documents_manage.html',
        {
            'profile': profile,
            'form': form,
            'documents': documents,
        },
    )


@login_required
def document_edit_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'documents', 'developer')

    document = get_object_or_404(LegalDocument, pk=pk)
    form = LegalDocumentForm(instance=document)

    if request.method == 'POST':
        form = LegalDocumentForm(request.POST, instance=document)

        if form.is_valid():
            form.save()
            return redirect('panel:documents')

    return render(
        request,
        'panel/document_edit.html',
        {
            'profile': profile,
            'form': form,
            'document': document,
        },
    )


@login_required
def document_delete_view(request, pk):
    profile = get_profile_or_deny(request)
    require_section(request, profile, 'documents', 'developer')

    document = get_object_or_404(LegalDocument, pk=pk)

    if request.method == 'POST':
        document.delete()

    return redirect('panel:documents')