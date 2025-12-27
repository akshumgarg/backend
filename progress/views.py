"""
Progress and Dashboard Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import Subject, Chapter, VideoProgress
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