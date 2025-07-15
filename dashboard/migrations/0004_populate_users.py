from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    
    # Create JohnDoe
    User.objects.create(
        username='JohnDoe',
        password=make_password('123'),
        first_name='John',
        last_name='Doe',
        email='johndoe@herahealth.com',
        is_staff=True
    )
    
    # Create HariSagar
    User.objects.create(
        username='HariSagar',
        password=make_password('Fluffy0!'),
        first_name='Hari',
        last_name='Sagar',
        email='hari.sagar@outlook.com',
        is_staff=True
    )
    
    # Create JimDoe
    User.objects.create(
        username='JimDoe',
        password=make_password('123'),
        first_name='Jim',
        last_name='Doe',
        email='jimdoe@herahealth.com',
        is_staff=True
    )
    
    # Create SamDoe
    User.objects.create(
        username='SamDoe',
        password=make_password('123'),
        first_name='Sam',
        last_name='Doe',
        email='samdoe@herahealth.com',
        is_staff=True
    )

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_add_user_field'),
    ]

    operations = [
        migrations.RunPython(create_users),
    ]
