from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User
from users.validators import validate_username_not_forbidden


class SignUpSerializer(serializers.Serializer):
    """Сериализатор регистрации: только валидация, создание через get_or_create во вью."""

    username = serializers.CharField(
        max_length=User.USERNAME_MAX_LENGTH,
        required=True,
        validators=[UnicodeUsernameValidator(), validate_username_not_forbidden],
    )
    email = serializers.EmailField(required=True, max_length=254)

    def validate(self, data):
        user_by_email = User.objects.filter(email=data['email']).first()
        user_by_username = User.objects.filter(username=data['username']).first()
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
        max_length=User.USERNAME_MAX_LENGTH,
        required=True,
        validators=[UnicodeUsernameValidator(), validate_username_not_forbidden],
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(user, data['confirmation_code']):
            raise serializers.ValidationError('Неверный код подтверждения')
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
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
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

    def to_representation(self, instance):
        """Возвращаем полный формат как в ТЗ: category и genre — объекты, rating — число."""
        serializer = TitleSerializer(instance, context=self.context)
        return serializer.data


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
        title = self.context.get('title')
        user = self.context['request'].user
        if title and Review.objects.filter(title=title, author=user).exists():
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
