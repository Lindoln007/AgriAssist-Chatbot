"""
URL configuration for settings app
"""
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_index, name='index'),
    path('update/user/', views.update_user_setting, name='update_user_setting'),
    path('update/system/', views.update_system_setting, name='update_system_setting'),
    path('get/<str:setting_type>/<str:setting_key>/', views.get_setting_value, name='get_setting_value'),
]

