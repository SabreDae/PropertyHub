from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest

from .models import Property


def purge_soft_deleted(
    modeladmin: ModelAdmin, request: HttpRequest, queryset: Property
):
    retention_period = 30
    # FIXME: Providing a hard-coded retention period, but this could be flexible and received from front-end
    count = Property.purge_delete_marked_records(retention_period)
    modeladmin.message_user(request, f"{count} properties were permanently deleted.")


@admin.register(Property)
class PropertyAdmin(ModelAdmin):
    """
    Admin interface configuration for Property model.

    Provides:
        - List display with key property information
        - Filtering by deletion status and creator
        - Search functionality for address fields
        - Custom action for purging soft-deleted properties
        - Read-only fields for metadata

    Notes:
        - Soft-deleted properties remain visible in admin
        - Created_by and deleted_at fields are read-only
        - Custom purge action available for cleaning up old deleted properties
    """

    list_display = [
        "address",
        "post_code",
        "city",
        "number_of_rooms",
        "created_by",
        "is_deleted",
        "deleted_at",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_deleted", "created_by"]
    search_fields = ["address", "post_code", "city"]
    readonly_fields = ["created_by", "deleted_at", "updated_at", "created_at"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "address",
                    "post_code",
                    "city",
                    "number_of_rooms",
                    "created_by",
                    "is_deleted",
                    "deleted_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    actions = [purge_soft_deleted]
