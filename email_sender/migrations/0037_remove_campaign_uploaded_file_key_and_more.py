# Generated by Django 5.1.2 on 2025-02-19 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_sender', '0036_uploadedfile_key_alter_uploadedfile_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='uploaded_file_key',
        ),
        migrations.AddField(
            model_name='campaign',
            name='uploaded_file_name',
            field=models.CharField(blank=True, help_text='name for the uploaded file', max_length=255, null=True),
        ),
    ]
