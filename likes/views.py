from django.shortcuts import render, redirect
from .models import Like
from django.contrib.contenttypes.models import ContentType
from library.models import Book, Comment, Review
from .utils import like
# Create your views here.

def book_like(request, pk):
    like(request.user, model=Book, object_id=pk)   
    return redirect('book_detail', pk)
    
def comment_like(request, pk, c_pk):
    like(request.user, model=Comment, object_id=c_pk)
    
    return redirect('book_detail', pk)
    
def review_like(request, pk, r_pk):
    like(request.user, model=Review, object_id=r_pk)
    
    return redirect('book_detail', pk)