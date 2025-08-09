from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated  # Add this import
from .models import Category, Menu
from .serializers import CategorySerializer, MenuSerializer, MenuAllSerializer, ContactSerializer
from drf_spectacular.utils import extend_schema


class CategoryView(APIView):
    permission_classes = [AllowAny]  # Allow public access
    @extend_schema(
        summary="Get all categories",
        description="Get all categories",
        responses={
            200: CategorySerializer(many=True),
            401: "Unauthorized",
            },
        tags=['Categories']
    )    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CategoryDetailView(APIView):
    permission_classes = [AllowAny]  # Allow public access
    @extend_schema(
        summary="Get category by ID",
        description="Get a specific category by its ID",
        responses={
            200: CategorySerializer(many=True),
            404: "Category not found",
            401: "Not Found",
            },
        tags=['Categories']
    )
    def get(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        menus = category.menu_set.all().order_by('-order')
        if menus.count() == 0:
            return Response({"message": "No menus found "}, status=status.HTTP_404_NOT_FOUND)
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # category = Category.objects.get(id=pk)
        # menus = category.menu_set.all()
        # serializer = MenuAllSerializer(menus, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class MenuDetailView(APIView):
    permission_classes = [AllowAny]  # Allow public access
    @extend_schema(
        summary="Get a menu by id",
        description="Get a menu by id",
        responses={
            200: MenuSerializer,
            401: "Unauthorized",
            404: "Not Found",
        },
        tags=['Menu']
    )
    def get(self, request, pk):
        menu = Menu.objects.filter(category=pk).order_by('-order')
        print(menu)
        serializer = MenuSerializer(menu, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ContactView(APIView):
    permission_classes = [AllowAny]  # Allow public access
    @extend_schema(
        summary="Submit contact form",
        description="Submit a contact form",
        request={
              "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User name"},
                    "email": {"type": "string", "format": "email", "description": "User email"},
                    "subject": {"type": "string", "description": "Subject of the message"},
                    "message": {"type": "string", "description": "Message "},
                },
                "required": ["name", "email", "subject", "message"]
            }
        },
        responses={
            201: ContactSerializer,
            400: "Bad Request", 
        },
        tags=['Contact']
    )
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# CRUD
# Create
# Read
# Update
# Delete

# GET  -> Read
# POST -> Create
# PUT  -> Update
# PATCH -> Update
# DELETE -> Delete