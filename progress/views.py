"""
Progress and Dashboard Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import Subject, Chapter, VideoProgress, VideoWatch, Video
from .serializers import SubjectSerializer, ChapterSerializer, VideoProgressSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    Get Student Dashboard Data
    Returns progress and chapters for all subjects
    """
    try:
        user = request.user
        
        # Only students can access dashboard
        if user.role != 'student':
            return Response({
                'success': False,
                'message': 'Only students can access dashboard'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all subjects
        subjects = Subject.objects.all().order_by('order')
        
        progress_data = []
        subjects_data = []
        
        for subject in subjects:
            # Get all chapters for this subject
            chapters = Chapter.objects.filter(subject=subject).order_by('order')
            
            # Calculate subject totals
            total_videos = chapters.aggregate(total=Sum('total_videos'))['total'] or 0
            
            # Get user's progress for this subject's chapters
            chapter_progress = VideoProgress.objects.filter(
                student=user,
                chapter__subject=subject
            ).select_related('chapter')
            
            # Create a map of chapter_id -> videos_watched
            progress_map = {str(p.chapter.id): p.videos_watched for p in chapter_progress}
            
            # Calculate total watched for subject
            videos_watched = sum(progress_map.values())
            
            # Calculate percentage
            percentage = round((videos_watched / total_videos * 100), 1) if total_videos > 0 else 0
            
            # Add to progress summary
            progress_data.append({
                'subject': subject.display_name,
                'videos_watched': videos_watched,
                'total_videos': total_videos,
                'percentage': percentage,
                'color': subject.color
            })
            
            # Build chapters data
            chapters_list = []
            for chapter in chapters:
                watched = progress_map.get(str(chapter.id), 0)
                chapters_list.append({
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'total_videos': chapter.total_videos,
                    'watched_videos': watched
                })
            
            subjects_data.append({
                'subject': subject.display_name,
                'chapters': chapters_list
            })
        
        response_data = {
            'progress': progress_data,
            'subjects': subjects_data
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Failed to fetch dashboard data',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_progress_view(request):
    """
    Update video progress for a chapter
    Expects: { "chapter_id": "uuid", "videos_watched": number }
    """
    try:
        user = request.user
        chapter_id = request.data.get('chapter_id')
        videos_watched = request.data.get('videos_watched')
        
        if not chapter_id or videos_watched is None:
            return Response({
                'success': False,
                'message': 'chapter_id and videos_watched are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get chapter
        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Chapter not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update or create progress
        progress, created = VideoProgress.objects.update_or_create(
            student=user,
            chapter=chapter,
            defaults={'videos_watched': videos_watched}
        )
        
        return Response({
            'success': True,
            'message': 'Progress updated successfully',
            'data': {
                'chapter_id': str(chapter.id),
                'videos_watched': progress.videos_watched,
                'total_videos': chapter.total_videos,
                'percentage': progress.percentage
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Update progress error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Failed to update progress',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chapter_videos_view(request, chapter_id):
    """
    Get all videos for a specific chapter
    Returns chapter details and list of videos with watch status
    """
    try:
        user = request.user
        
        # Get the chapter
        try:
            chapter = Chapter.objects.select_related('subject').get(id=chapter_id)
        except Chapter.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Chapter not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all videos for this chapter
        videos = Video.objects.filter(chapter=chapter).order_by('order')
        
        # Get user's watch status for these videos
        watched_videos = set(
    VideoWatch.objects.filter(
        student=user,
        completed=True
    ).values_list('video_id', flat=True)
)
        
        # Build videos list
        videos_data = []
        for video in videos:
            is_watched = str(video.id) in [str(v) for v in watched_videos]
            
            videos_data.append({
                'id': str(video.id),
                'title': video.title,
                
                'video_url': video.video_url,
                'thumbnail_url': video.thumbnail_url,
                'duration': video.duration,
                'duration_formatted': video.duration_formatted,
                'order': video.order,
                'is_watched': is_watched
            })
        
        # Get chapter progress
        try:
            progress = VideoProgress.objects.get(student=user, chapter=chapter)
            videos_watched_count = progress.videos_watched
        except VideoProgress.DoesNotExist:
            videos_watched_count = 0
        
        response_data = {
            'chapter': {
                'id': str(chapter.id),
                'title': chapter.title,
                
                'subject': chapter.subject.display_name,
                'subject_color': chapter.subject.color,
                'total_videos': chapter.total_videos,
                'videos_watched': videos_watched_count
            },
            'videos': videos_data
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Chapter videos error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Failed to fetch chapter videos',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_video_watched_view(request):
    """
    Mark a video as watched
    Expects: { "video_id": "uuid", "completed": true/false, "watch_time": seconds }
    """
    try:
        user = request.user
        video_id = request.data.get('video_id')
        completed = request.data.get('completed', False)
        watch_time = request.data.get('watch_time', 0)
        
        if not video_id:
            return Response({
                'success': False,
                'message': 'video_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get video
        try:
            video = Video.objects.select_related('chapter').get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Video not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update or create video watch record
        video_watch, created = VideoWatch.objects.update_or_create(
            student=user,
            video=video,
            defaults={
                'watched': True,
                'completed': completed,
                'watch_time': watch_time
            }
        )
        
        # Update chapter progress
        chapter = video.chapter
        watched_count = VideoWatch.objects.filter(
            student=user,
            video__chapter=chapter,
            completed=True
        ).count()
        
        VideoProgress.objects.update_or_create(
            student=user,
            chapter=chapter,
            defaults={'videos_watched': watched_count}
        )
        
        return Response({
            'success': True,
            'message': 'Video marked as watched',
            'data': {
                'video_id': str(video.id),
                'completed': video_watch.completed,
                'chapter_progress': {
                    'videos_watched': watched_count,
                    'total_videos': chapter.total_videos,
                    'percentage': round((watched_count / chapter.total_videos * 100), 1) if chapter.total_videos > 0 else 0
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Mark video watched error: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Failed to mark video as watched',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)