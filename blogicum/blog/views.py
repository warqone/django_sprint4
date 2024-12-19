from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from blog.forms import PostForm, EditProfileForm, CommentForm
from blog.models import Category, Post, Comments
from blog.utils import get_posts, get_post_by_id, paginator

User = get_user_model()


def homepage(request):
    """Функция для главной страницы,
    возвращающая набор опубликованных постов с постраничным выводом.
    """
    posts = get_posts()
    page_obj = paginator(posts, request)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id: int):
    """Функция, возвращающая конкретный пост с открытием
    комментариев и формы комментариев.
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            Post, id=post_id,
            category__is_published=True,
            is_published=True,
        )
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {'form': form, 'post': post, 'comments': comments}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug: str):
    """Функция, возвращающая набор
    опубликованных постов определённой категории.
    """
    posts = get_posts().filter(
        category__slug=category_slug
    )
    category = get_object_or_404(
        Category.objects.values(
            'title',
            'description',
        ), slug=category_slug,
        is_published=True
    )
    page_obj = paginator(posts, request)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def get_profile(request, username: str):
    """Функция, возвращающая профиль пользователя
    с постами и информацией профиля.
    """
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author',
        'category',
        'location',
    ).filter(
        author__username=username
    ).order_by('-pub_date')
    page_obj = paginator(posts, request)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username: str):
    """Функция, для открытия формы редактирования профиля."""
    user = get_object_or_404(User, username=username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def create_post(request):
    """Функция для создания поста(записи) с формой."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_update(request, post_id: int):
    """Функция для редактирования поста."""
    if not request.user.is_authenticated:
        return redirect('login')
    instance = get_post_by_id(post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, instance=instance,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_delete(request, post_id: int):
    """Функция для удаления поста."""
    post = get_post_by_id(post_id)
    if request.method == 'POST' and post.author == request.user:
        post.delete()
        return redirect('blog:profile', username=request.user)
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id: int):
    """Функция, для добавления комментария к записи."""
    post = get_post_by_id(post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    if form.is_valid():
        posts = form.save(commit=False)
        posts.author = request.user
        posts.post = post
        posts.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', context)


def edit_comment(request, post_id: int, comment_id: int):
    """Функция, для редактирования комментария к записи."""
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


def delete_comment(request, post_id: int, comment_id: int):
    """Функция, для удаления комментария к записи."""
    instance = get_object_or_404(Comments, post_id=post_id, pk=comment_id)
    context = {
        'comment': instance,
    }
    if instance.author == request.user or request.user.is_superuser:
        if request.method == 'POST':
            instance.delete()
            return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
