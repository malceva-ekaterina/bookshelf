from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('singup/', SingUpView.as_view(), name='sing_up'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<username>', UserProfileView.as_view(), name='user_profile'),
    path('profile/<username>/follow/', follow, name='follow'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]