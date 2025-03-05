from django import forms
from django.contrib import admin
from .models import (
    SMTPServer,
    UploadedFile,
    EmailStatusLog,
    Contact,
    ContactFile,
    Campaign,
    Unsubscribed,
)


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "name", "file_url")


@admin.register(SMTPServer)
class SMTPServerAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "name", "host", "port", "username", "use_tls")
    search_fields = ("name", "host", "username")
    ordering = ("name",)


@admin.register(EmailStatusLog)
class EmailStatusLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "status",
        "timestamp",
        "user",
        "from_email",
        "smtp_server",
    )
    search_fields = ("email", "status", "from_email")

    def user(self, obj):
        return obj.user.username

    user.short_description = "User"


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0  # No extra empty rows by default
    fields = ("data",)
    readonly_fields = ("data",)  # Make the data field read-only for admin display


@admin.register(ContactFile)
class ContactFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "uploaded_at",
    )  # Fields to display in the list view
    list_filter = ("user", "uploaded_at")  # Filters for easier navigation
    search_fields = ("name", "user__username")  # Search functionality
    inlines = [ContactInline]  # Display associated contacts inline


class ContactAdminForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"

    # If `data` is a JSONField, you can create a custom widget for better editing
    data = forms.JSONField(widget=forms.Textarea(attrs={"rows": 4, "cols": 50}))


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactAdminForm
    list_display = (
        "id",
        "contact_file",
        "data",
    )  # Display contact file and email in the list
    list_filter = ("contact_file",)  # Filter by contact file
    search_fields = (
        "contact_file__name",
    )  # Search by contact file name and email inside data
    readonly_fields = ()  # Make the data field editable
    actions = ["make_unsubscribed"]

    # Optionally, create a custom function to extract and display email from data
    def email(self, obj):
        return obj.data.get("email", "N/A")

    email.short_description = "Email"

    # Optional action for unsubscribing contacts
    def make_unsubscribed(self, request, queryset):
        # Logic for unsubscribing the contacts (You can implement this based on your requirements)
        pass

    make_unsubscribed.short_description = "Mark selected contacts as unsubscribed"


from django.contrib import admin
from .models import Campaign, SubjectFile  # Import SubjectFile

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user", 
        "uploaded_file",
        "display_name",
        "delay_seconds",
        "created_at",
    )
    list_filter = ("created_at", "user")
    search_fields = ("name", "subject_file__name", "user__email")  # Updated search_fields
    ordering = ("-created_at",) # If ForeignKey



@admin.register(Unsubscribed)
class UnsubscribedAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "contact_file_name",
        "unsubscribed_at",
    )  # Update fields here
    list_filter = ("contact_file_name", "unsubscribed_at")  # Update fields here
    search_fields = ("email", "contact_file_name")  # Allow searching by these fields



from django.contrib import admin
from .models import SubjectFile

@admin.register(SubjectFile)
class SubjectFileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "uploaded_at")  # Display key fields in admin panel
    list_filter = ("uploaded_at", "user")  # Filter by user and upload date
    search_fields = ("name", "user__email")  # Enable search for file name & user email
    ordering = ("-uploaded_at",)  # Order by latest uploaded file first



# from django.contrib import admin
# from .models import Campaign, SMTPServer

# class SMTPServerInline(admin.TabularInline):  
#     model = Campaign.smtp_servers.through  # ManyToManyField ka through model use karna hoga
#     extra = 1  # Kitne extra blank fields dikhe admin panel me

# @admin.register(Campaign)
# class CampaignAdmin(admin.ModelAdmin):
#     list_display = ('name', 'user', 'subject', 'created_at', 'updated_at')
#     search_fields = ('name', 'user__email')
#     list_filter = ('created_at',)
#     filter_horizontal = ('smtp_servers',)  # Multi-select box ke liye
#     inlines = [SMTPServerInline]  # Inline SMTP Server edit option add kiya
