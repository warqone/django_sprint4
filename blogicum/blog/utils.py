from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils import timezone

from blog.constants import POSTS_LIMIT
from blog.models import Post


def get_posts():
    """Функция, возвращающая базовый набор опубликованных постов."""
    return Post.objects.select_related(
        'author', 'category', 'location',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def get_post_by_id(id):
    """Функция, возвращающая пост либо 404 по заданному ID."""
    return get_object_or_404(Post, id=id)


def paginator(objects, request):
    """Функция, для постраничного вывода постов либо другой информации."""
    paginator = Paginator(objects, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
