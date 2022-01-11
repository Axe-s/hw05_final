from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.related import ForeignKey

from core.models import PubdateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название сообщества',
        max_length=200,
        help_text='Ограничение в 200 символов',
    )
    slug = models.SlugField('адрес сообщества', unique=True)
    description = models.TextField('Описание сообщества')

    def __str__(self):
        return self.title


class Post(PubdateModel):
    text = models.TextField('Новый пост', help_text='Текст нового поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(PubdateModel):
    post = ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        'Комментарий',
        help_text='текст нового комментария',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
