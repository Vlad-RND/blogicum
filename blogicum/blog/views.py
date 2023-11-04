from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views.generic import (
    ListView, UpdateView, CreateView, DetailView, DeleteView
)

from blog.models import Category, Post, Comment
from .constants import POSTS_LIMIT
from .forms import PostForm, CommentForm


class PostPaginateMixin():
    model = Post
    paginate_by = POSTS_LIMIT


class PostFormTempMixin():
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentSuccessUrlMixin():
    model = Comment

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class IndexListView(PostPaginateMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class ProfileListView(PostPaginateMixin, ListView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context

    def get_queryset(self):
        username = self.kwargs['username']
        author_id = get_object_or_404(User, username=username).pk

        if username == self.request.user.username:
            return Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(
                author=author_id
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        else:
            return Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
                author=author_id
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'email', 'first_name', 'last_name')
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.object.username})


class PostUpdateView(PostFormTempMixin, LoginRequiredMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(PostFormTempMixin, LoginRequiredMixin, CreateView):

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CategoryListView(PostPaginateMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        return Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            category=get_object_or_404(
                Category,
                is_published=True,
                slug=self.kwargs['category_slug']).id
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related('category', 'location', 'author'),
            pk=self.kwargs['post_id'],
        )
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(
                Post.objects.select_related('category', 'location', 'author'),
                pk=self.kwargs['post_id'],
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author'))
        return context


class PostDeleteView(PostFormTempMixin, LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True,
            author=self.request.user,
        )


class CommentCreateView(LoginRequiredMixin,
                        CommentSuccessUrlMixin,
                        CreateView):
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin,
                        CommentSuccessUrlMixin,
                        DeleteView):
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            post_id=self.kwargs['post_id'],
            pk=self.kwargs['comment_id'],
            author=self.request.user,
        )


class CommentUpdateView(LoginRequiredMixin,
                        CommentSuccessUrlMixin,
                        UpdateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            post_id=self.kwargs['post_id'],
            pk=self.kwargs['comment_id'],
            author=self.request.user,
        )
