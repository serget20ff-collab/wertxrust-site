from django.shortcuts import get_object_or_404, render
from .models import NewsPost
def news_list(request): return render(request,'news/news_list.html',{'posts':NewsPost.objects.filter(is_published=True)})
def news_detail(request,slug): return render(request,'news/news_detail.html',{'post':get_object_or_404(NewsPost,slug=slug,is_published=True)})
