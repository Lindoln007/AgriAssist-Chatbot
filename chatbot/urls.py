from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_home, name='home'),
    path('api/', views.chatbot_api, name='api'),
]
