from django.urls import path

from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    path('player-check/', views.player_check_view, name='player_check'),
    path('players/', views.players_view, name='players'),

    path('reports/', views.reports_view, name='reports'),
    path('moderation/', views.moderation_view, name='moderation'),

    path('shop/', views.shop_manage_view, name='shop'),
    path('shop/category/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    path('shop/product/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    path('servers/', views.servers_manage_view, name='servers'),
    path('servers/<int:pk>/delete/', views.server_delete_view, name='server_delete'),

    path('staff/', views.staff_view, name='staff'),

    path('documents/', views.documents_manage_view, name='documents'),
    path('documents/<int:pk>/edit/', views.document_edit_view, name='document_edit'),
    path('documents/<int:pk>/delete/', views.document_delete_view, name='document_delete'),

    path('settings/', views.settings_view, name='settings'),
    path('settings/api-token/<int:pk>/delete/', views.api_token_delete_view, name='api_token_delete'),
]