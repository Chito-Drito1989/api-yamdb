from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Разрешает доступ только администратору."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        is_admin = getattr(request.user, 'is_admin', False)
        return is_admin or request.user.is_superuser


class IsAdminOrReadOnly(BasePermission):
    """Только админ может изменять; остальные — только чтение."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or getattr(user, 'is_admin', False)


class IsAuthorOrModeratorOrAdmin(BasePermission):
    """Редактирование/удаление только автору, модератору или администратору."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, 'is_staff', False):
            return True
        if getattr(user, 'role', None) in ('admin', 'moderator'):
            return True
        author = getattr(obj, 'author', None)
        return author is not None and author.pk == user.pk
