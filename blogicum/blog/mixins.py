from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, reverse, redirect

from blog.models import Comment, Post
from .forms import PostForm, CommentForm
from .constants import POSTS_LIMIT


class IsAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        author = self.request.user

        if 'comment_id' in self.kwargs:
            author = get_object_or_404(
                Comment, pk=self.kwargs['comment_id']
            ).author
        elif 'post_id' in self.kwargs:
            author = get_object_or_404(Post, pk=self.kwargs['post_id']).author

        if self.request.user == author:
            return True
        else:
            return False


class PostMixin(IsAuthorMixin, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.object.author})


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostPaginateMixin():
    model = Post
    paginate_by = POSTS_LIMIT
