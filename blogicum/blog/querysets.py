from django.db.models import Count
from django.utils import timezone

from blog.models import Post


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
