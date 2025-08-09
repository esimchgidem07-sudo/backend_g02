from django.urls import path
from .views import *

urlpatterns = [
    path('category/', CategoryView.as_view(), name='category'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category'),
    path('menu/<int:pk>/', MenuDetailView.as_view(), name='menu_detail'),
    path('contact/', ContactView.as_view(), name='contact'),

]