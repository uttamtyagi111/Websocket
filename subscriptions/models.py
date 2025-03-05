from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Plan(models.Model):
    name = models.CharField(max_length=100)
    email_limit = models.IntegerField(default=20)
    device_limit = models.IntegerField(default=1)
    duration_days = models.IntegerField(default=14)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    level = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


def get_trial_expiration_date():
    """Return the expiration date for a 14-day trial."""
    return timezone.now() + timedelta(days=14)


from django.core.validators import RegexValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    plan_name = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    plan_status = models.CharField(max_length=20, default="inactive")
    emails_sent = models.IntegerField(default=0)
    email_limit = models.IntegerField(default=0)
    # razorpay_order_id = models.CharField(max_length=255, blank=True, null=True,unique=True)
    # razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True,unique=True)
    phonepe_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20, default="pending"
    )  # Add payment status
    plan_start_date = models.DateTimeField(null=True, blank=True)
    plan_expiration_date = models.DateTimeField(
        default=get_trial_expiration_date, null=True, blank=True
    )
    current_plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True
    )
    pending_plan_id = models.IntegerField(null=True, blank=True)
    # for billing address
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(
        max_length=15,  # Allows for international numbers
        validators=[
            RegexValidator(r"^\+?\d{10,15}$", message="Enter a valid mobile number.")
        ],
        null=True,
        blank=True,
    )
    is_2fa_enabled = models.BooleanField(default=False)

    DEFAULT_TRIAL_LIMIT = 20

    def can_send_email(self):
        """Check if the user can send an email based on their plan and email limit."""

        if self.current_plan is None:  # Trial logic
            if timezone.now() > self.plan_expiration_date:
                self.plan_status = "expired"
                self.save()
                return False, "Trial period has expired. Please subscribe to a plan."

            if self.emails_sent >= self.DEFAULT_TRIAL_LIMIT:
                self.plan_status = "expired"
                self.save()
                return False, "Trial limit exceeded. Please subscribe to a plan."

            return True, "You are on a trial; you can send more emails."

        if self.plan_expiration_date <= timezone.now():
            self.plan_status = "expired"
            self.save()
            return False, "Your subscription has expired. Please renew your plan."

        if self.email_limit == 0:
            return True, "You have unlimited email sending capabilities."

        if self.emails_sent < self.email_limit:
            return True, "You can send emails."

        self.plan_status = "expired"
        self.save()
        return False, "Plan expired . Please renew or upgrade your plan."

    def activate_plan(self, plan):
        """Activate a new plan for the user."""
        self.current_plan = plan
        self.plan_name = plan.name
        self.plan_status = "active"
        self.plan_start_date = timezone.now()
        self.plan_expiration_date = timezone.now() + timedelta(days=plan.duration_days)
        self.payment_status = "paid"
        self.emails_sent = 0
        self.email_limit = plan.email_limit
        self.pending_plan_id = None
        self.save()

    def choose_plan_view(self, new_plan):
        """Subscribe the user to a selected plan."""
        self.activate_plan(new_plan)
        self.email_limit = new_plan.email_limit
        self.save()

    def increment_email_count(self):
        """Increment the number of emails sent by the user."""
        self.emails_sent += 1
        self.save()

    def check_plan_status(self):
        if self.plan_expiration_date < timezone.now():
            return "Expired"
        return "Active"


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
    device_name = models.CharField(max_length=100)
    system_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name} - {self.user.email}"
