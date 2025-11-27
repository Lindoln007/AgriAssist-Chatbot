from django.urls import path
from . import views

app_name = 'policy_updates'

urlpatterns = [
    # User-facing URLs
    path('', views.user_list, name='user_list'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    
    # Admin URLs
    path('admin/', views.admin_list, name='admin_list'),
    path('admin/create/', views.admin_create, name='admin_create'),
    path('admin/edit/<int:pk>/', views.admin_edit, name='admin_edit'),
    path('admin/delete/<int:pk>/', views.admin_delete, name='admin_delete'),
]
