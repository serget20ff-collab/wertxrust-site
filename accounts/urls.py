from django.urls import path
from . import views
app_name='accounts'
urlpatterns=[path('steam/login/',views.steam_login,name='steam_login'),path('steam/callback/',views.steam_callback,name='steam_callback'),path('logout/',views.logout_view,name='logout'),path('profile/',views.profile_view,name='profile')]
