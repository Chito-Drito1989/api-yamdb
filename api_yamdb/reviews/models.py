import datetime as dt
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 50
SCORE_MIN = 1
SCORE_MAX = 10


def validate_year(value):
    """Проверка, что год не превышает текущий."""
    current_year = dt.date.today().year
    if value > current_year:
        raise ValidationError(f'Год {value} больше текущего {current_year}!')


class Category(models.Model):
    """Категория произведения."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Наименование'
    )
    slug = models.SlugField(
        unique=True, max_length=SLUG_MAX_LENGTH, verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанр произведения."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Наименование'
    )
    slug = models.SlugField(
        unique=True, max_length=SLUG_MAX_LENGTH, verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведение: фильм, книга или музыка."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    year = models.SmallIntegerField(validators=[validate_year],
                                    verbose_name='Год')
    description = models.TextField(blank=True, null=True,
                                   verbose_name='Описание')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='titles',
        null=True, verbose_name='Категория'
    )
    genre = models.ManyToManyField(Genre, related_name='titles', blank=True,
                                   verbose_name='Жанр')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Отзыв пользователя на произведение."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(SCORE_MIN),
            MaxValueValidator(SCORE_MAX),
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.username} — {self.title.name}'


class Comment(models.Model):
    """Комментарий пользователя к отзыву."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.author.username} — {self.review.id}'
