# Generated by Django 5.1.7 on 2025-03-25 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_app', '0003_repository_updated_at_repository_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='file_path',
        ),
        migrations.AddField(
            model_name='report',
            name='report_content',
            field=models.TextField(default='null'),
            preserve_default=False,
        ),
    ]
