from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User
from .serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateUpdateSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')

    user_by_email = User.objects.filter(email=email).first()
    user_by_username = User.objects.filter(username=username).first()
    if user_by_email and user_by_email.username != username:
        return Response(
            {'detail': 'Пользователь с таким email уже зарегистрирован.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if user_by_username and user_by_username.email != email:
        return Response(
            {'detail': 'Пользователь с таким username уже зарегистрирован.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = user_by_email or user_by_username
    if not user:
        user = User.objects.create(username=username, email=email)

    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    user.save(update_fields=['confirmation_code'])

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
        user = get_object_or_404(User, username=serializer.validated_data['username'])
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
        serializer.save(role=user.role)  # пользователь не может сам менять себе роль
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('id')
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        genre = self.request.query_params.get('genre')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')
        if category:
            qs = qs.filter(category__slug=category)
        if genre:
            qs = qs.filter(genre__slug=genre)
        if year:
            qs = qs.filter(year=year)
        if name:
            qs = qs.filter(name__icontains=name)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы по произведению. Список/детали — без токена; создание — авторизованный; правка/удаление — автор, модератор или админ."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrModeratorOrAdmin()]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        review_id = self.kwargs.get('review_id')
        obj = get_object_or_404(queryset, pk=review_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        # запрет второго отзыва от того же пользователя на то же произведение
        if Review.objects.filter(title=title, author=self.request.user).exists():
            raise ValidationError(
                {'detail': 'Вы уже оставили отзыв на это произведение.'}
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзыву. Аналогично отзывам: чтение без токена; создание — авторизованный; правка/удаление — автор, модератор или админ."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id, review__title_id=title_id)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrModeratorOrAdmin()]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        comment_id = self.kwargs.get('comment_id')
        obj = get_object_or_404(queryset, pk=comment_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id, title_id=title_id)
        serializer.save(author=self.request.user, review=review)
