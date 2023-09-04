from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class IsRoleOpUser(permissions.BasePermission):
    message = 'You are not authorized.'

    def has_permission(self, request, view):
        if request.user.is_ops_user:
            return True
        else:
            return False
        
class IsRoleClientUser(permissions.BasePermission):
    message = 'You are not authorized.'

    def has_permission(self, request, view):
        if request.user.is_ops_user:
            return False
        else:
            return True