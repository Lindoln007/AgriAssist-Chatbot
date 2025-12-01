from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/get/', views.api_get_weather, name='api_get_weather'),
]
