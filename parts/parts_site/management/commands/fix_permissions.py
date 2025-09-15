from django.core.management.base import BaseCommand
from django.conf import settings
import os
import stat

class Command(BaseCommand):
    help = 'Fix file permissions for media directory'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        
        # Create media directory if it doesn't exist
        if not os.path.exists(media_root):
            try:
                os.makedirs(media_root, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f'Created media directory: {media_root}')
                )
            except PermissionError as e:
                self.stdout.write(
                    self.style.ERROR(f'Permission denied creating media directory: {e}')
                )
                return
        
        # Fix permissions
        try:
            # Set directory permissions to 755
            os.chmod(media_root, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # Recursively fix permissions for all subdirectories and files
            for root, dirs, files in os.walk(media_root):
                # Fix directory permissions
                os.chmod(root, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                
                # Fix file permissions
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            
            self.stdout.write(
                self.style.SUCCESS(f'Fixed permissions for media directory: {media_root}')
            )
            
        except PermissionError as e:
            self.stdout.write(
                self.style.ERROR(f'Permission denied fixing permissions: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fixing permissions: {e}')
            )
