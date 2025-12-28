"""
URL Configuration for progress app
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    # Student endpoints
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('update/', views.update_progress_view, name='update'),
    
    # Chapter & Videos
    path('chapter/<uuid:chapter_id>/videos/', views.chapter_videos_view, name='chapter_videos'),
    path('video/watch/', views.mark_video_watched_view, name='mark_video_watched'),
    
    # Teacher endpoints
    path('teacher/students/', views.all_students_progress_view, name='all_students_progress'),
    path('teacher/students/<uuid:student_id>/', views.student_detail_progress_view, name='student_detail_progress'),
]