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
        
        # Check if media directory exists
        media_root = default_storage.location
        if not os.path.exists(media_root):
            os.makedirs(media_root, exist_ok=True)
            logger.info(f"Created media directory: {media_root}")
        
        # Try to save the file
        file_path = default_storage.save(f"test_uploads/{file.name}", file)
        logger.info(f"File saved to: {file_path}")
        
        return JsonResponse({
            'success': True,
            'file_path': file_path,
            'file_size': file.size,
            'media_root': media_root
        })
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def debug_upload_page(request):
    """
    Debug page to test file uploads
    """
    return render(request, 'debug_upload.html')
