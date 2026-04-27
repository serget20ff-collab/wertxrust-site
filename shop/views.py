from django.shortcuts import render

from .models import Product, ProductCategory


def shop_index(request):
    selected_category = request.GET.get('category', 'all')

    categories = ProductCategory.objects.filter(
        is_active=True,
    ).order_by('name')

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .prefetch_related('content_items')
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
        },
    )