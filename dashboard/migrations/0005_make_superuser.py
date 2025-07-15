from django.db import migrations, models
from django.contrib.auth.models import User

def make_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    user = User.objects.get(id=2)
    user.is_superuser = True
    user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_populate_users'),
    ]

    operations = [
        migrations.RunPython(make_superuser),
    ]
