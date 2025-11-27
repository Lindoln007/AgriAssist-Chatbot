from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_reminder, name='add'),
    path('update/<int:reminder_id>/', views.update_status, name='update_status'),
    path('api/events/', views.api_events, name='api_events'),
]
