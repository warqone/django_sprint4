# Generated by Django 3.2.16 on 2024-12-18 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20241218_2330'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comments',
            options={'default_related_name': 'comments', 'ordering': ('created_at',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]
