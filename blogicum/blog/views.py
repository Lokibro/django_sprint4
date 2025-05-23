from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, UpdateView
)
from django.views.generic.list import MultipleObjectMixin

from blog.forms import CommentForm, PostForm, UserForm
from blog.mixins import CommentMixin, OwnerMixin, PostListMixin
from blog.models import Category, Comment, Post


User = get_user_model()


class PostsListView(PostListMixin):
    template_name = 'blog/index.html'


class CategoriesListView(PostListMixin, MultipleObjectMixin):
    template_name = 'blog/category.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.get_queryset()
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return super().get_queryset().filter(
            category=category
        )


class ProfileDetailView(PostListMixin, MultipleObjectMixin):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if user.username == str(self.request.user):
            posts = self.get_posts().filter(
                author=user
            )
        else:
            posts = super().get_queryset().filter(
                author=user
            )
        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = self.get_queryset()
        context = super().get_context_data(
            object_list=object_list,
            **kwargs
        )
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(
            Post.objects.select_related('category', 'author'),
            Q(pk=self.kwargs['post_id']),
            Q(author__username=self.request.user) | Q(
                Q(
                    is_published=True
                ) & Q(
                    category__is_published=True
                ) & Q(
                    pub_date__lte=timezone.now()
                )
            )
        )
        context['form'] = CommentForm()
        context['comments'] = post.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(OwnerMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(OwnerMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostForm()
        form.instance = self.object
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        self.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.post.pk}
        )


class CommentUpdateView(
    OwnerMixin,
    LoginRequiredMixin,
    CommentMixin,
    UpdateView
):
    pass


class CommentDeleteView(
    OwnerMixin,
    LoginRequiredMixin,
    CommentMixin,
    DeleteView
):
    pass
