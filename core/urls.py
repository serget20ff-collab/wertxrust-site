from django.urls import path
from . import views
app_name='core'
urlpatterns=[path('',views.home,name='home'),path('legal/',views.legal_index,name='legal_index'),path('legal/<str:doc_type>/',views.legal_detail,name='legal_detail')]
