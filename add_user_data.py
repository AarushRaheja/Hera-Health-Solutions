import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_dashboard_project.settings')
django.setup()

from dashboard.models import UserProfile, File

# Add files to dashboard_file table
file1 = File(
    id="F001",
    name="Company Guidelines.pdf",
    upload_date="7/7/2025"
)
file1.save()

file2 = File(
    id="F002",
    name="Requirements.pdf",
    upload_date="4/11/2025"
)
file2.save()

file3 = File(
    id="F003",
    name="Employee Handbook.pdf",
    upload_date="2/5/2025"
)
file3.save()

print("Files added to dashboard_file table successfully!")

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