from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import os
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def test_file_upload(request):
    """
    Debug view to test file upload functionality
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        logger.info(f"File upload attempt: {file.name}, size: {file.size}")
        
        # Check if media directory exists and has proper permissions
        media_root = default_storage.location
        if not os.path.exists(media_root):
            try:
                os.makedirs(media_root, exist_ok=True)
                logger.info(f"Created media directory: {media_root}")
            except PermissionError as e:
                logger.error(f"Permission denied creating media directory: {e}")
                return JsonResponse({'error': f'Permission denied creating media directory: {e}'}, status=500)
        
        # Check write permissions
        if not os.access(media_root, os.W_OK):
            logger.error(f"No write permission to media directory: {media_root}")
            return JsonResponse({'error': f'No write permission to media directory: {media_root}'}, status=500)
        
        # Try to save the file
        file_path = default_storage.save(f"test_uploads/{file.name}", file)
        logger.info(f"File saved to: {file_path}")
        
        # Get the full URL for the file
        from django.conf import settings
        file_url = f"{settings.MEDIA_URL}{file_path}"
        
        return JsonResponse({
            'success': True,
            'file_path': file_path,
            'file_url': file_url,
            'file_size': file.size,
            'media_root': media_root,
            'media_url': settings.MEDIA_URL
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def debug_upload_page(request):
    """
    Debug page to test file uploads
    """
    return render(request, 'debug_upload.html')

def debug_media_page(request):
    """
    Debug page to view media files
    """
    return render(request, 'debug_media.html')

def test_media_access(request):
    """
    Test if media files are accessible
    """
    from django.conf import settings
    from django.http import HttpResponse
    import os
    
    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL
    
    # List files in media directory
    files = []
    if os.path.exists(media_root):
        for root, dirs, filenames in os.walk(media_root):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), media_root)
                file_url = f"{media_url}{rel_path}"
                full_path = os.path.join(root, filename)
                file_exists = os.path.exists(full_path)
                files.append({
                    'path': rel_path,
                    'url': file_url,
                    'full_path': full_path,
                    'exists': file_exists,
                    'readable': os.access(full_path, os.R_OK) if file_exists else False
                })
    
    return JsonResponse({
        'media_root': media_root,
        'media_url': media_url,
        'files': files,
        'media_root_exists': os.path.exists(media_root),
        'media_root_writable': os.access(media_root, os.W_OK) if os.path.exists(media_root) else False,
        'debug_mode': settings.DEBUG
    })

def test_media_file(request, file_path):
    """
    Test serving a specific media file
    """
    from django.conf import settings
    from django.http import HttpResponse, Http404
    import os
    
    media_root = settings.MEDIA_ROOT
    full_path = os.path.join(media_root, file_path)
    
    if not os.path.exists(full_path):
        raise Http404("File not found")
    
    try:
        with open(full_path, 'rb') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    except Exception as e:
        return HttpResponse(f"Error reading file: {str(e)}", status=500)
