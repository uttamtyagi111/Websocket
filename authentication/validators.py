import re
from django.core.exceptions import ValidationError


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "The password must contain at least one uppercase letter.",
                code="password_no_upper",
            )
        if not re.search(r"\d", password):
            raise ValidationError(
                "The password must contain at least one digit.",
                code="password_no_number",
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "The password must contain at least one special character.",
                code="password_no_special",
            )

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, "
            "one digit, and one special character."
        )
