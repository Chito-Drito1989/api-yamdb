from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Разрешает доступ только администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """Только админ может изменять; остальные — только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser)
            )
        )


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):
    """
    Чтение — всем; создание — авторизованным; правка/удаление —
    автор, модератор или админ.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in SAFE_METHODS or (
            user.is_authenticated
            and (
                user.is_admin
                or user.is_moderator
                or obj.author_id == user.pk
            )
        )
