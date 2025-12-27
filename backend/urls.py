# ============================================
# config/urls.py (Main URL configuration)
# ============================================
"""
Main URL configuration for the project
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """Root API endpoint"""
    return JsonResponse({
        'message': 'Authentication API',
        'version': '1.0',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'verify': '/api/auth/verify/',
            'logout': '/api/auth/logout/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('authentication.urls')),
    path('api/progress/', include('progress.urls')),
]