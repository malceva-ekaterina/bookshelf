from django import forms
from .models import *
from django.core.validators import FileExtensionValidator
from django.contrib.contenttypes.models import ContentType

class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{existing_classes} form-control'
            ).strip()
    cover = forms.ImageField(
        help_text="Upload your avatar image",
        validators=[
			FileExtensionValidator(
				allowed_extensions=['jpg', 'jpeg', 'png']
			)
		]
    )
    class Meta:
        model = Book
        fields = ('title', 'description', 'cover', 'genres', 'author')
        widgets = {
                    "description": forms.Textarea(attrs={"class": 'form-control', "rows": 2}),
                }
        
        
class CommentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (
                    f'{existing_classes} form-control'
                ).strip()
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            "text": forms.Textarea(attrs={"class": 'form-control', "rows": 3}),
        }

       
class GenreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (
                    f'{existing_classes} form-control'
                ).strip()
    class Meta:
        model = Genre
        fields = ('name', 'slug')

class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (
                    f'{existing_classes} form-control'
                ).strip()
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'sur_name')

class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (
                    f'{existing_classes} form-control'
                ).strip()
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            "text": forms.Textarea(attrs={"class": 'form-control', "rows": 3}),
        }

