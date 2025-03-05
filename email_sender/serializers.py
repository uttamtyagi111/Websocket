from rest_framework import serializers
from .models import SMTPServer, UploadedFile, EmailStatusLog, ContactFile, Campaign


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["id", "user_id", "name", "key", "file_url"]


class EmailStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailStatusLog
        fields = [
            "id",
            "user",
            "email",
            "status",
            "timestamp",
            "from_email",
            "smtp_server",
        ]


class SMTPServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPServer
        fields = ["id", "name", "host", "port", "username", "password", "use_tls"]


from rest_framework import serializers
from .models import Campaign, ContactFile, SMTPServer


# class ContactFileSerializer(serializers.ModelSerializer):
#     """Serializer to represent contact file details."""
#     class Meta:
#         model = ContactFile
#         fields = ['id', 'name']  # Include any fields you want to expose


from rest_framework import serializers


class CampaignSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    smtp_server_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    display_name = serializers.CharField()
    delay_seconds = serializers.IntegerField(required=False, default=0)
    uploaded_file = serializers.IntegerField()
    contact_list = serializers.IntegerField()
    subject_file = serializers.IntegerField()

    class Meta:
        model = Campaign
        fields = "__all__"

    def validate_contact_list(self, value):
        if not ContactFile.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "The provided contact file ID does not exist."
            )
        return value
    
    def validate_uploaded_file(self, value):
        if not UploadedFile.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "The provided uploaded file ID does not exist."
            )
        return value
    
    
    def get_file_url(uploaded_file):
        uploaded_file = UploadedFile.objects.filter(name=uploaded_file).first()
        return uploaded_file.file_url if uploaded_file else None


    def validate_smtp_server_ids(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one SMTP server ID must be provided."
            )
        invalid_ids = [
            id for id in value if not SMTPServer.objects.filter(id=id).exists()
        ]
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid SMTP server IDs: {invalid_ids}")
        return value

    def create(self, validated_data):
        smtp_server_ids = validated_data.pop("smtp_server_ids", [])
        campaign = Campaign.objects.create(**validated_data)
        campaign.smtp_servers.set(SMTPServer.objects.filter(id__in=smtp_server_ids))
        return campaign

    def update(self, instance, validated_data):
        smtp_server_ids = validated_data.pop("smtp_server_ids", [])

        for attr, value in validated_data.items():
            if attr != "smtp_servers":
                setattr(instance, attr, value)

        if smtp_server_ids:
            instance.smtp_servers.set(SMTPServer.objects.filter(id__in=smtp_server_ids))

        instance.save()
        return instance

    def validate(self, data):
        if not data.get("smtp_server_ids"):
            raise serializers.ValidationError(
                "At least one SMTP server ID is required."
            )

        if data.get("delay_seconds", 0) < 0:
            raise serializers.ValidationError("Delay seconds cannot be negative.")

        return data

    def validate_name(self, value):
        """Ensure the campaign name is unique for the user when creating a new campaign."""
        request = self.context.get("request")
        campaign_id = self.instance.id if self.instance else None  # Current campaign ID

        if request and hasattr(request, "user"):
            # Agar naya campaign create ho raha hai (POST) ya naam change ho raha hai (PUT)
            if Campaign.objects.filter(name=value, user=request.user).exclude(id=campaign_id).exists():
                raise serializers.ValidationError(
                    "A campaign with this name already exists for the user."
                )

        return value


    def to_representation(self, instance):
        """Ensure `id` is included in the response."""
        data = super().to_representation(instance)
        data["id"] = instance.id  # Manually add the `id`
        return data


from rest_framework import serializers
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "contact_file", "data"]
