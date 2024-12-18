from django.contrib import admin

from blog.models import Category, Location, Post, Comments


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'author',
        'location',
        'category',
        'pub_date',
    )
    search_fields = (
        'title',
        'author__username',
        'category_id__title',
    )
    list_filter = (
        'title',
        'category',
        'author',

    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'title',
        'slug',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'author',
    )


admin.site.empty_value_display = 'Не задано'
