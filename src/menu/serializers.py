from rest_framework import serializers
from .models import Category, Menu, Contact

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class MenuAllSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Menu
        fields = [ 'id', 'category', 'name', 'desc','img','price' ]

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"