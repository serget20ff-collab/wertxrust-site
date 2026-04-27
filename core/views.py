from django.shortcuts import get_object_or_404, render
from news.models import NewsPost
from servers.models import RustServer
from shop.models import Product
from .models import LegalDocument
def home(request): return render(request,'core/home.html',{'servers':RustServer.objects.filter(is_public=True)[:4],'products':Product.objects.filter(is_active=True,is_featured=True)[:4],'news_posts':NewsPost.objects.filter(is_published=True)[:3]})
def legal_index(request): return render(request,'core/legal_index.html',{'docs':LegalDocument.objects.all()})
def legal_detail(request,doc_type): return render(request,'core/legal_detail.html',{'doc':get_object_or_404(LegalDocument,doc_type=doc_type)})
