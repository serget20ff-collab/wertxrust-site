from django.urls import path
from . import views
app_name='servers'
urlpatterns=[path('',views.server_list,name='server_list')]
