from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import (
    ListView, UpdateView, CreateView, DeleteView, DetailView
)

from blog.models import Category, Post
from .forms import CommentForm
from .mixins import CommentMixin, IsAuthorMixin, PostMixin, PostPaginateMixin
from .constants import POSTS_LIMIT
from .querysets import (
    post_annotate, post_filter_order, get_profile, get_post_by_id
)


class IndexListView(ListView):
    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/index.html'
    queryset = post_filter_order(post_annotate())


class ProfileListView(ListView):
    model = Post
    paginate_by = POSTS_LIMIT
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_profile(self)
        return context

    def get_queryset(self):
        posts = post_annotate().filter(author=get_profile(self))

        if self.kwargs['username'] != self.request.user.username:
            return post_filter_order(posts)
        else:
            return posts.order_by('-pub_date')


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
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostCreateView(PostMixin, CreateView):

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CategoryListView(PostPaginateMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_id = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']).id

        return post_filter_order(post_annotate()).filter(category=category_id)


class PostDetailView(PostPaginateMixin, DetailView):

    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_post_by_id(self)

        if post.author == self.request.user:
            return post

        return get_object_or_404(
            Post, pk=self.kwargs[self.pk_url_kwarg],
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now(),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = get_post_by_id(self).comments.all()
        return context


class PostDeleteView(PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_post_by_id(self)


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
