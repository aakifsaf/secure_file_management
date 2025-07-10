from django.db import models
from django.conf import settings
# Create your models here.

class FileUpload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_file_name = models.CharField(max_length=255)
    encrypted_file = models.FileField(upload_to='encrypted_files/')
    encryption_key = models.TextField()  # Store encrypted key
    file_size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.original_file_name
