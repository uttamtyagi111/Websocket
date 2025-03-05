from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=255,blank=True, null=True, help_text="Key for Template")  
    file_url = models.URLField(max_length=1024)  
    uploaded_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name

class EmailStatusLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    status = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    from_email = models.EmailField()
    smtp_server = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.email} - {self.status} - {self.timestamp}"


class SMTPServer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    use_tls = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class ContactFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_files')
    name = models.CharField(max_length=255, help_text="User-defined name for the contact file")
    file = models.FileField(upload_to='contact_files/', help_text="Uploaded contact file", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    contact_file = models.ForeignKey(ContactFile, on_delete=models.CASCADE, related_name='contacts')
    data = models.JSONField(help_text="Data of the CSV row")

    def __str__(self):
        return f"Row in {self.contact_file.name}"
    
    
class SubjectFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="User-defined name for the Subject file")
    data = models.JSONField(default=list,help_text="Data of the CSV row")
    file = models.FileField(upload_to="subject_files/", help_text="Subject file", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subject File {self.id} - {self.user.email}"

        

class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255, help_text="Campaign name")
    subject_file = models.ForeignKey(SubjectFile, null=True, blank=True, on_delete=models.CASCADE) 
    contact_list = models.ForeignKey(ContactFile, on_delete=models.CASCADE, related_name='campaigns', help_text="Contact list associated with the campaign")
    delay_seconds = models.PositiveIntegerField(help_text="Delay between emails in seconds")
    smtp_servers = models.ManyToManyField('SMTPServer', related_name='campaigns', help_text="SMTP servers used for the campaign")
    uploaded_file = models.ForeignKey(UploadedFile, blank=True, null=True, on_delete=models.CASCADE, help_text="Template Associated with the campaign")
    display_name = models.CharField(max_length=255, blank=True, null=True, help_text="Display name for the sender")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the campaign was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the campaign was last updated")

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Unsubscribed(models.Model):
    email = models.EmailField(help_text="Email of the unsubscribed contact", null=True, blank=True)
    contact_file_name = models.CharField(
        max_length=255, help_text="Name of the contact file", null=True, blank=True
    )
    unsubscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} unsubscribed from {self.contact_file_name}"

