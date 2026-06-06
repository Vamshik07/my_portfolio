from django.urls import path
from django.http import FileResponse, Http404
from django.conf import settings
import os

def serve_media(request, path):
    """Serve media files directly"""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Security: prevent directory traversal attacks
    if not os.path.abspath(file_path).startswith(os.path.abspath(settings.MEDIA_ROOT)):
        raise Http404("File not found")
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")
    
    try:
        return FileResponse(open(file_path, 'rb'))
    except Exception:
        raise Http404("File not found")

urlpatterns = [
    path('media/<path:path>', serve_media, name='serve_media'),
]

