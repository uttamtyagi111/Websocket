from rest_framework.views import APIView
from rest_framework import serializers
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import async_to_sync
from django.utils.timezone import now
from .models import SubjectFile
from channels.layers import get_channel_layer
from email_validator import validate_email, EmailNotValidError
import dns.resolver
from django.core.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from subscriptions.models import UserProfile, Plan
from .serializers import EmailStatusLogSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from django.core.mail import EmailMessage, get_connection
from io import StringIO
from django.template import Template, Context
import csv, time, logging, os, boto3, time, uuid
from django.conf import settings
from .serializers import (
    CampaignSerializer,
    SMTPServerSerializer,
    UploadedFileSerializer,
    ContactSerializer,
)
from .models import (
    SMTPServer,
    UploadedFile,
    Campaign,
    ContactFile,
    Contact,
    Unsubscribed,
    EmailStatusLog,
    SubjectFile,
)
from django.shortcuts import get_object_or_404
from .forms import SMTPServerForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def smtp_servers_list(request):
    request_user_id = request.data.get("user_id")
    servers = SMTPServer.objects.filter(user_id=request_user_id)
    serializer = SMTPServerSerializer(servers, many=True)
    return Response({"servers": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def smtp_server_detail(request, pk):
    server = get_object_or_404(SMTPServer, pk=pk, user=request.user)
    serializer = SMTPServerSerializer(server)
    return Response({"server": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def smtp_server_create(request):
    serializer = SMTPServerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            {"message": "SMTP server created successfully.", "server": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def smtp_server_edit(request, pk):
    smtp_server = get_object_or_404(SMTPServer, pk=pk, user=request.user)
    form = SMTPServerForm(request.data, instance=smtp_server)

    if form.is_valid():
        smtp_server = form.save(commit=False)
        smtp_server.user = request.user
        smtp_server.save()
        return JsonResponse(
            {
                "message": "SMTP server updated successfully.",
                "success": True,
                "redirect": "smtp-servers-list",
            },
            status=200,
        )
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def smtp_server_delete(request, pk):
    smtp_server = SMTPServer.objects.filter(pk=pk, user_id=request.user.id).first()
    if smtp_server is None:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    smtp_server.delete()
    return Response(
        {"meesage": "smtp-server deleted successfully"},
        status=status.HTTP_204_NO_CONTENT,
    )


def replace_special_characters(content):
    replacements = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201C": '"',
        "\u201D": '"',
    }
    if content:
        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)
    return content


class UploadHTMLToS3(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"FILES: {request.FILES}")
        logger.debug(f"DATA: {request.data}")

        html_content = None
        user_given_name = request.data.get("name")

        if not user_given_name:
            return Response(
                {"error": "Name is required for the template."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "file" in request.FILES:
            file = request.FILES["file"]
            if not file.name.endswith(".html"):
                return Response(
                    {"error": "File must be an HTML file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            html_content = file.read()

        elif "html_content" in request.data:
            html_content = request.data.get("html_content")
            if not isinstance(html_content, str):
                return Response(
                    {"error": "HTML content must be a string."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            html_content = html_content.encode("utf-8")

        if not html_content:
            return Response(
                {"error": "No HTML content provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_name = f"{uuid.uuid4()}.html"

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_name,
                Body=html_content,
                ContentType="text/html",
            )
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        file_url = f"{settings.AWS_S3_FILE_URL}{file_name}"

        uploaded_file = UploadedFile.objects.create(
            name=user_given_name, file_url=file_url, key=file_name, user=request.user
        )

        return Response(
            {
                "user_id": request.user.id,
                "name": uploaded_file.name,
                "file_url": uploaded_file.file_url,
                "file_key": file_name,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadedFileList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        uploaded_files = UploadedFile.objects.filter(user=request.user)
        serializer = UploadedFileSerializer(uploaded_files, many=True)
        return Response(serializer.data)


class UploadedFileDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        uploaded_files = get_object_or_404(UploadedFile, id=file_id, user=request.user)
        serializer = UploadedFileSerializer(uploaded_files)
        return Response(serializer.data)


class UpdateUploadedFile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        new_user_given_name = request.data.get("name", uploaded_file.name)

        if not new_user_given_name.endswith(".html"):
            new_user_given_name += ".html"

        existing_s3_key = uploaded_file.key

        try:
            s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_s3_key
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to delete old file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        counter = 1
        new_s3_key = existing_s3_key

        while True:
            try:
                s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=new_s3_key)
                new_s3_key = f"{existing_s3_key.split('.')[0]}({counter}).{existing_s3_key.split('.')[-1]}"
                counter += 1
            except s3.exceptions.ClientError:
                break

        try:
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=new_s3_key,
                Body=file,
                ContentType="text/html",
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        uploaded_file.name = new_user_given_name
        uploaded_file.key = new_s3_key
        uploaded_file.file_url = f"{settings.AWS_S3_FILE_URL}{new_s3_key}"
        uploaded_file.save()

        return Response(
            {
                "message": "File updated successfully.",
                "file_name": uploaded_file.name,
                "file_key": uploaded_file.key,
                "file_url": uploaded_file.file_url,
            },
            status=status.HTTP_200_OK,
        )


class UploadedFileDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)

        file_key = uploaded_file.key
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            uploaded_file.delete()

            return Response(
                {"message": "File deleted successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# class UpdateUploadedFile(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, file_id):
#         uploaded_file = get_object_or_404(UploadedFile, id=file_id)

#         s3 = boto3.client(
#             "s3",
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             region_name=settings.AWS_S3_REGION_NAME,
#         )

#         existing_file_name = uploaded_file.name

#         try:
#             s3.delete_object(
#                 Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=existing_file_name
#             )
#         except Exception as e:
#             return Response(
#                 {"error": f"Failed to delete old file: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         if "file" not in request.FILES:
#             return Response(
#                 {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         file = request.FILES["file"]

#         counter = 1
#         new_file_name = existing_file_name

#         while True:
#             try:
#                 s3.head_object(
#                     Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=new_file_name
#                 )
#                 new_file_name = f"{existing_file_name.split('.')[0]}({counter}).{existing_file_name.split('.')[-1]}"
#                 counter += 1
#             except s3.exceptions.ClientError:
#                 break

#         try:
#             s3.put_object(
#                 Bucket=settings.AWS_STORAGE_BUCKET_NAME,
#                 Key=new_file_name,
#                 Body=file,
#                 ContentType="text/html",
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#         uploaded_file.name = new_file_name
#         uploaded_file.file_url = f"{settings.AWS_S3_FILE_URL}{new_file_name}"
#         uploaded_file.save()

#         return Response(
#             {"file_name": new_file_name, "file_url": uploaded_file.file_url},
#             status=status.HTTP_200_OK,
#         )


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = UploadedFileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ContactUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user

#         if ContactFile.objects.filter(user=user).count() >= 10:
#             return Response(
#                 {
#                     "error": "You have already uploaded 10 contact lists. To upload a new list, please delete an existing one."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         csv_file = request.FILES.get("csv_file")
#         file_name = request.data.get("name")

#         if not csv_file:
#             return Response(
#                 {"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST
#             )
#         if not file_name:
#             return Response(
#                 {"error": "File name is required."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         if ContactFile.objects.filter(user=user, name=file_name).exists():
#             return Response(
#                 {
#                     "error": f'A file with the name "{file_name}" already exists. Please use a different name.'
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             decoded_file = csv_file.read().decode("utf-8")
#             reader = csv.DictReader(StringIO(decoded_file))

#             if not reader.fieldnames:
#                 raise ValueError("CSV file is missing headers.")
#         except Exception as e:
#             return Response(
#                 {"error": f"Invalid CSV file format: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         contact_file = ContactFile.objects.create(user=user, name=file_name)

#         contacts = []
#         row_count = 0
#         for row in reader:
#             if any(row.values()):
#                 contacts.append(Contact(contact_file=contact_file, data=row))
#                 row_count += 1
#         Contact.objects.bulk_create(contacts)


#         return Response(
#             {
#                 "message": "Contacts uploaded and saved successfully.",
#                 "file_name": file_name,
#                 "total_contacts": row_count,
#                 "created_at": contact_file.uploaded_at.strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 ),
#             },
#             status=status.HTTP_201_CREATED,
#         )
class ContactUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        logger.info(f"User {user.email} is attempting to upload a contact file.")

        if ContactFile.objects.filter(user=user).count() >= 10:
            logger.warning(f"User {user.email} has reached the maximum upload limit.")
            return Response(
                {
                    "error": "You have already uploaded 10 contact lists. To upload a new list, please delete an existing one."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        csv_file = request.FILES.get("csv_file")
        file_name = request.data.get("name")

        if not csv_file:
            logger.error(
                f"User {user.email} tried to upload without providing a CSV file."
            )
            return Response(
                {"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not file_name:
            logger.error(
                f"User {user.email} tried to upload without providing a file name."
            )
            return Response(
                {"error": "File name is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if ContactFile.objects.filter(user=user, name=file_name).exists():
            logger.warning(
                f'User {user.email} tried to upload a duplicate file name: "{file_name}".'
            )
            return Response(
                {
                    "error": f'A file with the name "{file_name}" already exists. Please use a different name.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decoded_file = csv_file.read().decode("utf-8")
            reader = csv.DictReader(StringIO(decoded_file))

            if not reader.fieldnames:
                raise ValueError("CSV file is missing headers.")

        except Exception as e:
            logger.error(f"User {user.email} uploaded an invalid CSV file: {str(e)}")
            return Response(
                {"error": f"Invalid CSV file format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        contact_file = ContactFile.objects.create(user=user, name=file_name)
        logger.info(f'User {user.email} successfully uploaded file "{file_name}".')

        contacts = []
        row_count = 0
        for row in reader:
            if any(row.values()):
                contacts.append(Contact(contact_file=contact_file, data=row))
                row_count += 1

        Contact.objects.bulk_create(contacts)
        logger.info(
            f'User {user.email} - {row_count} contacts saved from "{file_name}".'
        )

        return Response(
            {
                "message": "Contacts uploaded and saved successfully.",
                "file_name": file_name,
                "total_contacts": row_count,
                "created_at": contact_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED,
        )


class ContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        file_id = request.query_params.get("file_id")

        if not file_id:
            return Response(
                {"error": "file_id is required to fetch contacts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            contact_file = ContactFile.objects.get(id=file_id, user=user)
        except ContactFile.DoesNotExist:
            return Response(
                {
                    "error": "Contact file not found or you do not have permission to access it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        contacts = Contact.objects.filter(contact_file=contact_file).values(
            "id", "data"
        )
        return Response(
            {"file_name": contact_file.name, "contacts": list(contacts)},
            status=status.HTTP_200_OK,
        )


class UserContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        contact_files = ContactFile.objects.filter(user=user)

        if not contact_files.exists():
            return Response(
                {"error": "No contact files found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        contact_list = []
        for contact_file in contact_files:
            contacts = Contact.objects.filter(contact_file=contact_file).values("data")
            contact_list.append(
                {
                    "file_id": contact_file.id,
                    "file_name": contact_file.name,
                    "contacts": list(contacts),
                    "created_at": contact_file.uploaded_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

        return Response({"user_contact_files": contact_list}, status=status.HTTP_200_OK)


from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class ContactFileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        """
        Update an existing contact file with a new CSV.
        This allows the user to edit and add new rows with new fields.
        """
        user = request.user

        try:
            contact_file = ContactFile.objects.get(id=file_id, user=user)
        except ContactFile.DoesNotExist:
            return Response(
                {
                    "error": "Contact file not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        contacts_data = request.data.get("contacts")
        if not contacts_data:
            return Response(
                {"error": "No contacts data provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_contacts = []
        new_contacts = []
        row_count = 0
        new_rows_count = 0

        existing_contact_ids = set(
            Contact.objects.filter(contact_file=contact_file).values_list(
                "id", flat=True
            )
        )

        with transaction.atomic():
            for row in contacts_data:
                contact_id = row.get("id")
                data = row.get("data", {})

                if contact_id in existing_contact_ids:
                    contact = Contact.objects.get(
                        id=contact_id, contact_file=contact_file
                    )
                    contact.data.update(data)
                    updated_contacts.append(contact)
                    row_count += 1
                else:
                    new_contacts.append(Contact(contact_file=contact_file, data=data))
                    new_rows_count += 1

            if updated_contacts:
                Contact.objects.bulk_update(updated_contacts, ["data"])
            if new_contacts:
                Contact.objects.bulk_create(new_contacts)

        return Response(
            {
                "message": "Contacts updated and new rows added successfully.",
                "file_name": contact_file.name,
                "total_contacts_updated": row_count,
                "total_new_rows": new_rows_count,
                "created_at": contact_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_200_OK,
        )


# class ContactFileUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, file_id):
#         """
#         Update an existing contact file with a new CSV.
#         This allows the user to edit and add new rows with new fields.
#         """
#         user = request.user

#         try:
#             contact_file = ContactFile.objects.get(id=file_id, user=user)
#         except ContactFile.DoesNotExist:
#             return Response(
#                 {
#                     "error": "Contact file not found or you do not have permission to update it."
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         contacts_data = request.data.get("contacts")
#         if not contacts_data:
#             return Response(
#                 {"error": "No contacts data provided."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         updated_contacts = []
#         row_count = 0
#         new_rows_count = 0

#         for row in contacts_data:
#             contact_id = row.get("id")
#             if contact_id:
#                 try:
#                     contact = Contact.objects.get(
#                         id=contact_id, contact_file=contact_file
#                     )
#                     contact.data.update(
#                         row.get("data", {})
#                     )
#                     contact.save()
#                     updated_contacts.append(contact)
#                     row_count += 1
#                 except Contact.DoesNotExist:
#                     continue
#             else:
#                 new_row = row.get("data", {})
#                 if new_row:
#                     contact = Contact(contact_file=contact_file, data=new_row)
#                     contact.save()
#                     updated_contacts.append(contact)
#                     new_rows_count += 1

#         return Response(
#             {
#                 "message": "Contacts updated and new rows added successfully.",
#                 "file_name": contact_file.name,
#                 "total_contacts_updated": row_count,
#                 "total_new_rows": new_rows_count,
#                 "created_at": contact_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
#             },
#             status=status.HTTP_200_OK,
#         )


class DeleteContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        file_id = request.query_params.get("file_id")

        if not file_id:
            return Response(
                {"error": "file_id is required to delete a contact list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            contact_file = ContactFile.objects.get(id=file_id, user=user)
        except ContactFile.DoesNotExist:
            return Response(
                {
                    "error": "Contact file not found or you do not have permission to delete it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        Contact.objects.filter(contact_file=contact_file).delete()

        contact_file.delete()

        return Response(
            {"message": "Contact list deleted successfully."}, status=status.HTTP_200_OK
        )


class ContactUnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, contact_file_id, contact_id):
        try:
            contact = Contact.objects.get(
                id=contact_id, contact_file_id=contact_file_id
            )
            contact_file = ContactFile.objects.get(id=contact_file_id)

            unsubscribed_entry = Unsubscribed.objects.create(
                email=contact.data.get("Email"),
                contact_file_name=contact_file.name,
            )
            contact.delete()
            if unsubscribed_entry:
                return Response(
                    {
                        "message": "Unsubscribed successfully",
                        "email": unsubscribed_entry.email,
                        "contact_file": contact_file.name,
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"error": "Failed to unsubscribe"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Contact.DoesNotExist:
            return Response(
                {"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ContactFile.DoesNotExist:
            return Response(
                {"error": "Contact file not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


logger = logging.getLogger(__name__)


class CampaignListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            campaigns = Campaign.objects.filter(user=request.user).prefetch_related(
                "smtp_servers"
            )

            campaign_data = []
            for campaign in campaigns:
                campaign_data.append(
                    {
                        "id": campaign.id,
                        "name": campaign.name,
                        "subject_file_id": campaign.subject_file_id,
                        "contact_list_id": campaign.contact_list_id,
                        "delay_seconds": campaign.delay_seconds,
                        "uploaded_file_name": campaign.uploaded_file.name,
                        "display_name": campaign.display_name,
                        "smtp_server_ids": list(
                            campaign.smtp_servers.values_list("id", flat=True)
                        ),
                    }
                )

            logger.info(
                f"User {request.user.email} retrieved {len(campaign_data)} campaigns."
            )
            return Response(campaign_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Error retrieving campaigns for user {request.user.email}: {str(e)}"
            )
            return Response(
                {"error": "Failed to retrieve campaigns"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CampaignView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        campaign_id = kwargs.get("id")
        if not campaign_id:
            return Response(
                {"error": "Campaign ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign = (
            Campaign.objects.filter(id=campaign_id, user=request.user)
            .values(
                "id",
                "name",
                "subject_file_id",
                "uploaded_file_id",
                "display_name",
                "delay_seconds",
                "contact_list_id",
            )
            .first()
        )

        if not campaign:
            return Response(
                {"error": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND
            )
        uploaded_file_id = campaign.get("uploaded_file_id")
        file_url = None
        if uploaded_file_id:
            uploaded_file = UploadedFile.objects.filter(id=uploaded_file_id).first()
            file_url = uploaded_file.file_url if uploaded_file else None

        smtp_server_ids = list(
            Campaign.objects.get(id=campaign_id).smtp_servers.values_list(
                "id", flat=True
            )
        )
        campaign["smtp_server_ids"] = smtp_server_ids
        campaign["file_url"] = file_url
        return Response(campaign, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        logger.debug(f"Request Data: {request.data}")
        serializer = CampaignSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user_campaign_count = Campaign.objects.filter(user=request.user).count()
            if user_campaign_count >= 10:
                return Response(
                    {"error": "You can only save up to 10 campaigns."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            name = serializer.validated_data["name"]
            contact_file_id = serializer.validated_data["contact_list"]
            smtp_server_ids = serializer.validated_data["smtp_server_ids"]
            delay_seconds = serializer.validated_data.get("delay_seconds", 0)
            uploaded_file_id = serializer.validated_data["uploaded_file"]
            display_name = serializer.validated_data["display_name"]
            subject_file_id = serializer.validated_data.get("subject_file")

            logger.debug(f"Received Data: {serializer.validated_data}")
            subject_file = None
            if subject_file_id:
                try:
                    subject_file = SubjectFile.objects.get(
                        id=subject_file_id, user=request.user
                    )
                except SubjectFile.DoesNotExist:
                    return Response(
                        {"error": "Subject file not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            try:
                contact_file = ContactFile.objects.get(
                    id=contact_file_id, user=request.user
                )
            except ContactFile.DoesNotExist:
                return Response(
                    {"error": "Contact file not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            try:
                uploaded_file = UploadedFile.objects.get(
                    id=uploaded_file_id, user=request.user
                )
            except UploadedFile.DoesNotExist:
                return Response(
                    {"error": "Template file not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            smtp_servers = SMTPServer.objects.filter(
                id__in=smtp_server_ids, user=request.user
            )
            if not smtp_servers.exists():
                return Response(
                    {
                        "error": "Selected SMTP servers not found or do not belong to the user."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            campaign = Campaign.objects.create(
                name=name,
                user=request.user,
                subject_file=subject_file,
                uploaded_file=uploaded_file,
                display_name=display_name,
                delay_seconds=delay_seconds,
                contact_list=contact_file,
            )

            if not campaign.id:
                logger.error("Campaign ID is missing after creation.")
                return Response(
                    {"error": "Failed to create campaign. Try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            logger.debug(f"Campaign Created Successfully: ID = {campaign.id}")

            campaign.smtp_servers.set(smtp_servers)

            contacts = contact_file.contacts.all()
            contact_serializer = ContactSerializer(contacts, many=True)
            logger.info(
                f"Campaign Created: {campaign.id}, Contacts Count: {len(contact_serializer.data)}"
            )

            return Response(
                {
                    "status": "Campaign saved successfully.",
                    "campaign_id": campaign.id,
                    "campaign_name": name,
                    "contacts": contact_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        logger.warning(f"Serializer Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        campaign_id = kwargs.get("id")
        if not campaign_id:
            return Response(
                {"error": "Campaign ID is required for updating."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            campaign = Campaign.objects.get(id=campaign_id, user=request.user)
        except Campaign.DoesNotExist:
            return Response(
                {"error": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignSerializer(
            campaign, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "Campaign updated successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        campaign_id = kwargs.get("id")
        if not campaign_id:
            return Response(
                {"error": "Campaign ID is required for deletion."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            campaign = Campaign.objects.get(id=campaign_id, user=request.user)
            campaign.delete()
            return Response(
                {"status": "Campaign deleted successfully."}, status=status.HTTP_200_OK
            )
        except Campaign.DoesNotExist:
            return Response(
                {"error": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND
            )


class SendEmailsView(APIView):
    DEFAULT_EMAIL_LIMIT = 20

    def get_html_content_from_s3(self, uploaded_file_name):
        """Fetches HTML content from S3 using the file name by retrieving the key from the database."""
        try:
            # Pehle database se uploaded file ka key dhundo
            uploaded_file = UploadedFile.objects.filter(name=uploaded_file_name).first()

            if not uploaded_file:
                logger.error(
                    f"No file found in database with name: {uploaded_file_name}"
                )
                return None

            key = uploaded_file.key  # Ye column check kar lo tumhare model me

            # AWS S3 Client
            session = boto3.session.Session()
            s3 = session.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            # S3 se file fetch karna
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)

            if "Body" in response:
                return response["Body"].read().decode("utf-8")

            logger.error(f"File {key} found in S3 but has no content.")
            return None

        except s3.exceptions.NoSuchKey:
            logger.error(f"File {key} does not exist in S3.")
        except s3.exceptions.ClientError as e:
            logger.error(f"Client error while fetching {key} from S3: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching file from S3: {str(e)}")

        return None

    def validate_email_domain(self, email):
        """Validate if the email domain has valid MX records."""
        domain = email.split("@")[-1]
        try:
            dns.resolver.resolve(domain, "MX")
            return True
        except dns.resolver.NoAnswer:
            return False
        except dns.resolver.NXDOMAIN:
            return False
        except Exception as e:
            logger.error(f"DNS lookup failed for domain {domain}: {str(e)}")
            return False

    def post(self, request, *args, **kwargs):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        campaign_id = request.data.get("campaign_id")
        user_id = user.id

        try:
            campaign = Campaign.objects.get(id=campaign_id, user_id=user_id)
        except Campaign.DoesNotExist:
            return Response(
                {"error": "Campaign not found or unauthorized."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            contact_file = ContactFile.objects.filter(
                id=campaign.contact_list.id, user=user
            ).first()
            contacts = Contact.objects.filter(contact_file=contact_file)
            contact_list = [contact.data for contact in contacts]
        except ContactFile.DoesNotExist:
            return Response(
                {"error": "Contact file not found for this campaign."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Error accessing contact list: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not contact_list:
            return Response(
                {"error": "No contacts found for this campaign."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        smtp_server_ids = campaign.smtp_servers.values_list("id", flat=True)
        smtp_servers = SMTPServer.objects.filter(id__in=smtp_server_ids, user=user)
        if not smtp_servers.exists():
            return Response(
                {"error": "No valid SMTP servers found for this campaign."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        can_send, message = profile.can_send_email()
        if not can_send:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        if profile.plan_status == "expired":
            return Response(
                {
                    "error": "Your plan has expired. Please subscribe a plan to continue."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        email_limit = (
            profile.email_limit if profile.email_limit else self.DEFAULT_EMAIL_LIMIT
        )

        if email_limit != 0 and profile.emails_sent >= email_limit:
            if profile.current_plan is None:
                profile.plan_status = "expired"
                profile.save()
                return Response(
                    {
                        "error": "Trial limit exceeded. Please subscribe to a plan to continue."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {
                    "error": "Email limit exceeded. Please upgrade your plan to continue."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        smtp_server_ids = campaign.smtp_servers.values_list("id", flat=True)
        uploaded_file = campaign.uploaded_file
        display_name = campaign.display_name
        delay_seconds = campaign.delay_seconds
        subject = campaign.subject_file

        try:
            file_content = self.get_html_content_from_s3(uploaded_file)
        except Exception as e:
            return Response(
                {"error": f"Error fetching file from S3: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        total_contacts = len(contact_list)
        successful_sends = 0
        failed_sends = 0
        email_statuses = []
        channel_layer = get_channel_layer()
        smtp_servers = SMTPServer.objects.filter(id__in=smtp_server_ids)
        num_smtp_servers = len(smtp_servers)

        for i, recipient in enumerate(contact_list):
            if email_limit != 0 and profile.emails_sent >= email_limit:
                for remaining_recipient in contact_list[i:]:
                    failed_sends += 1
                    status_message = "Failed to send: Email limit exceeded"
                    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                    email_statuses.append(
                        {
                            "email": remaining_recipient.get("Email"),
                            "status": status_message,
                            "timestamp": timestamp,
                        }
                    )
                    async_to_sync(channel_layer.group_send)(
                        f"email_status_{user_id}",
                        {
                            "type": "send_status_update",
                            "email": remaining_recipient.get("Email"),
                            "status": status_message,
                            "timestamp": timestamp,
                        },
                    )
                break

            recipient_email = recipient.get("Email")

            try:
                validated_email = validate_email(recipient_email).email
            except EmailNotValidError as e:
                failed_sends += 1
                status_message = f"Failed to send: {str(e)}"
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                email_statuses.append(
                    {
                        "email": recipient_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    }
                )

                async_to_sync(channel_layer.group_send)(
                    f"email_status_{user_id}",
                    {
                        "type": "send_status_update",
                        "email": recipient_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    },
                )
                continue

            if not self.validate_email_domain(validated_email):
                failed_sends += 1
                status_message = "Failed to send: Invalid domain"
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                email_statuses.append(
                    {
                        "email": validated_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    }
                )
                async_to_sync(channel_layer.group_send)(
                    f"email_status_{user_id}",
                    {
                        "type": "send_status_update",
                        "email": validated_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    },
                )
                continue
            contact = Contact.objects.filter(
                contact_file=contact_file, data__Email=recipient_email
            ).first()

            if contact:
                contact_id = contact.id
            else:
                contact_id = None
            file_id = contact_file.id

            unsubscribe_url = f"{request.scheme}://{request.get_host()}/contact-files/{file_id}/unsubscribe/{contact_id}/"

            context = {
                "firstName": recipient.get("firstName"),
                "lastName": recipient.get("lastName"),
                "companyName": recipient.get("companyName"),
                "display_name": display_name,
                "unsubscribe_url": unsubscribe_url,
            }
            try:
                template = Template(file_content)
                context_data = Context(context)
                email_content = template.render(context_data)
            except Exception as e:
                failed_sends += 1
                status_message = (
                    f"Failed to send: Error formatting email content - {str(e)}"
                )
                timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                email_statuses.append(
                    {
                        "email": validated_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    }
                )
                async_to_sync(channel_layer.group_send)(
                    f"email_status_{user_id}",
                    {
                        "type": "send_status_update",
                        "email": validated_email,
                        "status": status_message,
                        "timestamp": timestamp,
                    },
                )
                continue

            smtp_server = smtp_servers[i % num_smtp_servers]
            email = EmailMessage(
                subject=subject,
                body=email_content,
                from_email=f"{display_name} <{smtp_server.username}>",
                to=[recipient_email],
            )
            email.content_subtype = "html"

            try:
                connection = get_connection(
                    backend="django.core.mail.backends.smtp.EmailBackend",
                    host=smtp_server.host,
                    port=smtp_server.port,
                    username=smtp_server.username,
                    password=smtp_server.password,
                    use_tls=smtp_server.use_tls,
                )
                email.connection = connection
                email.send()
                status_message = "Sent successfully"
                successful_sends += 1
                profile.increment_email_count()
                profile.save()
            except Exception as e:
                status_message = f"Failed to send: {str(e)}"
                failed_sends += 1
                logger.error(f"Error sending email to {recipient_email}: {str(e)}")

            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            email_statuses.append(
                {
                    "email": validated_email,
                    "status": status_message,
                    "timestamp": timestamp,
                    "from_email": smtp_server.username,
                    "smtp_server": smtp_server.host,
                }
            )
            EmailStatusLog.objects.create(
                user=user,
                email=validated_email,
                status=status_message,
                from_email=smtp_server.username,
                smtp_server=smtp_server.host,
            )

            async_to_sync(channel_layer.group_send)(
                f"email_status_{user_id}",
                {
                    "type": "send_status_update",
                    "email": validated_email,
                    "status": status_message,
                    "timestamp": timestamp,
                },
            )

            if delay_seconds > 0:
                time.sleep(delay_seconds)

        return Response(
            {
                "status": "All emails processed",
                "total_emails": total_contacts,
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "email_statuses": email_statuses,
            },
            status=status.HTTP_200_OK,
        )


class EmailStatusAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        total_emails = EmailStatusLog.objects.filter(user=user).count()
        successful_sends = EmailStatusLog.objects.filter(
            user=user, status="Sent successfully"
        ).count()
        failed_sends = EmailStatusLog.objects.filter(
            user=user, status__startswith="Failed"
        ).count()

        analytics_data = {
            "total_emails": total_emails,
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
        }

        return Response(analytics_data, status=status.HTTP_200_OK)


class EmailStatusByDateRangeView(APIView):
    permission_classes = [IsAuthenticated]

    class DateRangeSerializer(serializers.Serializer):
        start_date = serializers.DateField(required=True)
        end_date = serializers.DateField(required=True)

        def validate(self, data):
            start_date = data.get("start_date")
            end_date = data.get("end_date")

            delta = end_date - start_date
            if delta.days > 7:
                raise ValidationError("The date range cannot be more than 7 days.")
            return data

    def get(self, request, *args, **kwargs):
        user = request.user

        serializer = self.DateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        today = timezone.now().date()
        if end_date > today:
            raise ValidationError("End date cannot be in the future.")

        if start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")

        successful_sends = []
        failed_sends = []
        labels = []

        for i in range((end_date - start_date).days + 1):
            day = start_date + timedelta(days=i)
            labels.append(day.strftime("%Y-%m-%d"))

            successful_sends.append(
                EmailStatusLog.objects.filter(
                    user=user, status="Sent successfully", timestamp__date=day
                ).count()
            )

            failed_sends.append(
                EmailStatusLog.objects.filter(
                    user=user, status__startswith="Failed", timestamp__date=day
                ).count()
            )

        analytics_data = {
            "labels": labels,
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
        }

        return Response(analytics_data, status=status.HTTP_200_OK)


# import csv
# from io import StringIO
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from .models import SubjectFile

# class SubjectFileUploadView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         csv_file = request.FILES.get("csv_file")
#         file_name = request.data.get("name")

#         if not csv_file or not file_name:
#             return Response(
#                 {"error": "File name and CSV file are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if not csv_file.name.lower().endswith(".csv"):
#             return Response(
#                 {"error": "Only CSV files are allowed."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if SubjectFile.objects.filter(user=user, name=file_name).exists():
#             return Response(
#                 {"error": f'A file with the name "{file_name}" already exists. Please use a different name.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Read and decode CSV file
#             decoded_file = csv_file.read().decode("utf-8")
#             reader = csv.DictReader(StringIO(decoded_file))

#             csv_data = [row for row in reader if any(row.values())]  # Convert CSV rows to JSON

#             if not csv_data:
#                 return Response(
#                     {"error": "The CSV file is empty or incorrectly formatted."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         except Exception as e:
#             return Response(
#                 {"error": f"Invalid CSV file format: {str(e)}"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Save CSV data in JSON format inside the SubjectFile model
#         subject_file = SubjectFile.objects.create(user=user, name=file_name, data=csv_data)

#         return Response(
#             {
#                 "message": "Subject file uploaded successfully.",
#                 "file_name": file_name,
#                 "total_subjects": len(csv_data),
#                 "uploaded_at": subject_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
#             },
#             status=status.HTTP_201_CREATED
#         )



class SubjectFileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        file = request.FILES.get("csv_file")
        file_name = request.data.get("name")

        if not file:
            return Response(
                {"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not file_name:
            return Response(
                {"error": "File name is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Read CSV file
        try:
            decoded_file = file.read().decode("utf-8")
            reader = csv.DictReader(StringIO(decoded_file))  # Read as dictionary

            if not reader.fieldnames:
                return Response(
                    {"error": "CSV file is missing headers."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            expected_header = "Subject"
            csv_headers = [
                header.strip() for header in reader.fieldnames
            ]  # Normalize headers (trim spaces)

            if expected_header not in csv_headers:
                return Response(
                    {
                        "error": f"Invalid CSV header. Expected header: '{expected_header}', but found: {csv_headers}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract and store rows
            rows = [
                {"id": index + 1, expected_header: row[expected_header]}
                for index, row in enumerate(reader)
                if row.get(expected_header)
            ]

            if not rows:
                return Response(
                    {"error": "CSV file contains no valid data."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": f"Invalid CSV file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save data in JSON format
        subject_file = SubjectFile.objects.create(
            user=user,
            name=file_name,
            uploaded_at=now(),
            data={"data": rows},  # Storing rows as JSON
        )

        return Response(
            {
                "message": "Subject file uploaded successfully.",
                "file_name": file_name,
                "total_rows": len(rows),
                "created_at": subject_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_201_CREATED,
        )



class SubjectFileList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_files = SubjectFile.objects.filter(user=user).values(
            "id", "name", "uploaded_at"
        )

        formatted_data = {
            "subject_file_list": [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "uploaded_at": file["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S"),
                }
                for file in user_files
            ]
        }

        return Response(formatted_data)


class DeleteSubjectFile(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        user = request.user
        try:
            file = SubjectFile.objects.get(id=file_id, user=user)
            file.delete()
            return Response(
                {"message": "File deleted successfully"}, status=status.HTTP_200_OK
            )
        except SubjectFile.DoesNotExist:
            return Response(
                {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
            )


class SubjectFileDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        user = request.user
        try:
            file = SubjectFile.objects.get(id=file_id, user=user)

            response_data = {
                "id": file.id,
                "name": file.name,
                "uploaded_at": file.uploaded_at,
                "data": file.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except SubjectFile.DoesNotExist:
            return Response(
                {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
            ) 
class SubjectFileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        """
        Update an existing subject file with new rows or modify existing ones.
        """
        user = request.user

        try:
            subject_file = SubjectFile.objects.get(id=file_id, user=user)
        except SubjectFile.DoesNotExist:
            return Response(
                {"error": "Subject file not found or you do not have permission to update it."},
                status=status.HTTP_404_NOT_FOUND,
            )

        rows_data = request.data.get("rows")
        if not rows_data:
            return Response(
                {"error": "No rows data provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure subject_file.data is a list
        if not isinstance(subject_file.data, list):
            subject_file.data = []

        existing_rows = {row["id"]: row for row in subject_file.data if "id" in row}
        next_id = max([row["id"] for row in subject_file.data if "id" in row], default=0) + 1
        updated_data = []

        for row in rows_data:
            row_id = row.get("id")
            if row_id in existing_rows:
                existing_rows[row_id].update(row)  # Update the existing row
            else:
                row["id"] = next_id
                next_id += 1
                updated_data.append(row)  # Add new row

        # Save updated data
        subject_file.data = list(existing_rows.values()) + updated_data
        subject_file.save()

        return Response(
            {
                "message": "Subject file updated successfully.",
                "file_id": subject_file.id,
                "file_name": subject_file.name,
                "updated_rows": len(rows_data),
                "total_rows": len(subject_file.data),
                "uploaded_at": subject_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
                "rows": subject_file.data, 
            },
            status=status.HTTP_200_OK,
        )


# class SubjectFileUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, file_id):
#         """
#         Update or insert rows in the SubjectFile data.
#         - If `id` is given, update the existing row.
#         - If `id` is not given, add a new row with a sequential unique ID.
#         """
#         user = request.user

#         try:
#             subject_file = SubjectFile.objects.get(id=file_id, user=user)
#         except SubjectFile.DoesNotExist:
#             return Response(
#                 {
#                     "error": "Subject file not found or you do not have permission to update it."
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         subject_data = request.data.get("rows")  # Expecting a list of dicts

#         if not isinstance(subject_data, list):
#             return Response(
#                 {"error": "Invalid data format. Expected a list of dictionaries."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         updated_rows = []
#         new_rows = []
#         total_updated = 0
#         total_new = 0

#         # Extract existing rows into a dictionary {id: row_data}
#         existing_data = {
#             row["id"]: row
#             for row in subject_file.data
#             if isinstance(row, dict) and "id" in row
#         }

#         # Determine the next row ID based on the total count of existing rows
#         next_id = max(existing_data.keys(), default=0) + 1

#         with transaction.atomic():
#             for row in subject_data:
#                 if not isinstance(row, dict):  # Ensure valid data format
#                     continue

#                 row_id = row.get("id")
#                 row_subject = row.get("Subject")  # Extract "Subject" field

#                 if row_id and row_id in existing_data:
#                     # Update existing row
#                     existing_data[row_id]["Subject"] = row_subject
#                     updated_rows.append(existing_data[row_id])
#                     total_updated += 1
#                 else:
#                     # Insert new row with a sequential ID
#                     new_row = {"id": next_id, "Subject": row_subject}
#                     subject_file.data.append(new_row)
#                     new_rows.append(new_row)
#                     total_new += 1
#                     next_id += 1  # Increment for the next new row

#             # Save changes to the database
#             subject_file.save()

#         return Response(
#             {
#                 "message": "Rows updated and new rows added successfully.",
#                 "file_id": subject_file.id,
#                 "file_name": subject_file.name,
#                 "total_rows_updated": total_updated,
#                 "total_new_rows": total_new,
#                 "created_at": subject_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
#                 "rows": subject_file.data,  # Returning updated row data
#             },
#             status=status.HTTP_200_OK,
#         )


class SubjectFileRowDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id, row_id):
        """
        Delete a specific row from the SubjectFile by row ID.
        """
        user = request.user

        try:
            subject_file = SubjectFile.objects.get(id=file_id, user=user)
        except SubjectFile.DoesNotExist:
            return Response(
                {
                    "error": "Subject file not found or you do not have permission to delete it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        existing_rows = subject_file.data  
        row_to_delete = None

        updated_rows = []
        with transaction.atomic():
            for row in existing_rows:
                if isinstance(row, dict) and row.get("id") == row_id:
                    row_to_delete = row
                else:
                    updated_rows.append(row)

            if not row_to_delete:
                return Response(
                    {"error": f"Row with ID {row_id} not found in this file."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            subject_file.data = updated_rows
            subject_file.save()

        return Response(
            {
                "message": f"Row with ID {row_id} deleted successfully.",
                "file_id": subject_file.id,
                "file_name": subject_file.name,
                "total_remaining_rows": len(updated_rows),
                "created_at": subject_file.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
                "rows": updated_rows,  
            },
            status=status.HTTP_200_OK,
        )
