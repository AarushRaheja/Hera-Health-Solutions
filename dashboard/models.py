
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    class Meta:
        unique_together = ('first_name', 'last_name', 'phone_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
    profiles = models.ManyToManyField('UserProfile', related_name='files')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
