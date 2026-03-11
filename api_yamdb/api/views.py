from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from reviews.models import Category, Genre, Title, Review, Comment
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateUpdateSerializer,
    ReviewSerializer,
    CommentSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

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
