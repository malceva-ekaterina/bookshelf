from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import *
from .forms import *
from likes.utils import *
# Create your views here.

class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "authors/author_form.html"
    
    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()
    
class GenreCreateView(LoginRequiredMixin, CreateView):
    model = Genre
    form_class = GenreForm
    
    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()
    
class BookListView(ListView):
    model = Book
    template_name = "books/index.html"
    context_object_name = 'books'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('genres')

        query = self.request.GET.get('q')
        genre_id = self.request.GET.get('genre')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['genres'] = Genre.objects.all()
        context['selected_query'] = self.request.GET.get('q', '')
       
        context['selected_genre'] = self.request.GET.get('genre', '')
        if context['selected_genre'].isdigit():
            context['selected_genre'] = int(context['selected_genre'])
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related('genres', 'author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_is_liked'] = is_liked_by(self.request.user, Book, self.object.pk)
        
        comments_qs = (
            self.object.comments
            .filter(parent__isnull=True)
            .select_related('user', 'user__profile')
            .prefetch_related('replies__user', 'replies__user__profile')
            .order_by('-created_at')
        )
        context['comments'] = annotate_liked_by_user(comments_qs, self.request.user, Comment)
        
        review_qs = (
            self.object.reviews.order_by('-created_at')
        )
        context['review_exist'] = Review.objects.filter(book=self.object, user=self.request.user).exists
        
        context['reviews'] = annotate_liked_by_user(review_qs, self.request.user, Review)
        context['review_form'] = ReviewForm()
        context['comment_form'] = CommentForm()
        return context
    
    
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"
    
    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_form"] = AuthorForm()
        context["genre_form"] = GenreForm()
        return context
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = "books/book_form.html"
    form_class = BookForm
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["author_form"] = AuthorForm()
            context["genre_form"] = GenreForm()
            return context
        
    def test_func(self):
        return self.get_object().owner == self.request.user

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    
    def get_success_url(self):
        return reverse('user_profile', kwargs={'username': self.request.user.username})
    def test_func(self):
            return self.get_object().owner == self.request.user


@login_required
def create_review(request, pk):
    book = get_object_or_404(Book, id=pk)
    if not Review.objects.filter(book=book, user=request.user).exists():
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.instance.user = request.user
                form.instance.book = book
                form.save()
    return redirect('book_detail', pk)
        
@login_required
def create_comment(request, pk):
    book = Book.objects.get(id=pk)
    text = request.POST.get('text')
    parent_id = request.POST.get('parent_id') # Передается, если это ответ
    
    parent_obj = None
    if parent_id:
        parent_obj = Comment.objects.get(id=parent_id)

    Comment.objects.create(
        user=request.user,
        text=text,
        content_object=book, 
        parent=parent_obj  
    )
    return redirect('book_detail', pk)

