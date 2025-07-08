
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
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, to_field='id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-viewed')

    class Meta:
        unique_together = ('file', 'user_profile')
        db_table = 'dashboard_file_user'

    def __str__(self):
        return f"File: {self.file.id}, User: {self.user_profile.id}, Status: {self.get_status_display()}"
