from django.shortcuts import render

from .models import RustServer


def server_list(request):
    servers = (
        RustServer.objects
        .filter(is_public=True)
        .order_by('sort_order', 'name')
    )

    return render(
        request,
        'servers/server_list.html',
        {
            'servers': servers,
        },
    )