from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.constants import LIMIT_POST
from blog.models import Category, Post


User = get_user_model()

def get_objects(model: models.Model):
    return model.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    posts = get_objects(Post)[:LIMIT_POST]
    context = {'post_list': posts}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(get_objects(Post), pk=post_id)
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(),
        slug=category_slug,
        is_published=True
    )
    posts = get_objects(Post).filter(category=category)
    context = {'category': category, 'post_list': posts}
    return render(request, 'blog/category.html', context)

# Работа с пользователями

class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])


class ProfileUpdateView(UpdateView):
    model = User
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')