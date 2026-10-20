from PIL import Image
import os
import uuid
from pathlib import Path
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg

from likes.models import Like
# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
        
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    
    likes = GenericRelation(Like, related_query_name='comment')
    
    def __str__(self):
        return f'User {self.user.username} wrote {self.text}'
    
   
    

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.slug
    
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sur_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

def unique_book_path(instance, filename):
    ext = Path(filename).suffix
    new_filename = f'book_{instance.title}_cover{ext}'
    
    return Path('covers') / new_filename

class Book(models.Model):
    title = models.CharField()
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to=unique_book_path, default='covers/default.png', blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    author = models.ManyToManyField(Author)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='books') 
    created_at = models.DateTimeField(auto_now_add=True)
    
    likes = GenericRelation(Like, related_query_name='book')
    comments = GenericRelation(Comment, related_query_name='book')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
    
            if self.cover:
                img = Image.open(self.cover.path)
    
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(self.cover.path)
    @property
    def get_avg_rating(self):
        result = self.reviews.aggregate(Avg('rating'))
        return result['rating__avg']
    
class Rating(models.IntegerChoices):
        ONE = 1, '⭐'
        TWO = 2, '⭐⭐'
        THREE = 3, '⭐⭐⭐'
        FOUR = 4, '⭐⭐⭐⭐'
        FIVE = 5, '⭐⭐⭐⭐⭐'
        
class Review(models.Model):
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(choices=Rating.choices, default=Rating.FIVE)
    text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    likes = GenericRelation(Like, related_query_name='review')
    
    class Meta():
        unique_together = ('user', 'book')
    
    def __str__(self):
        return f'User:{self.user.username} left a review on {self.book.title}'
    
    def get_stars(self):
        return Rating(self.rating).label