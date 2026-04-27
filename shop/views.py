from django.shortcuts import render
from .models import Product, ProductCategory
def shop_index(request): return render(request,'shop/shop_index.html',{'categories':ProductCategory.objects.prefetch_related('products'),'products':Product.objects.filter(is_active=True)})
