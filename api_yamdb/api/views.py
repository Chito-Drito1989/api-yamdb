from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from users.models import User
from .serializers import SignUpSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Регистрация пользователя и отправка кода подтверждения."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')

    # Пытаемся получить или создать пользователя
    user, created = User.objects.get_or_create(username=username, email=email)

    # Генерируем код (токен)
    confirmation_code = default_token_generator.make_token(user)

    # Отправка почты
    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код подтверждения: {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)
