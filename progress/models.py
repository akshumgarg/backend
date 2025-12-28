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
    # description = models.TextField(blank=True, null=True)
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


class Video(models.Model):
    """Video model for each chapter"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=500, help_text="YouTube URL or video link")
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in seconds", default=0)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['chapter', 'order', 'title']
        unique_together = ['chapter', 'order']
    
    def __str__(self):
        return f"{self.chapter.title} - {self.title}"
    
    @property
    def duration_formatted(self):
        """Return duration in MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"


class VideoWatch(models.Model):
    """Track which videos a student has watched"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='watched_videos'
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='watches')
    watched = models.BooleanField(default=False)
    watch_time = models.IntegerField(default=0, help_text="Time watched in seconds")
    completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_watches'
        unique_together = ['student', 'video']
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.student.name} - {self.video.title}"


class VideoProgress(models.Model):
    """Track video watch progress for each student per chapter (aggregated)"""
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