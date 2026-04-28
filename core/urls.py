from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('help/', views.help_center, name='help_center'),

    path('legal/', views.legal_index, name='legal_index'),
    path('legal/<slug:slug>/', views.legal_detail, name='legal_detail'),
]