# Generated by Django 5.2.3 on 2025-07-03 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='profiles',
            field=models.ManyToManyField(related_name='files', to='dashboard.userprofile'),
        ),
    ]
