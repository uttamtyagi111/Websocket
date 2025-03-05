from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .forms import OTPVerificationForm
from django.http import JsonResponse
from .forms import EmailLoginForm
from functools import cache
import secrets
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib import messages
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .forms import (
    CreateUserForm,
    EmailLoginForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
)
from .forms import OTPVerificationForm
from django.core.mail import send_mail
from django.conf import settings
from .models import DeviceVerifyOTP, LoginOTP
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .forms import PasswordResetRequestForm
from .utils import send_password_reset_email, send_logout_otp_email
from subscriptions.models import UserProfile, UserDevice
from django.shortcuts import render
from .utils import generate_otp, send_otp_email, send_welcome_email
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login as django_login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from django.core.cache import cache


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view."})


class CustomTokenRefreshView(TokenRefreshView):
    pass


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_logged_in_devices(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return Response({"error": "User is not authenticated"}, status=401)

    user = request.user
    user_devices = UserDevice.objects.filter(user=user)
    device_data = []
    for device in user_devices:
        device_data.append(
            {
                "device_id": device.id,
                "device_name": device.device_name,
                "system_info": device.system_info,
            }
        )
    return Response(
        {
            "logged_in_devices": device_data,
            "message": "Logged-in devices fetched successfully",
        }
    )


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def loginPage(request):
#     form = EmailLoginForm(data=request.data)

#     if not form.is_valid():
#         return Response({
#             'form_valid': form.is_valid(),
#             'errors': form.errors
#         }, status=400)

#     email = form.cleaned_data['email']
#     password = form.cleaned_data['password']
#     user = authenticate(request, email=email, password=password)

#     if not user:
#         return Response({'message': 'Email or password is incorrect.'}, status=400)

#     if not user.is_active:
#         return Response({'message': 'Account is inactive.'}, status=400)

#     try:
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         return Response({'message': 'User profile not found.'}, status=400)

#     plan_name = getattr(user_profile.current_plan, 'name', None)

#     if plan_name:
#         print(f"Plan Name: {plan_name}")
#     else:
#         print("No plan associated with this user.")

#     if not plan_name or plan_name.lower() == "basic":
#         device_limit = 1
#     elif plan_name.lower() == "standard":
#         device_limit = 3
#     elif plan_name.lower() == "premium":
#         device_limit = 5
#     elif plan_name.lower() == "elite":
#         device_limit = 15
#     else:
#         return Response({'message': 'Invalid plan name.'}, status=400)

#     system_info = request.data.get('system_info')
#     if not system_info:
#         return Response({'message': 'System info is required.'}, status=400)

#     if not check_device_limit(user_profile, system_info, device_limit):
#         return Response({
#             'message': f'Device limit exceeded. You can only log in on {device_limit} device(s) based on your {plan_name} plan. Please log out from other devices to log in.',
#             'logged_in_devices': logged_in_devices(user_profile)
#         }, status=200)

#     if user_profile.is_2fa_enabled:
#         Login.objects.filter(user=user, expires_at__lt= now()).delete()
#         otp_instance = LoginOTP.objects.create(
#             user=user,
#             otp=generate_otp(),
#             expires_at=now() + timedelta(minutes=5)  # OTP expires in 5 minutes
#         )
#         send_otp_email(user.email, user.username, otp_instance.otp)

#         return Response({
#             'message': 'OTP sent to your email. Please verify to complete login.',
#             'redirect': 'verify_otp',  # Redirect to OTP verification page
#             'user_id': user.id,
#         }, status=200)
#     else:
#         # If 2FA is disabled, generate access and refresh tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)

#         # Handle device login (saving device info and tokens)
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         device_count = existing_devices.count()

#         device_name = f"device{device_count + 1}"
#         user_device = UserDevice.objects.create(
#             user=user,
#             device_name=device_name,
#             system_info=system_info,
#             token=refresh_token
#         )

#         return Response({
#             'user_id': user.id,
#             'access': access_token,
#             'refresh': refresh_token,
#             'system_info': system_info,
#             "device_id": user_device.id,
#             'redirect': 'home',  # Redirect to home after successful login
#             'message': 'Login successful'
#         })


@api_view(["POST"])
@permission_classes([AllowAny])
def loginPage(request):
    form = EmailLoginForm(data=request.data)

    if not form.is_valid():
        return Response(
            {"form_valid": form.is_valid(), "errors": form.errors}, status=400
        )

    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]
    user = authenticate(request, email=email, password=password)

    if not user:
        return Response({"message": "Email or password is incorrect."}, status=400)

    if not user.is_active:
        return Response({"message": "Account is inactive."}, status=400)

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({"message": "User profile not found."}, status=400)

    # Plan aur device limit database se fetch karein
    current_plan = user_profile.current_plan
    plan_name = current_plan.name if current_plan else "Trial"
    device_limit = current_plan.device_limit if current_plan else 1
    print(f"Plan Name: {plan_name}, Device Limit: {device_limit}")

    system_info = request.data.get("system_info")
    if not system_info:
        return Response({"message": "System info is required."}, status=400)

    if not check_device_limit(user_profile, system_info, device_limit):
        return Response(
            {
                "message": f"Device limit exceeded. You can only log in on {device_limit} device(s) based on your {plan_name} plan. Please log out from other devices to log in.",
                "logged_in_devices": logged_in_devices(user_profile),
            },
            status=200,
        )

    if user_profile.is_2fa_enabled:
        LoginOTP.objects.filter(user=user, expires_at__lt=now()).delete()
        otp_instance = LoginOTP.objects.create(
            user=user, otp=generate_otp(), expires_at=now() + timedelta(minutes=5)
        )
        send_otp_email(user.email, user.username, otp_instance.otp)

        return Response(
            {
                "message": "OTP sent to your email. Please verify to complete login.",
                "redirect": "verify_otp",
                "user_id": user.id,
            },
            status=200,
        )
    else:
        # If 2FA is disabled, generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        existing_devices = UserDevice.objects.filter(user=user_profile.user)
        device_count = existing_devices.count()

        device_name = f"device{device_count + 1}"
        user_device = UserDevice.objects.create(
            user=user,
            device_name=device_name,
            system_info=system_info,
            token=refresh_token,
        )

        return Response(
            {
                "user_id": user.id,
                "access": access_token,
                "refresh": refresh_token,
                "system_info": system_info,
                "device_id": user_device.id,
                "redirect": "home",
                "message": "Login successful",
            }
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verifyLoginOTP(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    system_info = request.data.get("system_info")

    if not email or not otp:
        return Response({"message": "Email and OTP are required."}, status=400)

    if not system_info:
        return Response({"message": "System info is required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=400)

    try:
        otp_instance = LoginOTP.objects.filter(user=user).latest("created_at")

    except LoginOTP.DoesNotExist:
        return Response({"message": "Invalid OTP or OTP has expired."}, status=400)

    if otp_instance.expires_at < now():
        return Response({"message": "OTP has expired."}, status=400)

    if otp != otp_instance.otp:
        return Response({"message": "Invalid OTP."}, status=400)

    # LoginOTP.objects.filter(user=user).delete()  # Delete old OTPs
    # otp_instance = LoginOTP.objects.create(user=user, otp=otp)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    otp_instance.delete()

    existing_devices = UserDevice.objects.filter(user=user)
    device_count = existing_devices.count()
    device_name = f"device{device_count + 1}"

    user_device = UserDevice.objects.create(
        user=user, device_name=device_name, system_info=system_info, token=refresh_token
    )

    return Response(
        {
            "user_id": user.id,
            "access": access_token,
            "refresh": refresh_token,
            "system_info": system_info,
            "device_id": user_device.id,
            "redirect": "home",
            "message": "OTP verified successfully. Login successful.",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def request_logout_otp(request):
    device_id = request.data.get("device_id")

    if not device_id:
        return Response({"error": "Device ID is required"}, status=400)

    try:
        device = UserDevice.objects.get(id=device_id)
        user = device.user

        otp = generate_otp()
        expires_at = now() + timedelta(minutes=10)

        DeviceVerifyOTP.objects.filter(user=user).delete()

        DeviceVerifyOTP.objects.create(
            user=user, device_id=device_id, otp=otp, expires_at=expires_at
        )

        send_logout_otp_email(user.email, user.username, otp)

        return Response(
            {"message": "OTP sent to your email. Please verify before logging out."},
            status=200,
        )

    except UserDevice.DoesNotExist:
        return Response({"error": "Invalid Device ID. Device not found."}, status=400)


class LogoutDeviceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        device_id = request.data.get("device_id")
        system_info = request.data.get("system_info")
        otp = request.data.get("otp")

        if not device_id or not system_info or not otp:
            return Response(
                {"error": "Device ID, OTP, and system info are required"},
                status=HTTP_400_BAD_REQUEST,
            )

        device = get_object_or_404(UserDevice, id=device_id)
        user = device.user

        try:
            otp_record = DeviceVerifyOTP.objects.get(user=user, otp=otp)

            if otp_record.is_expired():
                otp_record.delete()
                return Response(
                    {"error": "OTP expired. Request a new one."},
                    status=HTTP_400_BAD_REQUEST,
                )

            otp_record.delete()
        except DeviceVerifyOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP. Please try again."}, status=HTTP_400_BAD_REQUEST
            )

        try:
            old_refresh_token = device.token

            if not old_refresh_token:
                return Response(
                    {"error": "No refresh token found for this device"},
                    status=HTTP_400_BAD_REQUEST,
                )

            try:
                old_token = RefreshToken(old_refresh_token)
                old_token.blacklist()
            except Exception as e:
                return Response(
                    {"error": f"Failed to blacklist old token: {str(e)}"},
                    status=HTTP_400_BAD_REQUEST,
                )
            device.delete()
            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)
                



            return Response(
                {
                    "success": f"Device {device.device_name} logged out successfully.",
                    "user_id": user.id,
                    "device_id": device_id,
                    "access_token": new_access_token,
                    "refresh_token": str(new_refresh_token),
                    "message": "Device has been logged out and removed.",
                },
                status=HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


def check_device_limit(user_profile, system_info, device_limit):
    """
    Checks if the user has exceeded the allowed device limit based on their plan.
    """
    if user_profile.current_plan:
        allowed_limit = user_profile.current_plan.device_limit
    else:
        allowed_limit = 1

    existing_devices_count = UserDevice.objects.filter(user=user_profile.user).count()

    return existing_devices_count < allowed_limit


# def check_device_limit(user_profile, system_info,device_limit):
#     """
#     Checks if the user has exceeded the allowed device limit.
#     """

#     if user_profile.plan_name == None:
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         if existing_devices.count() >= 1:
#             return False
#     elif user_profile.plan_name == 'Basic':
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         if existing_devices.count() >= 1:
#             return False
#     elif user_profile.plan_name == 'Standard':
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         if existing_devices.count() >= 3:
#             return False
#     elif user_profile.plan_name == 'Premium':
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         if existing_devices.count() >= 5:
#             return False
#     elif user_profile.plan_name == 'Elite':
#         existing_devices = UserDevice.objects.filter(user=user_profile.user)
#         if existing_devices.count() >= 15:
#             return False
#     return True


def logged_in_devices(user_profile):
    """
    Returns the list of devices the user is logged in on.
    """
    devices = UserDevice.objects.filter(user=user_profile.user)
    devices_info = [
        {
            "device_name": device.device_name,
            "device_id": device.id,
            "system_info": device.system_info,
        }
        for device in devices
    ]
    return devices_info

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        device_id = request.data.get("device_id")
        user = request.user

        if not device_id:
            logger.warning(f"User {user.email} attempted logout without a device ID.")
            return Response({"message": "Device ID is required."}, status=400)

        # Prevent 404 exception by using filter().first()
        device = UserDevice.objects.filter(id=device_id).first()
        if not device:
            logger.warning(f"User {user.email} attempted to logout, but device {device_id} was not found.")
            return Response({"message": "Device not found."}, status=404)

        if device.user != user:
            logger.warning(f"User {user.email} tried to remove device {device_id} without permission.")
            return Response({"message": "You do not have permission to remove this device."}, status=403)

        refresh_token = device.token
        if not refresh_token:
            logger.warning(f"User {user.email} has no refresh token for device {device_id}.")
            return Response({"message": "No refresh token found for this device."}, status=400)

        # Blacklist token
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User {user.email} successfully blacklisted token for device {device_id}.")
        except Exception as e:
            logger.error(f"Error blacklisting token for user {user.email}: {str(e)}")
            return Response({"message": f"Error blacklisting token: {str(e)}"}, status=400)

        # Delete the device
        device.delete()
        logger.info(f"User {user.email} logged out and removed device {device_id}.")

        return Response({"message": "Logout successful and device removed."}, status=200)

    except AuthenticationFailed:
        logger.error(f"User {request.user.email} provided an invalid token.")
        return Response({"message": "Invalid token"}, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error during logout for user {request.user.email}: {str(e)}")
        return Response({"message": f"Error: {str(e)}"}, status=500)




# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#     try:
#         device_id = request.data.get("device_id")

#         if not device_id:
#             return Response({"message": "Device ID is required."}, status=400)

#         device = get_object_or_404(UserDevice, id=device_id)

#         if device.user != request.user:
#             return Response(
#                 {"message": "You do not have permission to remove this device."},
#                 status=403,
#             )

#         refresh_token = device.token

#         if not refresh_token:
#             return Response(
#                 {"message": "No refresh token found for this device."}, status=400
#             )

#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#         except Exception as e:
#             return Response(
#                 {"message": f"Error blacklisting token: {str(e)}"}, status=400
#             )

#         device.delete()

#         return Response(
#             {"message": "Logout successful and device removed."}, status=200
#         )

#     except InvalidToken:
#         return Response({"message": "Invalid token"}, status=400)
#     except Exception as e:
#         return Response({"message": f"Error: {str(e)}"}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_blacklisted_token(request):
    """
    This API checks if a given refresh token is blacklisted.
    """
    refresh_token = request.data.get("refresh_token")
    if not refresh_token:
        return Response({"message": "Refresh token is required."}, status=400)

    try:
        token = RefreshToken(refresh_token)
        try:
            BlacklistedToken.objects.get(token__jti=token["jti"])
            return Response({"message": "The token is blacklisted."}, status=200)
        except ObjectDoesNotExist:
            return Response({"message": "The token is not blacklisted."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home(request):
    user = request.user
    data = {
        "message": "Welcome to the home page!",
        "current_year": 2025,
        "user": {"username": user.username, "email": user.email},
    }
    return JsonResponse(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def registerPage(request):
    if request.user.is_authenticated:
        return Response({"redirect": "home"}, status=status.HTTP_302_FOUND)

    form = CreateUserForm(data=request.data)

    if form.is_valid():
        email = form.cleaned_data.get("email")
        username = form.cleaned_data.get("username")

        if User.objects.filter(email=email).exists():
            return Response(
                {
                    "message": "Email is already registered. Please log in or use a different email."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = generate_otp()
        cache.set(f"otp_{email}", otp, timeout=600)
        send_otp_email(email, otp, username)

        user_data = {
            "username": username,
            "email": email,
            "password": form.cleaned_data.get("password"),
        }
        cache.set(f"register_data_{email}", user_data, timeout=600)

        return Response(
            {
                "message": "OTP sent to your email. Please verify to complete registration.",
                "email": email,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"form_valid": form.is_valid(), "errors": form.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    form = OTPVerificationForm(data=request.data)

    if form.is_valid():
        otp_input = form.cleaned_data.get("otp")
        otp_stored = cache.get(f'otp_{request.data.get("email")}')

        if otp_input == otp_stored:
            user_data = cache.get(f'register_data_{request.data.get("email")}')

            if user_data:
                user, created = User.objects.get_or_create(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                )
                if created:
                    user.is_active = True
                    user.set_password(user_data["password"])
                    user.save()
                    send_welcome_email(user)

                cache.delete(f'otp_{request.data.get("email")}')
                cache.delete(f'register_data_{request.data.get("email")}')

                return Response(
                    {"message": "Email verified and account created successfully."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "User data not found. Please register again."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {"form_valid": form.is_valid(), "errors": form.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


def user_list(request):
    users = User.objects.all()
    return render(request, "authentication/user_list.html", {"users": users})


import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    form = PasswordResetRequestForm(data=request.data)

    if form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            send_password_reset_email(user, settings.BASE_URL)
            return Response(
                {"message": "Password reset email sent."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"errors": {"email": ["No user found with this email address."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {"form_valid": form.is_valid(), "errors": form.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            messages.error(request, "Invalid or expired reset link.")
            return Response(
                {"redirect": "request_password_reset"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid or expired reset link.")
        return Response(
            {"redirect": "request_password_reset"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password has been reset successfully.")
            return Response({"redirect": "login"}, status=status.HTTP_200_OK)
    else:
        form = SetNewPasswordForm()

    return Response({"form": form.as_p()}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.is_2fa_enabled:
            return Response(
                {"message": "2FA is already enabled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_profile.is_2fa_enabled = True
        user_profile.save()

        return Response(
            {"message": "2FA has been enabled successfully."}, status=status.HTTP_200_OK
        )
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        if not user_profile.is_2fa_enabled:
            return Response(
                {"message": "2FA is already disabled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_profile.is_2fa_enabled = False
        user_profile.save()

        return Response(
            {"message": "2FA has been disabled successfully."},
            status=status.HTTP_200_OK,
        )
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)

        if user_profile.is_2fa_enabled:
            return Response({"2fa_status": "enabled"}, status=status.HTTP_200_OK)
        else:
            return Response({"2fa_status": "disabled"}, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .models import Enquiry
from .serializers import EnquirySerializer
from django.conf import settings

class EnquiryView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = EnquirySerializer(data=request.data)
        
        if serializer.is_valid():
            enquiry = serializer.save()
            
            # Send email to admin
            admin_email_subject = f"New Enquiry from {enquiry.name}"
            admin_email_body = f"""
            Name: {enquiry.name}
            Phone: {enquiry.phone}
            Email: {enquiry.email}
            Subject: {enquiry.subject}
            Description: {enquiry.description}
            """
            send_mail(
                admin_email_subject,
                admin_email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],  # Replace with your email
                fail_silently=False,
            )

            # Send confirmation email to user
            user_email_subject = "Enquiry Received"
            user_email_body = f"Dear {enquiry.name},\n\nThank you for reaching out! We have received your enquiry and will get back to you soon.\n\nBest Regards,\nYour Company"
            
            send_mail(
                user_email_subject,
                user_email_body,
                settings.DEFAULT_FROM_EMAIL,
                [enquiry.email],
                fail_silently=False,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
