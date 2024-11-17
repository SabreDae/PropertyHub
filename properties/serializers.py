import logging
import re

from rest_framework import serializers
from typing import Any, Dict

from .models import Property


logger = logging.getLogger(__name__)


class PropertySerializer(serializers.ModelSerializer):
    """
    Serializer for Property model.

    Handles the serialization and deserialization of Property instances,
    including validation of input data and proper handling of read-only fields.

    Fields:
        id: Read-only property ID
        address: Property street address
        post_code: Property postal code
        city: Property city
        number_of_rooms: Number of rooms in the property
        created_by: Read-only reference to creating user
        is_deleted: Read-only deletion status
        deleted_at: Read-only deletion timestamp
        created_at: Read-only creation timestamp
        updated_at: Read-only update timestamp

    Validation:
        - Ensures all required fields are provided
        - Validates post_code format
        - Ensures number_of_rooms is positive
    """
    class Meta:
        model = Property
        fields = ["id", "address", "post_code", "city", "number_of_rooms", "created_by", "updated_at", "created_at", "is_deleted", "deleted_at"]
        read_only_fields = ["created_by", "deleted_at", "updated_at", "created_at"]    
    
    def validate_address(self, value: str) -> str:
        if not value or not value.strip():
            logger.warning("Empty address submitted")
            raise serializers.ValidationError("Please enter a property address")
        # Remove leading/trailing whitespace and reduce multiple spaces to single
        cleaned_address = ' '.join(value.split())
        return cleaned_address

    def validate_city(self, value: str) -> str:
        if not value or not value.strip():
            logger.warning("Empty city submitted")
            raise serializers.ValidationError("Please enter a city")
        cleaned_city = ' '.join(value.split())
        return cleaned_city
    
    def validate_post_code(self, value: str) -> str:
        cleaned_code = value.strip().upper()
        if not cleaned_code:
            logger.warning("Empty post code submitted")
            raise serializers.ValidationError("Please enter a valid post code")
        
        cleaned_code = ''.join(cleaned_code.split()) 
        if len(cleaned_code) < 5: 
            logger.warning(f"Post code too short: {cleaned_code}")
            raise serializers.ValidationError("Please enter a valid post code format")
        
        cleaned_code = f"{cleaned_code[:-3]} {cleaned_code[-3:]}"
        
        post_code_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'
        if not re.match(post_code_pattern, cleaned_code):
            logger.warning(f"Invalid post code format: {cleaned_code}")
            raise serializers.ValidationError("Please enter a valid post code format")
        return cleaned_code
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get('number_of_rooms') is not None and data.get('number_of_rooms') <= 0:
            raise serializers.ValidationError({
                'number_of_rooms': "Number of rooms must be greater than zero"
            })

        return data

    def to_representation(self, instance: Property) -> Dict[str, Any]:
        try: 
            representation = super().to_representation(instance)
            if not self.context["request"].user.is_staff:
                # Ensure that non-admin users will not see the created_by details
                representation.pop("created_by", None)
            return representation
        except KeyError:
            logger.warning("Request not found in serializer context")
