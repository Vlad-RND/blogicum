from django.db.models import Count
from django.utils import timezone


def post_annotate(posts):
    return posts.select_related(
        'category', 'location', 'author'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def post_filter_order(obj):
    return obj.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )
