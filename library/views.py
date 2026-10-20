from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Q, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce
from .models import *
from .forms import *
from likes.utils import *
from collections import defaultdict

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
        queryset = super().get_queryset()

        query = self.request.GET.get('q')
        genre_id = self.request.GET.get('genre')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)

        reviews_subquery = Review.objects.filter(
            book_id=OuterRef('pk')  
        ).values('book_id').annotate(avg=Avg('rating')).values('avg')


        queryset = queryset.annotate(
            avg_rating=Coalesce(Subquery(reviews_subquery), 0.0)
        )

        if genre_id:
            queryset = queryset.distinct()

        return queryset.prefetch_related('genres')
    
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
        return super().get_queryset().prefetch_related('genres', 'author').annotate(avg_rating=(Avg('reviews__rating')*100/5))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_is_liked'] = is_liked_by(self.request.user, Book, self.object.pk)
        
        qs = (
            self.object.comments
            .select_related('user', 'user__profile')
            .annotate(likes_count=Count('likes'))      # счётчик лайков
            .order_by('-created_at')
        )
        qs = annotate_liked_by_user(qs, self.request.user, Comment)  # ← аннотация на ВСЕ

        # 2. Строим дерево
        children_map = defaultdict(list)
        for c in qs:
            children_map[c.parent_id].append(c)
        for c in qs:
            c.children = children_map[c.id]

        context['comments'] = children_map[None]
        review_qs = (
            self.object.reviews.order_by('-created_at')
        )
        if self.request.user.is_authenticated:
            context['review_exist'] = Review.objects.filter(book=self.object, user=self.request.user).exists
        else:
            context['review_exist'] = False
            
        context['review_form'] = ReviewForm()   
        context['reviews'] = annotate_liked_by_user(review_qs, self.request.user, Review)
        if self.request.user.is_authenticated and Review.objects.filter(book=self.object, user=self.request.user).exists():
            review = Review.objects.get(book=self.object, user=self.request.user)
            context['review_form'] = ReviewForm(instance=review)
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
def create_review(request, b_pk):
    book = get_object_or_404(Book, id=b_pk)
    if not Review.objects.filter(book=book, user=request.user).exists():
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                form.save(commit=False)
                form.instance.user = request.user
                form.instance.book = book
                form.save()
    return redirect('book_detail', b_pk)
        
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

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = "reviews/review_form.html"
    form_class = ReviewForm
    def get_success_url(self):
            return reverse('book_detail', kwargs={'pk': self.request.path.GET.get('b_pk') | self.request.path.POST.get('b_pk') })
    def test_func(self):
            return self.get_object().user == self.request.user

@login_required
def review_update(request, b_pk):
    book = Book.objects.get(pk=b_pk)
    review = get_object_or_404(Review, user=request.user, book=book)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
    return redirect('book_detail', b_pk)