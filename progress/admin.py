"""
Django Admin Configuration for Progress
"""
from django.contrib import admin
from .models import Subject, Chapter, VideoProgress


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'color', 'order']
    list_editable = ['order']
    search_fields = ['name', 'display_name']
    ordering = ['order', 'display_name']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'order', 'total_videos', 'created_at']
    list_filter = ['subject']
    list_editable = ['order', 'total_videos']
    search_fields = ['title', 'subject__display_name']
    ordering = ['subject', 'order']


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'chapter', 'videos_watched', 'get_total_videos', 'percentage', 'last_watched_at']
    list_filter = ['chapter__subject', 'last_watched_at']
    search_fields = ['student__name', 'student__email', 'chapter__title']
    readonly_fields = ['created_at', 'last_watched_at']
    
    def get_total_videos(self, obj):
        return obj.chapter.total_videos
    get_total_videos.short_description = 'Total Videos'
    
    def percentage(self, obj):
        return f"{obj.percentage}%"
    percentage.short_description = 'Progress'