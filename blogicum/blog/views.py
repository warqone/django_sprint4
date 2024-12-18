from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.constants import POSTS_LIMIT
from blog.forms import PostForm, EditProfileForm, PostEditForm, CommentForm
from blog.models import Category, Post, Comments

from blogicum.urls import handler500

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_LIMIT

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаем request.FILES в форму для обработки файлов
        kwargs['files'] = self.request.FILES
        return kwargs

    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'category', 'location',
        ).annotate(
            comment_count=Count('comments')
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаем request.FILES в форму для обработки файлов
        kwargs['files'] = self.request.FILES
        return kwargs

    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_LIMIT

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаем request.FILES в форму для обработки файлов
        kwargs['files'] = self.request.FILES
        return kwargs

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        return Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            category=category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        context['category'] = category
        return context


def get_profile(request, username):
    user = get_object_or_404(
        User.objects.all(), username=username
    )
    post_list = Post.objects.select_related(
        'author',
        'category',
        'location',
    ).annotate(
        comment_count=Count('comments')
    ).filter(
        author__username=username
    ).order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile')
    context = {'form': form}
    return render(request, 'blog/user.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.get_username()}
        )


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Post.objects.get(id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return Post.objects.get(id=self.kwargs['post_id'])


@login_required
def add_comment(request, post_id):
    user = get_object_or_404(User, username=request.user)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    if form.is_valid():
        posts = form.save(commit=False)
        posts.author = user
        posts.post = post
        posts.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comments, post_id=post_id, pk=comment_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'comment': instance,
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comments, post_id=post_id, pk=comment_id)
    context = {
        'comment': instance,
    }
    if instance.author == request.user or request.user.is_superuser:
        if request.method == 'POST':
            instance.delete()
            return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
