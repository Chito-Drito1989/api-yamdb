from rest_framework import serializers
from users.models import User


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации. Проверяет email и username."""

    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150)

    def validate_username(self, value):
        """Запрещает использовать 'me' в качестве имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.')
        return value
