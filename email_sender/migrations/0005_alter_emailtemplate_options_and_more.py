# Generated by Django 5.1 on 2024-08-21 22:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_sender', '0004_emailtemplate_user_sender_user_smtpserver_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={},
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='body',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='user',
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='template_path',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.CreateModel(
            name='UserEditedTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_path', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('original_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='email_sender.emailtemplate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
