from datetime import timedelta
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.utils import timezone

from ..admin import PropertyAdmin, purge_soft_deleted
from ..models import Property


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True


class PropertyAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = PropertyAdmin(Property, self.site)
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@test.com", password="password123"
        )

        self.active_property = Property.objects.create(
            address="123 Active St",
            post_code="AC1 2TV",
            city="Test City",
            number_of_rooms=3,
            created_by=self.user,
        )

        self.deleted_property = Property.objects.create(
            address="456 Deleted St",
            post_code="DE1 3TD",
            city="Test City",
            number_of_rooms=2,
            created_by=self.user,
        )
        self.deleted_property.delete()

    def test_list_display(self):
        expected_fields = [
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
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_list_filter(self):
        expected_filters = ["is_deleted", "created_by"]
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_search_fields(self):
        expected_search = ["address", "post_code", "city"]
        self.assertEqual(self.admin.search_fields, expected_search)

    def test_readonly_fields(self):
        expected_readonly = ["created_by", "deleted_at", "updated_at", "created_at"]
        self.assertEqual(self.admin.readonly_fields, expected_readonly)

    def test_fieldsets(self):
        expected_fields = (
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
        self.assertEqual(self.admin.fieldsets[0][1]["fields"], expected_fields)

    def test_actions(self):
        self.assertIn(purge_soft_deleted, self.admin.actions)

    def test_purge_soft_deleted_action(self):
        # Create a property that was deleted more than 30 days ago
        old_deleted_property = Property.objects.create(
            address="789 Old Deleted St",
            post_code="OD1 4TD",
            city="Test City",
            number_of_rooms=4,
            created_by=self.user,
            is_deleted=True,
            deleted_at=timezone.now() - timedelta(days=31),
        )
        request = self.factory.post("/")
        request.user = self.user

        # Add message storage to request
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        # Execute
        queryset = Property.objects.filter(is_deleted=True)
        purge_soft_deleted(self.admin, request, queryset)

        # Verify old deleted property is gone
        with self.assertRaises(Property.DoesNotExist):
            Property.objects.get(pk=old_deleted_property.pk)

        # Verify recently deleted property still exists
        self.assertTrue(Property.objects.filter(pk=self.deleted_property.pk).exists())

    def test_purge_soft_deleted_no_eligible_records(self):
        request = self.factory.post("/")
        request.user = self.user
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        queryset = Property.objects.filter(is_deleted=True)
        purge_soft_deleted(self.admin, request, queryset)

        # Verify recently deleted property still exists
        self.assertTrue(Property.objects.filter(pk=self.deleted_property.pk).exists())

    def test_get_readonly_fields(self):
        request = self.factory.get("/")
        request.user = self.user

        readonly_fields = self.admin.get_readonly_fields(request)
        self.assertIn("created_by", readonly_fields)
        self.assertIn("deleted_at", readonly_fields)

    def test_has_delete_permission(self):
        request = self.factory.get("/")
        request.user = self.user

        self.assertTrue(self.admin.has_delete_permission(request, self.active_property))

    def test_has_add_permission(self):
        request = self.factory.get("/")
        request.user = self.user

        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_change_permission(self):
        request = self.factory.get("/")
        request.user = self.user

        self.assertTrue(self.admin.has_change_permission(request, self.active_property))
