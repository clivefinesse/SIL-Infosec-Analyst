from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def standard_response(status=True, message="", data=None, status_code=status.HTTP_200_OK):
    """Standardized API response format"""
    return Response({
        "status": status,
        "message": message,
        "data": data or {}
    }, status=status_code)

class UserCreateView(generics.CreateAPIView):
    """
    Register a new user and send verification email
    Returns user data and tokens if registration succeeds
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.send_verification_email()
        
        refresh = RefreshToken.for_user(user)
        
        return standard_response(
            status=True,
            message="Registration successful. Verification email sent.",
            data={
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            },
            status_code=status.HTTP_201_CREATED
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Authenticate user and return JWT tokens
    Includes user data in the response
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data['username'])
            response.data = {
                "status": True,
                "message": "Login successful",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "email_verified": user.email_verified,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    },
                    "tokens": response.data
                }
            }
        return response

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update authenticated user's profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return standard_response(
            status=True,
            message="Profile retrieved successfully",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return standard_response(
            status=True,
            message="Profile updated successfully",
            data=serializer.data
        )

class PasswordResetView(generics.GenericAPIView):
    """
    Initiate password reset process
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return standard_response(
            status=True,
            message="If this email exists in our system, you'll receive a password reset link",
            status_code=status.HTTP_200_OK
        )

class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Complete password reset process
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate new tokens after password reset
        refresh = RefreshToken.for_user(user)
        
        return standard_response(
            status=True,
            message="Password reset successfully",
            data={
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            },
            status_code=status.HTTP_200_OK
        )

class EmailVerificationView(generics.GenericAPIView):
    """
    Verify user's email via token
    Redirects to frontend with verification status
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        uidb64 = request.GET.get('uidb64')
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return redirect(
                f'{settings.FRONTEND_URL}/login?'
                f'verified=true&'
                f'refresh={str(refresh)}&'
                f'access={str(refresh.access_token)}'
            )
        
        return redirect(
            f'{settings.FRONTEND_URL}/error?'
            f'message=Invalid+verification+link'
        )