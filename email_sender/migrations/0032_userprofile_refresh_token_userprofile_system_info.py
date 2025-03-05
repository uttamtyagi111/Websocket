# Generated by Django 5.1.2 on 2024-11-04 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_sender', '0031_remove_userprofile_refresh_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='refresh_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='system_info',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
