from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('book/<int:pk>', book_like, name='book_like'),
    path('book/<int:pk>/comment/<int:c_pk>/', comment_like, name='comment_like'),
    path('book/<int:pk>/review/<int:r_pk>/', review_like, name='review_like'),
]