# from apscheduler.schedulers.background import BackgroundScheduler
# from django.core.mail import send_mail
# from django.utils.timezone import now
# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# import logging
# from subscriptions.models import UserProfile

# # Configure logging
# logger = logging.getLogger(__name__)

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
#                 emails_left = user_profile.current_plan.email_limit - user_profile.emails_sent
#             else:
#                 emails_left = None

#             # Send email limit warning
#             if emails_left is not None and emails_left <= 195:
#                 send_mail(
#                     'Email Limit Warning',
#                     f'You have only {emails_left} emails remaining in your plan. Please upgrade to continue uninterrupted.',
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_profile.user.email],
#                     fail_silently=False
#                 )
#                 logger.info(f"Email limit warning sent to {user_profile.user.email}.")

#             # Send plan expiry warning
#             if remaining_days is not None and remaining_days <= 7:
#                 send_mail(
#                     'Plan Expiry Warning',
#                     f'Your plan will expire in {remaining_days} days. Please renew it.',
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_profile.user.email],
#                     fail_silently=False
#                 )
#                 logger.info(f"Plan expiry warning sent to {user_profile.user.email}.")

#         except ObjectDoesNotExist:
#             logger.error(f"User profile data missing for user {user_profile.user.username}.")
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging
from subscriptions.models import UserProfile

# Configure logging
logger = logging.getLogger(__name__)


def check_and_send_email_notifications():
    """Check the user's email limit and plan expiration, and send emails accordingly."""
    logger.info("Running email notification task...")

    # Get all active user profiles
    user_profiles = UserProfile.objects.filter(plan_status="active")

    for user_profile in user_profiles:
        try:
            # Check plan expiration
            if user_profile.plan_expiration_date:
                remaining_days = (user_profile.plan_expiration_date - now()).days
            else:
                remaining_days = None

            # Get user's remaining emails
            if user_profile.current_plan:
                emails_left = (
                    user_profile.current_plan.email_limit - user_profile.emails_sent
                )
            else:
                emails_left = None

            # Send email limit warning
            if emails_left is not None and emails_left <= 195:
                send_mail(
                    "Email Limit Warning",
                    f"You have only {emails_left} emails remaining in your plan. Please upgrade to continue uninterrupted.",
                    settings.DEFAULT_FROM_EMAIL,
                    [user_profile.user.email],
                    fail_silently=False,
                )
                logger.info(f"Email limit warning sent to {user_profile.user.email}.")

            # Send plan expiry warning
            if remaining_days is not None and remaining_days <= 7:
                send_mail(
                    "Plan Expiry Warning",
                    f"Your plan will expire in {remaining_days} days. Please renew it.",
                    settings.DEFAULT_FROM_EMAIL,
                    [user_profile.user.email],
                    fail_silently=False,
                )
                logger.info(f"Plan expiry warning sent to {user_profile.user.email}.")

        except ObjectDoesNotExist:
            logger.error(
                f"User profile data missing for user {user_profile.user.username}."
            )


def start_scheduler():
    """Start the APScheduler for periodic tasks."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_send_email_notifications, "interval", hours=72
    )  # Run every 723 hours
    scheduler.start()
    logger.info("Scheduler started successfully.")


# def start_scheduler():
#     """Start the APScheduler for periodic tasks."""
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(check_and_send_email_notifications, 'interval', hours=72)  # Run every 6 hours
#     scheduler.start()
#     logger.info("Scheduler started successfully.")
