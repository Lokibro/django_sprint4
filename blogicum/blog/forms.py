from django import forms
from django.contrib.auth import get_user_model

from blog.models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'text': forms.Textarea(
                {'cols': '22', 'rows': '5'}
            ),
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                {'cols': '22', 'rows': '5'}
            ),
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email'
        ]
