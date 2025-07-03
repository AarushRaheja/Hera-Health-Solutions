
from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    STATUS_CHOICES = [
        ('not-started', 'Not Started'),
        ('in-progress', 'In Progress'),
        ('complete', 'Complete'),
    ]

    name = models.CharField(max_length=255)
    upload = models.FileField(upload_to='user_files/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-started')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
