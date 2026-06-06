from django.urls import path
from django.views.static import serve
from django.conf import settings
import os

def serve_media(request, path):
    """Serve media files"""
    return serve(request, path, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('media/<path:path>', serve_media),
]
