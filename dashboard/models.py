from django.db import models
from django.contrib.auth.models import User

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
