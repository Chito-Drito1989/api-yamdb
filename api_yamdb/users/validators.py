from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username_not_forbidden(value):
    """Проверка имени пользователя на запрещенные значения."""
    if value in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Недопустимое имя пользователя: "{value}".'
        )
