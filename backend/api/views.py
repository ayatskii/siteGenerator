from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Token
from .serializers import UserSerializer, TokenSerializer
from .permissions import IsAdmin
from django.conf import settings
from datetime import datetime, timedelta
import hashlib
import uuid
from django.utils import timezone

SALT = "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
URL = "http://localhost:3000"


def mail_template(content, button_url, button_text):
    return f"""<!DOCTYPE html>
            <html>
            <body style="text-align: center; font-family: "Verdana", serif; color: #000;">
                <div style="max-width: 600px; margin: 10px; background-color: #fafafa; padding: 25px; border-radius: 20px;">
                <p style="text-align: left;">{content}</p>
                <a href="{button_url}" target="_blank">
                    <button style="background-color: #444394; border: 0; width: 200px; height: 30px; border-radius: 6px; color: #fff;">{button_text}</button>
                </a>
                <p style="text-align: left;">
                    If you are unable to click the above button, copy paste the below URL into your address bar
                </p>
                <a href="{button_url}" target="_blank">
                    <p style="margin: 0px; text-align: left; font-size: 10px; text-decoration: none;">{button_url}</p>
                </a>
                </div>
            </body>
            </html>"""

class ResetPasswordView(APIView):
    def post(self, request, format=None):
        user_id = request.data["id"]
        token = request.data["token"]
        password = request.data["password"]

        token_obj = Token.objects.filter(
            user_id=user_id).order_by("-created_at")[0]
        if token_obj.expires_at < timezone.now():
            return Response(
                {
                    "success": False,
                    "message": "Password Reset Link has expired!",
                },
                status=status.HTTP_200_OK,
            )
        elif token_obj is None or token != token_obj.token or token_obj.is_used:
            return Response(
                {
                    "success": False,
                    "message": "Reset Password link is invalid!",
                },
                status=status.HTTP_200_OK,
            )
        else:
            token_obj.is_used = True
            hashed_password = make_password(password=password, salt=SALT)
            ret_code = User.objects.filter(
                id=user_id).update(password=hashed_password)
            if ret_code:
                token_obj.save()
                return Response(
                    {
                        "success": True,
                        "message": "Your password reset was successfully!",
                    },
                    status=status.HTTP_200_OK,
                )


class ForgotPasswordView(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        user = User.objects.get(email=email)
        created_at = timezone.now()
        expires_at = timezone.now() + timezone.timedelta(1)
        salt = uuid.uuid4().hex
        token = hashlib.sha512(
            (str(user.id) + user.password + created_at.isoformat() + salt).encode(
                "utf-8"
            )
        ).hexdigest()
        token_obj = {
            "token": token,
            "created_at": created_at,
            "expires_at": expires_at,
            "user_id": user.id,
        }
        serializer = TokenSerializer(data=token_obj)
        if serializer.is_valid():
            serializer.save()
            subject = "Forgot Password Link"
            content = mail_template(
                "We have received a request to reset your password. Please reset your password using the link below.",
                f"{URL}/resetPassword?id={user.id}&token={token}",
                "Reset Password",
            )
            send_mail(
                subject=subject,
                message=content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=content,
            )
            return Response(
                {
                    "success": True,
                    "message": "A password reset link has been sent to your email.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            error_msg = ""
            for key in serializer.errors:
                error_msg += serializer.errors[key][0]
            return Response(
                {
                    "success": False,
                    "message": error_msg,
                },
                status=status.HTTP_200_OK,
            )


class RegistrationView(APIView):
    def post(self, request, format=None):
        # Create a mutable copy of request.data
        data = request.data.copy()
        data["password"] = make_password(
            password=data["password"], salt=SALT
        )
        # Ensure role is always USER, regardless of input
        data["role"] = "USER"
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save(role="USER")
            return Response(
                {"success": True, "message": "You are now registered on our website!"},
                status=status.HTTP_201_CREATED,
            )
        else:
            error_msg = ""
            for key in serializer.errors:
                error_msg += serializer.errors[key][0]
            return Response(
                {"success": False, "message": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    def post(self, request, format=None):
        try:
            email = request.data["email"]
            password = request.data["password"]
            hashed_password = make_password(password=password, salt=SALT)
            user = User.objects.get(email=email)
            if user is None or user.password != hashed_password:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid Login Credentials!",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            else:
                # Generate JWT tokens
                refresh = RefreshToken()
                refresh['user_id'] = user.id
                refresh['email'] = user.email
                refresh['role'] = user.role
                
                access_token = refresh.access_token
                access_token['user_id'] = user.id
                access_token['email'] = user.email
                access_token['role'] = user.role
                
                return Response(
                    {
                        "success": True,
                        "message": "You are now logged in!",
                        "access": str(access_token),
                        "refresh": str(refresh),
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "role": user.role,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid Login Credentials!",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class PromoteUserView(APIView):
    """
    Endpoint to promote a user to ADMIN role.
    Only accessible by users with ADMIN role.
    """
    permission_classes = [IsAdmin]

    def post(self, request, format=None):
        """
        Promote a user to ADMIN role.
        Requires: {"user_id": <user_id>} in request body
        """
        try:
            user_id = request.data.get("user_id")
            if not user_id:
                return Response(
                    {
                        "success": False,
                        "message": "user_id is required",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user_to_promote = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "User not found",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if user is already an admin
            if user_to_promote.role == "ADMIN":
                return Response(
                    {
                        "success": False,
                        "message": "User is already an admin",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Promote user to admin
            user_to_promote.role = "ADMIN"
            user_to_promote.save()

            return Response(
                {
                    "success": True,
                    "message": f"User {user_to_promote.email} has been promoted to admin",
                    "user": {
                        "id": user_to_promote.id,
                        "name": user_to_promote.name,
                        "email": user_to_promote.email,
                        "role": user_to_promote.role,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )