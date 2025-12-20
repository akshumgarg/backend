# ============================================
# authentication/urls.py (Create this file)
# ============================================
"""
URL configuration for authentication app
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_token_view, name='verify'),
    path('logout/', views.logout_view, name='logout'),
]


