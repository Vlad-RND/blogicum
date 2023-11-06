from django.db.models import Count
from blog.models import Post
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


def post_annotate():
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments'))


def post_filter_order(obj):
    return obj.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    ).order_by('-pub_date')


def get_profile(self):
    return get_object_or_404(User, username=self.kwargs['username'])


def get_post_by_id(self):
    return get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=self.kwargs['post_id'],
    )
