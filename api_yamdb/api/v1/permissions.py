from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Разрешает доступ только администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(BasePermission):
    """Только админ может изменять; остальные — только чтение."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """Редактирование/удаление только автору, модератору или администратору."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_admin or user.role == 'moderator':
            return True
        author = getattr(obj, 'author', None)
        return author is not None and author.pk == user.pk


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):
    """
    Чтение — всем; создание — авторизованным; правка/удаление —
    автор, модератор или админ.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_admin or user.role == 'moderator':
            return True
        author = getattr(obj, 'author', None)
        return author is not None and author.pk == user.pk
