from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import (
    ListView, UpdateView, CreateView, DeleteView
)

from blog.models import Category, Post
from .forms import CommentForm, PostForm
from .mixins import CommentMixin, IsAuthorMixin, PostMixin, PostPaginateMixin
from .constants import POSTS_LIMIT
from .querysets import post_annotate, post_filter_order


class IndexListView(ListView):
    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/index.html'
    queryset = post_filter_order(post_annotate(Post.objects))


class ProfileListView(ListView):
    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/profile.html'

    def get_profile(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context

    def get_queryset(self):
        posts = post_annotate(self.get_profile().posts.all())

        if self.get_profile() != self.request.user:
            posts = post_filter_order(posts)

        return posts


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'email', 'first_name', 'last_name')
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.object.username})


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CategoryListView(PostPaginateMixin, ListView):
    template_name = 'blog/category.html'

    def get_category(self):
        return get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )

    def get_queryset(self):
        return post_filter_order(post_annotate(self.get_category().posts))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostDetailView(PostPaginateMixin, ListView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return self.get_object().comments.all()

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related('category', 'location', 'author'),
            pk=self.kwargs['post_id'],
        )

        if post.author == self.request.user:
            return post

        return get_object_or_404(
            post_filter_order(Post.objects),
            pk=self.kwargs[self.pk_url_kwarg],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = self.get_object()
        return context


class PostDeleteView(PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentDeleteView(CommentMixin, IsAuthorMixin, DeleteView):
    pass


class CommentUpdateView(CommentMixin, IsAuthorMixin, UpdateView):
    pass


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
