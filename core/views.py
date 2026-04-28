from django.shortcuts import get_object_or_404, render

from news.models import NewsPost
from servers.models import RustServer
from shop.models import Product

from .models import HelpCategory, LegalDocument


def home(request):
    servers = (
        RustServer.objects
        .filter(is_public=True, show_on_home=True)
        .order_by('sort_order', 'name')[:3]
    )

    featured_products = (
        Product.objects
        .filter(is_active=True, is_featured=True)
        .select_related('category')
        .order_by('name')[:4]
    )

    return render(
        request,
        'core/home.html',
        {
            'servers': servers,
            'featured_products': featured_products,
            'news_posts': NewsPost.objects.filter(is_published=True)[:3],
        },
    )


def legal_index(request):
    docs = LegalDocument.objects.filter(is_published=True).order_by('name')

    return render(
        request,
        'core/legal_index.html',
        {
            'docs': docs,
        },
    )


def legal_detail(request, slug):
    doc = get_object_or_404(
        LegalDocument,
        slug=slug,
        is_published=True,
    )

    return render(
        request,
        'core/legal_detail.html',
        {
            'doc': doc,
        },
    )


def help_center(request):
    categories = (
        HelpCategory.objects
        .filter(is_public=True)
        .prefetch_related('items')
        .order_by('sort_order', 'title')
    )

    selected_category = request.GET.get('category', '').strip()
    active_category = None

    if selected_category:
        active_category = categories.filter(pk=selected_category).first()

    if not active_category:
        active_category = categories.first()

    return render(
        request,
        'core/help_center.html',
        {
            'categories': categories,
            'active_category': active_category,
        },
    )