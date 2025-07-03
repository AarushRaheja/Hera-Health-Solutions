import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_dashboard_project.settings')
django.setup()

from dashboard.models import UserProfile

# Create a new user profile with the specified data
user_profile = UserProfile(
    id=123,
    first_name="Joe",
    last_name="Johnson",
    phone_number="415-223-5921",
    email="joe.johnson@herahealth.com"
)

# Save the user profile to the database
user_profile.save()

print("User profile created successfully!")

user_profile = UserProfile(
    id=456,
    first_name="John",
    last_name="Doe",
    phone_number="245-293-9182",
    email="john.doe@herahealth.com"
)

# Save the user profile to the database
user_profile.save()

print("User profile created successfully!")

user_profile = UserProfile(
    id=789,
    first_name="Tim",
    last_name="Health",
    phone_number="329-190-9042",
    email="tim.health@herahealth.com"
)

# Save the user profile to the database
user_profile.save()

print("User profile created successfully!")