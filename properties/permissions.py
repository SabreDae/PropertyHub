from django.http import HttpRequest
from django.views import View
from rest_framework import permissions

from .models import Property


class IsPropertyCreator(permissions.BasePermission):
    """
    Allow access only to property creators.
    """

    message = "You must be the creator of this property to perform this action."

    def has_object_permission(
        self, request: HttpRequest, view: View, obj: Property
    ) -> bool:
        return obj.created_by == request.user


class IsPropertyAdminOrCreator(permissions.BasePermission):
    """
    Allow access to admin users or property creators.
    """

    message = "You must be an admin or the creator of this property."

    def has_object_permission(
        self, request: HttpRequest, view: View, obj: Property
    ) -> bool:
        return request.user.is_staff or IsPropertyCreator().has_object_permission(
            request, view, obj
        )
