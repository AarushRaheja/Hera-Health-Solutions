from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class File(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    upload_date = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.id})" if self.name else self.id

class DashboardFileUser(models.Model):
    STATUS_CHOICES = [
        ('not-viewed', 'Not Viewed'),
        ('viewed', 'Viewed')
    ]
    
    file = models.ForeignKey(File, on_delete=models.CASCADE, to_field='id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-viewed')

    class Meta:
        unique_together = ('file', 'user')
        db_table = 'dashboard_file_user'

    def __str__(self):
        return f"File: {self.file.id}, User: {self.user.id}, Status: {self.get_status_display()}"


class UploadedFile(models.Model):
    """
    Tracks files uploaded by users.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        help_text="The user who uploaded the file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Name of the uploaded file"
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the file was uploaded"
    )
    file_path = models.CharField(
        max_length=500,
        help_text="Relative path to the uploaded file",
        null=True,
        blank=True
    )
    file_content = models.BinaryField(
        null=True,
        blank=True,
        help_text="The actual content of the uploaded file"
    )

    class Meta:
        db_table = 'dashboard_uploaded_files'
        verbose_name = 'Uploaded File'
        verbose_name_plural = 'Uploaded Files'
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.file_name} (uploaded by {self.user.username})"
