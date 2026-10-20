from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DeleteView, DetailView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
# Create your views here.
class SingUpView(CreateView):
    form_class = SingUpForm
    template_name = 'registration/sing_up.html'
    success_url = '/'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
    
class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        if self.object == self.request.user:
            context['is_author'] = True
        else:
            context['is_author'] = True
        if self.request.user.is_authenticated and Follow.objects.filter(author=self.object, follower=self.request.user).exists():
            context['is_follower'] = True
        else:
            context['is_follower'] = False
        
        return context

class UserProfileView(DetailView):
    model = User
    template_name = 'account/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.object == self.request.user:
            context['is_author'] = True
        else:
            context['is_author'] = False
        if self.request.user.is_authenticated and Follow.objects.filter(author=self.object, follower=self.request.user).exists():
            context['is_follower'] = True
        else:
            context['is_follower'] = False
        return context
       

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        
        context = {'user_form': user_form, 'profile_form': profile_form}
        return render(request, 'account/profile_edit.html', context)
    
@login_required 
def follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        is_follow = Follow.objects.filter(author=author, follower=request.user)
        if is_follow:
            is_follow.delete()
        else:
            follower = Follow(author=author, follower=request.user)
            follower.save()
    return redirect('user_profile', author)