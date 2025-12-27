"""
URL Configuration for progress app
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('update/', views.update_progress_view, name='update'),
]