from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from users.models import User
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .permissions import IsAdmin


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')

    user, created = User.objects.get_or_create(username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код: {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.validated_data[
            'username'])

        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)  # Обычный пользователь не может сам менять себе роль
        return Response(serializer.data, status=status.HTTP_200_OK)
