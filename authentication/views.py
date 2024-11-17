from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import ValidationError
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]  # No authentication required for registration

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: {"type": "object", "properties": {"token": {"type": "string"}}},
            400: {"description": "Validation errors"},
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]  # No authentication required for login

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {"type": "object", "properties": {"token": {"type": "string"}}},
            400: {"description": "Invalid credentials"},
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # User is authenticated using the serializer
            user = serializer.validated_data['user']  # 'user' will be returned after validation

            if user and user.is_active:
                # Generate and return a token for the authenticated user
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)

            raise AuthenticationFailed("Invalid credentials")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Authentication required for logout

    @extend_schema(
        request=None,
        responses={200: {"description": "Logged out successfully"}},
    )
    def post(self, request):
        request.auth.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]  # No authentication required for password reset

    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            200: {"description": "Password reset email sent."},
            400: {"description": "Validation errors"},
        },
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['email']
            serializer.send_password_reset_email(user)
            return Response(
                {"message": "Password reset email sent."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]  # No authentication required for password reset

    def post(self, request, token):
        try:
            # Verify the token and extract user
            user = self.verify_token(token)
            if user:
                serializer = PasswordResetConfirmSerializer(data=request.data)
                if serializer.is_valid():
                    new_password = serializer.validated_data['password']
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def verify_token(self, token):
        try:
            # Extract user from the token
            for user in User.objects.all():
                if default_token_generator.check_token(user, token):
                    return user
            return None
        except Exception:
            raise ValidationError("Invalid or expired token.")