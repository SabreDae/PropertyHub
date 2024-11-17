from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from datetime import datetime, timedelta

from ..models import Property

User = get_user_model()


class PropertyViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@mail.com", username="admin", password="admin123"
        )

        # Create test property
        self.property = Property.objects.create(
            address="123 Test St",
            post_code="TE1 1ST",
            city="Test City",
            number_of_rooms=3,
            created_by=self.user1,
        )

        # Set up API client
        self.client.force_authenticate(user=self.user1)

    def test_list_properties(self):
        response = self.client.get(reverse("property-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_property(self):
        data = {
            "address": "456 New St",
            "post_code": "NE2 2ND",
            "city": "New City",
            "number_of_rooms": 4,
        }
        response = self.client.post(reverse("property-list-create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 2)

    def test_create_property_with_invalid_data(self):
        data = {"address": ""}
        response = self.client.post(reverse("property-list-create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_property_missing_required_fields(self):
        response = self.client.post(
            reverse("property-list-create"),
            {"address": "123 Test St"},  # Missing other required fields
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_property(self):
        response = self.client.get(
            reverse("property-detail", kwargs={"pk": self.property.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["address"], "123 Test St")

    def test_update_property_partial_fields(self):
        original_address = self.property.address
        response = self.client.patch(
            reverse("property-detail", kwargs={"pk": self.property.pk}),
            {"number_of_rooms": 4},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.address, original_address)
        self.assertEqual(self.property.number_of_rooms, 4)

    def test_update_property_invalid_rooms(self):
        response = self.client.patch(
            reverse("property-detail", kwargs={"pk": self.property.pk}),
            {"number_of_rooms": -1},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_property(self):
        response = self.client.delete(
            reverse("property-detail", kwargs={"pk": self.property.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.property.refresh_from_db()
        self.assertTrue(self.property.is_deleted)

    def test_recover_property(self):
        # First delete the property
        self.property.delete()

        response = self.client.post(
            reverse("property-recover", kwargs={"pk": self.property.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertFalse(self.property.is_deleted)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=self.user2)

        # Try to update
        response = self.client.patch(
            reverse("property-detail", kwargs={"pk": self.property.pk}),
            {"address": "Unauthorized Change"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete
        response = self.client.delete(
            reverse("property-detail", kwargs={"pk": self.property.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_deleted_property(self):
        self.property.delete()
        response = self.client.patch(
            reverse("property-detail", kwargs={"pk": self.property.pk}),
            {"address": "New Address"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recover_non_deleted_property(self):
        response = self.client.post(
            reverse("property-recover", kwargs={"pk": self.property.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_access(self):
        self.client.force_authenticate(user=self.admin_user)

        # Admin should be able to update any property
        response = self.client.patch(
            reverse("property-detail", kwargs={"pk": self.property.pk}),
            {"address": "Admin Change"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_only_active_properties(self):
        Property.objects.create(
            address="Delete Me",
            post_code="DE1 ETE",
            city="Delete City",
            number_of_rooms=1,
            created_by=self.user1,
            is_deleted=True,
        )

        response = self.client.get(reverse("property-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the non-deleted property
