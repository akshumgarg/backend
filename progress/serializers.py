"""
Serializers for progress API
"""
from rest_framework import serializers
from .models import Subject, Chapter, VideoProgress


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'display_name', 'color', 'order']
        read_only_fields = ['id']


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer for Chapter model"""
    subject_name = serializers.CharField(source='subject.display_name', read_only=True)
    
    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'subject_name', 'title', 'order', 'total_videos']
        read_only_fields = ['id']


class VideoProgressSerializer(serializers.ModelSerializer):
    """Serializer for VideoProgress model"""
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = VideoProgress
        fields = ['id', 'student', 'chapter', 'chapter_title', 'videos_watched', 'percentage', 'last_watched_at']
        read_only_fields = ['id', 'student', 'last_watched_at']