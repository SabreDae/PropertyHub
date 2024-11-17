from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from datetime import timedelta

from ..models import Property


TEST_USER = get_user_model()

class PropertyModelTests(TestCase):
    def setUp(self):
        self.user = TEST_USER.objects.create_user(
            username="testuser@example.com",
            password="XXXXXXXXXXXX"
        )
        self.property = Property.objects.create(
            address="123 Test St",
            post_code="AB12 3CD",
            city="Test City",
            number_of_rooms=2,
            created_by=self.user
        )

    def test_property_creation(self):
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(self.property.address, "123 Test St")
        self.assertEqual(self.property.post_code, "AB12 3CD")
        self.assertEqual(self.property.city, "Test City")
        self.assertEqual(self.property.number_of_rooms, 2)
        self.assertEqual(self.property.created_by, self.user)
        self.assertFalse(self.property.is_deleted)
        self.assertIsNone(self.property.deleted_at)

    def test_property_soft_deletion(self):
        self.property.delete()
        self.assertTrue(self.property.is_deleted)
        self.assertIsNotNone(self.property.deleted_at)
        self.assertTrue(Property.objects.filter(id=self.property.id).exists())

    def test_property_undo_deletion(self):
        self.property.delete()
        self.property.undo_deletion()
        self.assertFalse(self.property.is_deleted)
        self.assertIsNone(self.property.deleted_at)

    def test_get_active_properties(self):
        Property.objects.create(
            address="456 Test St",
            post_code="EF45 6GH",
            city="Test City",
            created_by=self.user,
            is_deleted=True
        )
        active_properties = Property.get_active()
        self.assertEqual(active_properties.count(), 1)
        self.assertEqual(active_properties.first(), self.property)

    def test_purge_deleted_properties(self):
        old_property = Property.objects.create(
            address="789 Test St",
            post_code="IJ89 0KL",
            city="Test City",
            created_by=self.user,
            is_deleted=True,
            deleted_at=timezone.now() - timedelta(days=31)
        )
        count = Property.purge_delete_marked_records(retention_period=30)
        self.assertEqual(count, 1)
        self.assertFalse(
            Property.objects.filter(id=old_property.id).exists()
        )

    def test_update_deleted_property(self):
        self.property.delete()
        self.property.refresh_from_db()
        
        self.property.address = "Updated Address"
        self.property.save()
        
        updated_property = Property.objects.get(id=self.property.id)
        self.assertEqual(updated_property.address, "Updated Address")
        self.assertTrue(updated_property.is_deleted)
        self.assertIsNotNone(updated_property.deleted_at)

    def test_delete_already_deleted_property(self):
        # First deletion
        first_deleted_at = timezone.now()
        self.property.delete()
        self.property.refresh_from_db()
        
        # Store first deletion timestamp
        original_deleted_at = self.property.deleted_at
        
        # Try second deletion
        self.property.delete()
        self.property.refresh_from_db()
        
        # Verify deletion timestamp hasn't changed
        self.assertEqual(self.property.deleted_at, original_deleted_at)
    
    def test_undo_deletion_on_non_deleted_property(self):
        self.assertFalse(self.property.is_deleted)
        success = self.property.undo_deletion()
        self.property.refresh_from_db()
        
        self.assertFalse(success)
        self.assertFalse(self.property.is_deleted)
        self.assertIsNone(self.property.deleted_at)
