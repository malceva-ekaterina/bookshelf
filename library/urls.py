from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('', BookListView.as_view(), name='books'),
    path('books/new/', BookCreateView.as_view(), name='book_create'),
    path('books/<pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/<pk>/edit', BookUpdateView.as_view(), name='book_edit'),
    path('books/<pk>/delete', BookDeleteView.as_view(), name='book_delete'),
    path('authors/new/', AuthorCreateView.as_view(), name='author_create'),
    path('genre/new/', GenreCreateView.as_view(), name='genre_create'),
    path('books/<int:b_pk>/review/new/', create_review, name='review_create'),
    path('books/<int:b_pk>/review/edit/', review_update, name='review_edit'),
    path('books/<int:pk>/comment/new/', create_comment, name='comment_create'),
]