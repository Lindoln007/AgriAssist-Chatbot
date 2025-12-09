from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    path('', views.farmer_list, name='list'),
    path('add/', views.farmer_create, name='create'),
    path('<int:pk>/', views.farmer_detail, name='detail'),
    path('<int:farmer_id>/visit/add/', views.visit_create, name='visit_create'),
]
