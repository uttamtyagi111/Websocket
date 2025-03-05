from django.contrib import admin
from .models import Plan, UserProfile


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_days", "email_limit", "device_limit")
    search_fields = ("name", "price")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan_name",
        "plan_status",
        "emails_sent",
        "plan_expiration_date",
        "is_2fa_enabled",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("is_2fa_enabled", "plan_name", "plan_status")
    readonly_fields = ("emails_sent", "phonepe_transaction_id")

    def plan_name(self, obj):
        return obj.current_plan.name if obj.current_plan else "No Plan Assigned"

    plan_name.short_description = "Plan Name"


from subscriptions.models import UserDevice


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "id",
        "user",
        "device_name",
        "system_info",
        "token",
        "created_at",
    )
    search_fields = ("user__email", "device_name")
    list_filter = ("user", "device_name")
    readonly_fields = ("token",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(UserDevice, UserDeviceAdmin)
