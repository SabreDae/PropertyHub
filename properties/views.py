import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import status
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from typing import Any


from .models import Property
from .serializers import PropertySerializer
from .permissions import IsPropertyAdminOrCreator

logger = logging.getLogger(__name__)


class PropertyListCreate(ListCreateAPIView):
    """
    API endpoint for listing and creating properties.

    GET: Returns a list of all active (non-deleted) properties
    POST: Creates a new property
    """

    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns queryset of active properties."""
        return Property.get_active()

    def perform_create(self, serializer):
        """Creates a new property with the current user as creator."""
        return serializer.save(created_by=self.request.user)


class PropertyRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting specific properties.

    GET: Retrieve property details
    PATCH: Update property details
    DELETE: Soft delete property
    """

    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsPropertyAdminOrCreator]

    def get_queryset(self) -> QuerySet[Property]:
        """Returns all properties, including deleted ones"""
        return Property.objects.all()

    def get_object(self) -> Property:
        """
        Retrieve and validate the property object.
        """
        property = super().get_object()

        # For methods PATCH, PUT, DELETE, check if property is deleted
        if self.request.method in ["PATCH", "PUT"] and property.is_deleted:
            raise ValueError("Cannot modify a deleted property")
        if self.request.method == "DELETE" and property.is_deleted:
            raise ValueError("Property is already deleted")

        return property

    def update(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """Handle PUT/PATCH requests with custom error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance: Property) -> None:
        """Performs soft delete instead of hard delete."""
        instance.delete()
        logger.info(f"Property {instance.id} deleted by {self.request.user.id}")

    def get_serializer_context(self):
        """Adds additional context for the serializer."""
        context = super().get_serializer_context()
        context.update(
            {"is_admin": self.request.user.is_staff, "user_id": self.request.user.id}
        )
        return context


class PropertyRecover(GenericAPIView):
    """
    API endpoint for recovering (un-deleting) a property.
    """

    permission_classes = [IsAuthenticated, IsPropertyAdminOrCreator]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        try:
            property = self.get_object()

            if not property.is_deleted:
                return Response(
                    {"detail": "This property is not deleted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            property.undo_deletion()
            return Response(
                {"detail": "Property recovered successfully"}, status=status.HTTP_200_OK
            )

        except Property.DoesNotExist:
            return Response(
                {"detail": "Property not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except (DRFPermissionDenied, DjangoPermissionDenied) as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(
                f"Unexpected error recovering property {kwargs.get('pk')}: {str(e)}"
            )
            return Response(
                {"detail": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
