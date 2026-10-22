from rest_framework import permissions, SAFE_METHODS

class IsAdminOrReadOnly(BasePermissions):
    def has_permissions(self,request,view):
        if request.method in SAFE_METHODS:
            return true
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == 'admin' or user.is_staff)
        )