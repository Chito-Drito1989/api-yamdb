<<<<<<< HEAD
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешает доступ только администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated 
            and (request.user.is_admin or request.user.is_superuser)
        )
=======
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (request.user and request.user.is_staff)
>>>>>>> origin/feature/titles-categories-genres-csv
