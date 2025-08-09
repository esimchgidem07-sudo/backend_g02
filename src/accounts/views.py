from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Authentication"],
        summary="User login",
        description="Authenticate user with email and password to get JWT tokens",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email", "description": "User email"},
                    "password": {"type": "string", "description": "User password"},
                },
                "required": ["email", "password"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Access token"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "username": {"type": "string"},
                        }
                    }
                }
            },
            400: "Bad Request",
            401: "Invalid credentials"
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "username"
                    }
                }
            )
        ]
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Please provide both email and password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(email=email, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response({
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                }
            })
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,  # True для продакшена
                samesite="Lax",
                max_age=60*60*24
            )
            return response
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Authentication"],
        summary="User registration",
        description="Register a new user with email, username and password",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email", "description": "User email"},
                    "username": {"type": "string", "description": "Username"},
                    "password": {"type": "string", "description": "User password"},
                    "password_confirm": {"type": "string", "description": "Password confirmation"},
                },
                "required": ["email", "username", "password", "password_confirm"]
            }
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Access token"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "username": {"type": "string"},
                        }
                    }
                }
            },
            400: "Bad Request - Validation error or passwords don't match"
        }
    )
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        
        if not all([email, username, password, password_confirm]):
            return Response(
                {'error': 'Please provide all required fields'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if password != password_confirm:
            return Response(
                {'error': 'Passwords do not match'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'User with this username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password
            )
            refresh = RefreshToken.for_user(user)
            response = Response({
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                }
            }, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,  # True для продакшена
                samesite="Lax",
                max_age=60*60*24
            )
            return response
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    @extend_schema(
        tags=["Authentication"],
        summary="User logout",
        description="Logout user by blacklisting the refresh token and removing the refresh_token cookie",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Refresh token to blacklist"},
                },
                "required": ["refresh"]
            }
        },
        responses={
            200: "Successfully logged out",
            400: "Bad Request - Invalid token"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({'message': 'Successfully logged out'})
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Получаем refresh из cookie, если не передан явно
        refresh = request.data.get("refresh") or request.COOKIES.get("refresh_token")
        if not refresh:
            return Response({'error': 'No refresh token provided'}, status=400)
        # Подменяем request.data для сериализатора
        data = request.data.copy()
        data["refresh"] = refresh
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        return Response(serializer.validated_data)
    
# Create your views here.
