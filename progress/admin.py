"""
Django Admin Configuration for Progress
"""
from django.contrib import admin
from .models import Subject, Chapter, Video, VideoWatch, VideoProgress


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'color', 'order']
    list_editable = ['order']
    search_fields = ['name', 'display_name']
    ordering = ['order', 'display_name']


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ['order', 'title', 'video_url', 'duration']
    ordering = ['order']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'order', 'get_video_count', 'total_videos', 'created_at']
    list_filter = ['subject']
    list_editable = ['order']
    search_fields = ['title', 'subject__display_name']
    ordering = ['subject', 'order']
    inlines = [VideoInline]
    
    def get_video_count(self, obj):
        return obj.videos.count()
    get_video_count.short_description = 'Videos'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'order', 'duration_formatted', 'created_at']
    list_filter = ['chapter__subject', 'chapter']
    list_editable = ['order']
    search_fields = ['title', 'chapter__title']
    ordering = ['chapter', 'order']


@admin.register(VideoWatch)
class VideoWatchAdmin(admin.ModelAdmin):
    list_display = ['student', 'video', 'completed', 'watch_time', 'last_watched_at']
    list_filter = ['completed', 'video__chapter__subject', 'last_watched_at']
    search_fields = ['student__name', 'student__email', 'video__title']
    readonly_fields = ['created_at', 'last_watched_at']


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