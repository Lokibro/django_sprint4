from django.contrib.auth import get_user_model
from django import forms

from blog.models import Post, Comment


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


class UserForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email'
        ]