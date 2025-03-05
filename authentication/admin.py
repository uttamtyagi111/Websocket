from django.contrib import admin
from .models import DeviceVerifyOTP, PasswordResetToken, LoginOTP
from django.utils.html import format_html
from datetime import datetime


class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token",
        "expires_at",
        "is_expired",
        "created_at",
        "delete_action",
    )
    search_fields = ("user__username", "user__email", "token")
    list_filter = ("expires_at", "created_at")

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.short_description = "Expired?"

    def delete_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Delete</a>',
            f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/delete/",
        )

    delete_action.short_description = "Delete"


admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)


class DeviceVerifyOTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "device_id",
        "otp",
        "expires_at",
        "is_expired",
        "created_at",
        "delete_action",
    )
    search_fields = ("user__username", "user__email", "otp", "device_id")
    list_filter = ("expires_at", "created_at")

    # def is_expired(self, obj):
    #     return obj.expires_at < timezone.now() + timedelta(minutes=5)
    # is_expired.boolean = True
    # is_expired.short_description = 'Expired?'

    def delete_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Delete</a>',
            f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/delete/",
        )

    delete_action.short_description = "Delete"


admin.site.register(DeviceVerifyOTP, DeviceVerifyOTPAdmin)


class LoginOTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "otp",
        "expires_at",
        "is_expired",
        "created_at",
        "delete_action",
    )
    search_fields = ("user__username", "user__email", "otp")
    list_filter = ("expires_at", "created_at")

    # def is_expired(self, obj):
    #     return obj.expires_at < timezone.now() + timedelta(minutes=5)
    # is_expired.boolean = True
    # is_expired.short_description = 'Expired?'

    def delete_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Delete</a>',
            f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/delete/",
        )

    delete_action.short_description = "Delete"


admin.site.register(LoginOTP, LoginOTPAdmin)


from django.contrib import admin
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Enquiry Details', {
            'fields': ('subject', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
