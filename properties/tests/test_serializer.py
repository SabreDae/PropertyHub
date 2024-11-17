from django.contrib.auth import get_user_model
from django.test import TestCase

from ..serializers import PropertySerializer


TEST_USER = get_user_model()

class PropertySerializerTests(TestCase):
    def setUp(self):
        self.user = TEST_USER.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.property_data = {
            "address": "123 Test St",
            "post_code": "AB12 3CD",
            "city": "Test City",
            "number_of_rooms": 3,
            "created_by": self.user.id
        }

    def test_valid_serializer(self):
        serializer = PropertySerializer(data=self.property_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_empty_address(self):
        self.property_data["address"] = ""
        serializer = PropertySerializer(data=self.property_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("address", serializer.errors)

    def test_invalid_number_of_rooms(self):
        self.property_data["number_of_rooms"] = 0
        serializer = PropertySerializer(data=self.property_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("number_of_rooms", serializer.errors)

    def test_serializer_strips_whitespace(self):
        self.property_data["address"] = "  123 Test St  "
        serializer = PropertySerializer(data=self.property_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["address"], "123 Test St")

    def test_create_property_with_invalid_post_code(self):
        invalid_post_codes = [
            "12345",  # Wrong format
            "ABC DEF",  # No numbers
            "A1 1",  # Too short
            "AB12 3CDEF"  # Too long
        ]
        
        for post_code in invalid_post_codes:
            self.property_data["post_code"] = post_code
            serializer = PropertySerializer(data=self.property_data)
            self.assertFalse(
                serializer.is_valid(),
                f"Post code {post_code} should be invalid"
            )
            self.assertIn("post_code", serializer.errors)
    
    def test_create_property_with_special_characters(self):
        special_chars_data = {
            "address": "123 Test St #@$%",
            "city": "Test City-Upon-Sea",
            "post_code": "AB12 3CD"
        }
        
        serializer = PropertySerializer(data={
            **self.property_data,
            **special_chars_data
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["address"],
            special_chars_data["address"]
        )
        self.assertEqual(
            serializer.validated_data["city"],
            special_chars_data["city"]
        )

    def test_whitespace_handling(self):
        whitespace_data = {
            "address": "  123   Test   St  ",
            "city": "  Test   City  ",
            "post_code": "  AB12   3CD  "
        }
        
        serializer = PropertySerializer(data={
            **self.property_data,
            **whitespace_data
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["address"].strip(),
            "123 Test St"
        )
        self.assertEqual(
            serializer.validated_data["city"].strip(),
            "Test City"
        )
        self.assertEqual(
            serializer.validated_data["post_code"].strip(),
            "AB12 3CD"
        )

    def test_empty_fields(self):
        required_fields = ["address", "post_code", "city"]
        
        for field in required_fields:
            data = self.property_data.copy()
            data[field] = ""
            serializer = PropertySerializer(data=data)
            self.assertFalse(
                serializer.is_valid(),
                f"Empty {field} should be invalid"
            )
            self.assertIn(field, serializer.errors)

    def test_none_values(self):
        nullable_fields = ["number_of_rooms"]
        non_nullable_fields = ["address", "post_code", "city"]
        
        # Test nullable fields
        for field in nullable_fields:
            data = self.property_data.copy()
            data[field] = None
            serializer = PropertySerializer(data=data)
            self.assertTrue(
                serializer.is_valid(),
                f"None value for {field} should be valid"
            )
        
        # Test non-nullable fields
        for field in non_nullable_fields:
            data = self.property_data.copy()
            data[field] = None
            serializer = PropertySerializer(data=data)
            self.assertFalse(
                serializer.is_valid(),
                f"None value for {field} should be invalid"
            )
            self.assertIn(field, serializer.errors)

