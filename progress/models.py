"""
Progress tracking models
"""
from django.db import models
from django.conf import settings
import uuid


class Subject(models.Model):
    """Subject model - Physics, Chemistry, Maths"""
    SUBJECT_CHOICES = (
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('maths', 'Maths'),
    )
    
    COLOR_CHOICES = (
        ('#3b82f6', 'Blue'),
        ('#8b5cf6', 'Purple'),
        ('#ec4899', 'Pink'),
        ('#10b981', 'Green'),
        ('#f59e0b', 'Orange'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#3b82f6')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subjects'
        ordering = ['order', 'display_name']
    
    def __str__(self):
        return self.display_name


class Chapter(models.Model):
    """Chapter model for each subject"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chapters'
        ordering = ['subject', 'order', 'title']
        unique_together = ['subject', 'title']
    
    def __str__(self):
        return f"{self.subject.display_name} - {self.title}"


class VideoProgress(models.Model):
    """Track video watch progress for each student"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='video_progress'
    )
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='progress')
    videos_watched = models.IntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_progress'
        unique_together = ['student', 'chapter']
    
    def __str__(self):
        return f"{self.student.name} - {self.chapter.title} ({self.videos_watched}/{self.chapter.total_videos})"
    
    @property
    def percentage(self):
        if self.chapter.total_videos == 0:
            return 0
        return round((self.videos_watched / self.chapter.total_videos) * 100, 1)