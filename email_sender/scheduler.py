from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
from django.conf import settings
import logging
from subscriptions.models import UserProfile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def check_and_send_email_notifications():
    """Check the user's email limit and plan expiration, and send emails accordingly."""
    logger.info("Running email notification task...")

    # Get all active user profiles
    user_profiles = UserProfile.objects.filter(plan_status="active")

    for user_profile in user_profiles:
        try:
            # 🔹 Check plan expiration
            remaining_days = (
                (user_profile.plan_expiration_date - now()).days
                if user_profile.plan_expiration_date
                else None
            )

            # 🔹 Get user's remaining emails
            emails_left = (
                user_profile.current_plan.email_limit - user_profile.emails_sent
                if user_profile.current_plan
                else None
            )

            # 🔸 Send email limit warning when only 5 emails are left
            if emails_left is not None and emails_left <= 5:
                email_body = render_to_string(
                    "subscriptions/email_limit_warning.html",
                    {
                        "username": user_profile.user.username,
                        "plan_name": user_profile.current_plan.name,
                        "email_limit": user_profile.current_plan.email_limit,
                        "emails_left": emails_left,
                    },
                )

                email = EmailMessage(
                    subject="Email Limit Warning",
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_profile.user.email],
                )

                email.content_subtype = "html"
                email.send()
                logger.info(f"Email limit warning sent to {user_profile.user.email}.")

            # 🔸 Send plan expiry warning when only 7 days are left
            if remaining_days is not None and remaining_days <= 7:
                email_body = render_to_string(
                    "subscriptions/plan_expiry_warning.html",
                    {
                        "username": user_profile.user.username,
                        "plan_name": user_profile.current_plan.name,
                        "plan_expiration_date": user_profile.plan_expiration_date.strftime("%d %B %Y"),
                        "remaining_days": remaining_days,
                    },
                )

                email = EmailMessage(
                    subject="Plan Expiry Warning",
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_profile.user.email],
                )

                email.content_subtype = "html"
                email.send()
                logger.info(f"Plan expiry warning sent to {user_profile.user.email}.")

        except Exception as e:
            logger.error(f"Error sending notifications for {user_profile.user.username}: {e}")

# def check_and_send_email_notifications():
#     """Check the user's email limit and plan expiration, and send emails accordingly."""
#     logger.info("Running email notification task...")

#     # Get all active user profiles
#     user_profiles = UserProfile.objects.filter(plan_status="active")

#     for user_profile in user_profiles:
#         try:
#             # Check plan expiration
#             if user_profile.plan_expiration_date:
#                 remaining_days = (user_profile.plan_expiration_date - now()).days
#             else:
#                 remaining_days = None

#             # Get user's remaining emails
#             if user_profile.current_plan:
#                 emails_left = (
#                     user_profile.current_plan.email_limit - user_profile.emails_sent
#                 )
#             else:
#                 emails_left = None

#             # Send email limit warning
#             if emails_left is not None and emails_left <= 195:
#                 send_mail(
#                     "Email Limit Warning",
#                     f"You have only {emails_left} emails remaining in your plan. Please upgrade to continue uninterrupted.",
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_profile.user.email],
#                     fail_silently=False,
#                 )
#                 logger.info(f"Email limit warning sent to {user_profile.user.email}.")

#             # Send plan expiry warning
#             if remaining_days is not None and remaining_days <= 7:
#                 send_mail(
#                     "Plan Expiry Warning",
#                     f"Your plan will expire in {remaining_days} days. Please renew it.",
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_profile.user.email],
#                     fail_silently=False,
#                 )
#                 logger.info(f"Plan expiry warning sent to {user_profile.user.email}.")

#         except ObjectDoesNotExist:
#             logger.error(
#                 f"User profile data missing for user {user_profile.user.username}."
#             )


def start_scheduler():
    """Start the APScheduler for periodic tasks."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_send_email_notifications, "interval", hours=72
    )  # Run every 72 hours
    scheduler.start()
    logger.info("Scheduler started successfully.")

