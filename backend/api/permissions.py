from rest_framework import permissions
from .models import User


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if the user has ADMIN role.
    Only allows access if the user is authenticated and has ADMIN role.
    """

    def has_permission(self, request, view):
        """
        Check if the user has ADMIN role.
        """
        # Check if user is authenticated
        if not hasattr(request, 'user') or not request.user:
            return False

        # If user is a User instance, check role directly
        if isinstance(request.user, User):
            return request.user.role == 'ADMIN'

        # If user is not a User instance, it means authentication failed
        return False

