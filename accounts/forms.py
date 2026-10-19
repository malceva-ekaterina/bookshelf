from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import * 

class SingUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{existing_classes} form-control'
            ).strip()
    class Meta():
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{existing_classes} form-control'
            ).strip()
    class Meta:
        model = Profile
        fields = ('bio', 'city', 'avatar')
    
        widgets = {
            "bio": forms.Textarea(attrs={"cols": 100, "rows": 2}),
        }

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{existing_classes} form-control'
            ).strip()
    class Meta:
        model = User
        fields = ('first_name', 'last_name')