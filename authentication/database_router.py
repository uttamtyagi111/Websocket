class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """
        Attempts to read `model` from the 'db_login' or 'db_email' database.
        """
        if model._meta.app_label == "your_app_name_for_login":
            return "db_login"
        elif model._meta.app_label == "your_app_name_for_email":
            return "db_email"
        return "default"

    def db_for_write(self, model, **hints):
        """
        Attempts to write `model` to the 'db_login' or 'db_email' database.
        """
        if model._meta.app_label == "your_app_name_for_login":
            return "db_login"
        elif model._meta.app_label == "your_app_name_for_email":
            return "db_email"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in the same database.
        """
        if obj1._state.db in ["db_login", "db_email"] and obj2._state.db in [
            "db_login",
            "db_email",
        ]:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations only on the 'default' database.
        """
        if db in ["db_login", "db_email"]:
            return False
        return True
