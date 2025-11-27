from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_selection, name='login_selection'),
    path('login/user/', views.user_login, name='user_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('signin/', views.login_selection, name='login'),
    path('logout/', views.signout, name='logout'),
    
    # Chatbot URLs
    path('', views.chatbot_home, name='home'),
    path('api/', views.chatbot_api, name='api'),
    path('sessions/', views.get_user_sessions, name='get_sessions'),
    path('session/<int:session_id>/', views.get_session_messages, name='session_messages'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
]
