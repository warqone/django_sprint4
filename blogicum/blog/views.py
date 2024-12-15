from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.constants import POSTS_LIMIT
from blog.models import Category, Post

User = get_user_model()


def get_posts():
    """Функция которая возвращает базовый набор опубликованных объектов."""
    return Post.objects.select_related(
        'author',
        'category',
        'location',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    """Вкладка с последними опубликованными постами."""
    post_list = get_posts().order_by('-pub_date')[:POSTS_LIMIT]

    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Вкладка с подробностями поста."""
    post = get_object_or_404(
        get_posts(), pk=post_id
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Вкладка с постами определённой категории."""
    category = get_object_or_404(
        Category.objects.values(
            'slug',
            'title',
        ).filter(is_published=True),
        slug=category_slug
    )
    post_list = get_posts().filter(category__slug=category_slug)
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, 'blog/category.html', context)


def get_profile(request, username):
    user = get_object_or_404(
        User.objects.all(), username=username
    )
    return render(request, 'blog/profile.html', {'profile': user})
