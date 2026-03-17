from django.core.exceptions import ValidationError


def validate_username_not_forbidden(value):
    """Запрет username «me» (занят под эндпоинт /users/me/)."""
    if value == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
