from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20250714_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardfileuser',
            name='user',
            field=models.ForeignKey(to='auth.User', on_delete=models.CASCADE),
        ),
    ]
