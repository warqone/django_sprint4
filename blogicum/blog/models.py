from django.contrib.auth import get_user_model
from django.db import models

from blog.abstract_models import PublishedModel
from blog.constants import LETTER_LIMIT, MAX_LENGTH

User = get_user_model()
#  Оптимизировал как смог, чтобы не было ошибок pytest и в работе сайта.


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:LETTER_LIMIT]


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:LETTER_LIMIT]


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = ('posts')
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title[:LETTER_LIMIT]

    @property
    def comment_count(self):
        return self.comments.count()


class Comments(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:LETTER_LIMIT]

    class Meta:
        ordering = ('created_at',)
        default_related_name = ('comments')
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
