# Generated by Django 5.1.2 on 2025-02-27 15:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_sender', '0037_remove_campaign_uploaded_file_key_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='subject',
        ),
        migrations.CreateModel(
            name='SubjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='User-defined name for the Subject file', max_length=255)),
                ('file', models.FileField(blank=True, help_text='Subject file', null=True, upload_to='subject_files/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='subject_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='email_sender.subjectfile'),
        ),
    ]
