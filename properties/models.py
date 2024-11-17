from django.conf import settings
from django.db import models
from django.utils import timezone


class Property(models.Model):
    """
    Represents a property in the real estate system.

    This model implements soft delete functionality, allowing properties to be marked
    as deleted without being removed from the database. Properties marked as deleted
    for more than the retention period can be permanently removed using the purge
    functionality.

    Attributes:
        address (str): The street address of the property
        post_code (str): The postal code of the property
        city (str): The city where the property is located
        number_of_rooms (int): Total number of rooms in the property
        created_by (User): Reference to the user who created this property
        is_deleted (bool): Soft delete flag
        deleted_at (datetime): Timestamp when the property was marked as deleted
        created_at (datetime): Timestamp when the property was created
        updated_at (datetime): Timestamp when the property was last updated
    """

    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    number_of_rooms = models.PositiveIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.address

    def clean(self):
        super().clean()

    def delete(self, *args, **kwargs) -> None:
        """
        Mark record to be deleted.
        """
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    def undo_deletion(self) -> bool:
        """
        Undo deletion of a property.
        """
        if not self.is_deleted:
            return False
        self.is_deleted = False
        self.deleted_at = None
        self.save()
        return True

    @classmethod
    def get_active(cls) -> models.QuerySet:
        """
        Queryset that ignores any records marked for deletion by default.

        Returns:
            QuerySet: All properties where is_deleted is False
        """
        return cls.objects.filter(is_deleted=False)

    @classmethod
    def purge_delete_marked_records(cls, retention_period: int = 30) -> int:
        """
        Delete any records marked for deletion that are older than the retention period.

        Args:
            days (int): Number of days to retain deleted properties

        Returns:
            int: Number of properties that were permanently deleted

        Example:
            >>> Property.purge_delete_marked_records(30)
            2  # Two properties were permanently deleted
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=retention_period)
        properties_to_purge = cls.objects.filter(
            is_deleted=True, deleted_at__lte=cutoff_date
        )
        count, _ = properties_to_purge.delete()
        return count
