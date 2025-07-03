import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_dashboard_project.settings')
django.setup()

from dashboard.models import UserProfile

# Verify all user profiles
profiles = UserProfile.objects.all().order_by('id')

for profile in profiles:
    print(f"\nProfile ID: {profile.id}")
    print(f"First Name: {profile.first_name}")
    print(f"Last Name: {profile.last_name}")
    print(f"Phone Number: {profile.phone_number}")
    print(f"Email: {profile.email}")
