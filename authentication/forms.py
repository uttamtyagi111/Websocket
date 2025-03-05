from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import re


User = get_user_model()


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password..."}),
        label="Password",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.validate_password(password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character."
            )
        return password

    def validate_password(self, password):
        if password is None:
            return False
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True


class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email:
            self.add_error("email", "Email is required.")
        if not password:
            self.add_error("password", "Password is required.")

        return cleaned_data

    def get_user(self):
        User = get_user_model()
        try:
            user = User.objects.get(email=self.cleaned_data["email"])
            if user.check_password(self.cleaned_data["password"]):
                return user
        except User.DoesNotExist:
            return None


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address",
                "autocomplete": "off",
                "class": "form-control",
            }
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email exists.")
        return email


class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New Password..."}),
        label="New Password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password..."}),
        label="Confirm New Password",
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token", None)
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        if not self.validate_password(password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character."
            )
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        if self.token and self.token.is_expired():
            raise forms.ValidationError("This link has expired.")
        return cleaned_data

    def validate_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter OTP",
                "autocomplete": "off",
                "class": "form-control",
            }
        ),
    )
