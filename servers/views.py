from django.shortcuts import render
from .models import RustServer
def server_list(request): return render(request,'servers/server_list.html',{'servers':RustServer.objects.filter(is_public=True)})
