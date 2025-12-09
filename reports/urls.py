from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('submit/<int:visit_id>/', views.submit_report, name='submit'),
    path('list/', views.report_list, name='list'),
]
