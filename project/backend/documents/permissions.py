from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Позволяет авторам редактировать/удалять свои документы.
    Остальным только чтение.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем изменения только если пользователь == автор
        return obj.created_by == request.user
