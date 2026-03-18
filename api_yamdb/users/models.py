from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import validate_username_not_forbidden

USERNAME_MAX_LENGTH = 150
ROLE_MAX_LENGTH = 20
EMAIL_MAX_LENGTH = 254


class RoleChoices(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_forbidden,
        ],
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
        help_text='Расскажите немного о себе'
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        help_text='Уровень доступа пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        """Администратор по роли или superuser."""
        return (
            self.role == RoleChoices.ADMIN
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == RoleChoices.MODERATOR

    def __str__(self):
        return self.username
