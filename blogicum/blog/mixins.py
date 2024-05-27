from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import ListView
from django.urls import reverse
from django.utils import timezone

from blog.constants import LIMIT_POST
from blog.forms import CommentForm
from blog.models import Comment, Post


class CommentMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostListMixin(ListView):
    model = Post
    paginate_by = LIMIT_POST

    def get_queryset(self):
        return self.get_posts().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count('comments'))

    def get_posts(self):
        return Post.objects.select_related(
            'category',
            'author',
            'location'
        ).order_by('-pub_date')


class OwnerMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, *kwargs)
