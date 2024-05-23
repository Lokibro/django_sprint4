from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.list import MultipleObjectMixin

from blog.forms import CommentForm, PostForm, UserForm
from blog.constants import LIMIT_POST
from blog.models import Category, Comment, Post



User = get_user_model()

# Список постов на главной странице
class PostsListView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = LIMIT_POST

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

class CategoriesListView(ListView, MultipleObjectMixin):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = LIMIT_POST

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = Post.objects.select_related(
            'author',
            'category',
            'location'
        ).filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True,
            pub_date__lte=timezone.now(),
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileDetailView(DetailView, MultipleObjectMixin):
    model = User
    form_class = UserForm
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    pk_url_kwarg = 'username'
    paginate_by = LIMIT_POST

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author_id=self.get_object().id).order_by('-pub_date').annotate(comment_count=Count('comments'))
        context = super(ProfileDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    pk_url_kwarg = 'username'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        post = self.model.objects.get(username=self.request.user)
        return post

    def form_valid(self, form):
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id')
        )
        if post.author != self.request.user and not post.is_published:
            raise Http404
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post').order_by('created_at')
        )
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def form_valid(self, form):
        return super(PostUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return UpdateView.dispatch(self, request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'form'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostForm()
        form.instance = self.object
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return UpdateView.dispatch(self, request, *args, **kwargs)

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
        return reverse('blog:post_detail', kwargs={'post_id': self.post.pk})

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise Http404
        return super(CommentUpdateView, self).dispatch(request, *args, **kwargs)

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise Http404
        return super(CommentDeleteView, self).dispatch(request, *args, **kwargs)
