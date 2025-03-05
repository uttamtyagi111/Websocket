from django.apps import AppConfig


class EmailSenderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "email_sender"

    # def ready(self):
    #     pass
    def ready(self):
        # Import and start the scheduler
        from email_sender.scheduler import start_scheduler

        start_scheduler()
