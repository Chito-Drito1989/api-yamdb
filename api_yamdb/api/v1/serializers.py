from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User, USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH
from users.validators import validate_username_not_forbidden


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор регистрации: только валидация, создание через
    get_or_create во вью.
    """

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_forbidden,
        ],
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
    )

    def validate(self, data):
        user_by_email = User.objects.filter(email=data['email']).first()
        user_by_username = User.objects.filter(
            username=data['username']
        ).first()
        if user_by_email != user_by_username:
            error_msg = {}
            if user_by_email is not None:
                error_msg['email'] = ['Этот email уже занят.']
            if user_by_username is not None:
                error_msg['username'] = ['Этот username уже занят.']
            raise serializers.ValidationError(error_msg)
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_forbidden,
        ],
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(
            user, data['confirmation_code']
        ):
            raise serializers.ValidationError('Неверный код подтверждения')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(default=None, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description',
            'genre', 'category',
        )


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва: текст, оценка 1–10, автор (read_only)."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        view = self.context.get('view')
        title_id = view.kwargs.get('title_id') if view else None
        user = self.context['request'].user
        if title_id and user.is_authenticated:
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к отзыву."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
