"""
Progress and Dashboard Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import Subject, Chapter, Video, VideoProgress, VideoWatch
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    Student dashboard: subjects, chapters, and progress
    """
    try:
        user = request.user

        if user.role != 'student':
            return Response(
                {'success': False, 'message': 'Only students can access dashboard'},
                status=status.HTTP_403_FORBIDDEN
            )

        subjects = Subject.objects.all().order_by('order')

        progress_data = []
        subjects_data = []

        for subject in subjects:
            chapters = (
                Chapter.objects
                .filter(subject=subject)
                .annotate(total_videos=Count('videos'))
                .order_by('order')
            )

            total_videos = sum(c.total_videos for c in chapters)

            chapter_progress = VideoProgress.objects.filter(
                student=user,
                chapter__in=chapters
            )

            progress_map = {str(p.chapter_id): p.videos_watched for p in chapter_progress}

            watched_total = sum(progress_map.values())

            percentage = (
                round((watched_total / total_videos) * 100, 1)
                if total_videos > 0 else 0
            )

            progress_data.append({
                'subject': subject.display_name,
                'videos_watched': watched_total,
                'total_videos': total_videos,
                'percentage': percentage,
                'color': subject.color
            })

            chapters_list = []
            for chapter in chapters:
                chapters_list.append({
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'total_videos': chapter.total_videos,
                    'watched_videos': progress_map.get(str(chapter.id), 0)
                })

            subjects_data.append({
                'subject': subject.display_name,
                'chapters': chapters_list
            })

        return Response(
            {'success': True, 'data': {'progress': progress_data, 'subjects': subjects_data}},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error("Dashboard error", exc_info=True)
        return Response(
            {'success': False, 'message': 'Failed to fetch dashboard data', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chapter_videos_view(request, chapter_id):
    """
    Get videos for a chapter
    """
    try:
        user = request.user

        chapter = Chapter.objects.select_related('subject').get(id=chapter_id)

        videos = Video.objects.filter(chapter=chapter).order_by('order')

        watched_ids = set(
            VideoWatch.objects.filter(
                student=user,
                completed=True
            ).values_list('video_id', flat=True)
        )

        videos_data = []
        for video in videos:
            videos_data.append({
                'id': str(video.id),
                'title': video.title,
                'description': video.description,
                'video_url': video.video_url,
                'thumbnail_url': video.thumbnail_url,
                'duration': video.duration,
                'duration_formatted': video.duration_formatted,
                'order': video.order,
                'is_watched': video.id in watched_ids
            })

        progress = VideoProgress.objects.filter(
            student=user,
            chapter=chapter
        ).first()

        videos_watched = progress.videos_watched if progress else 0

        return Response(
            {
                'success': True,
                'data': {
                    'chapter': {
                        'id': str(chapter.id),
                        'title': chapter.title,
                        'description': chapter.description,
                        'subject': chapter.subject.display_name,
                        'subject_color': chapter.subject.color,
                        'total_videos': videos.count(),
                        'videos_watched': videos_watched
                    },
                    'videos': videos_data
                }
            },
            status=status.HTTP_200_OK
        )

    except Chapter.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Chapter not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        logger.error("Chapter videos error", exc_info=True)
        return Response(
            {'success': False, 'message': 'Failed to fetch chapter videos', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_video_watched_view(request):
    """
    Mark video as watched
    """
    try:
        user = request.user
        video_id = request.data.get('video_id')
        completed = request.data.get('completed', False)
        watch_time = request.data.get('watch_time', 0)

        if not video_id:
            return Response(
                {'success': False, 'message': 'video_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        video = Video.objects.select_related('chapter').get(id=video_id)

        VideoWatch.objects.update_or_create(
            student=user,
            video=video,
            defaults={
                'completed': completed,
                'watch_time': watch_time
            }
        )

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

        return Response(
            {
                'success': True,
                'message': 'Video marked as watched',
                'data': {
                    'chapter_progress': {
                        'videos_watched': watched_count,
                        'total_videos': chapter.videos.count(),
                        'percentage': round(
                            (watched_count / chapter.videos.count()) * 100, 1
                        ) if chapter.videos.count() > 0 else 0
                    }
                }
            },
            status=status.HTTP_200_OK
        )

    except Video.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Video not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        logger.error("Mark video watched error", exc_info=True)
        return Response(
            {'success': False, 'message': 'Failed to mark video as watched', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
