from django import forms
from .models import SMTPServer


class SMTPServerForm(forms.ModelForm):
    class Meta:
        model = SMTPServer
        fields = ["name", "host", "port", "username", "password", "use_tls"]


class EmailSendForm(forms.Form):
    smtp_server_ids = forms.ModelMultipleChoiceField(
        queryset=SMTPServer.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    email_list = forms.FileField()
    subject = forms.CharField(max_length=255)
    your_name = forms.CharField(max_length=100)
