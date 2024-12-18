from django import forms
from django.contrib.auth.models import User

from .models import Post, Comments


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
