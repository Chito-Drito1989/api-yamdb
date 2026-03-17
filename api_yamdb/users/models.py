from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class RoleChoices(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
        help_text='Расскажите немного о себе'
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        help_text='Уровень доступа пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
