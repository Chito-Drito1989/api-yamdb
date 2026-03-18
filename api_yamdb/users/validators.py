from django.core.exceptions import ValidationError

FORBIDDEN_USERNAMES = ('me',)


def validate_username_not_forbidden(value):
    """Запрет зарезервированных username (напр. me — эндпоинт /users/me/)."""
    if value in FORBIDDEN_USERNAMES:
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
