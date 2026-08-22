from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address

User = get_user_model()


class UserRegisterSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "phone_number", "password")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "full_name",
            "country",
            "city",
            "street_address",
            "postal_code",
            "is_default",
        )
        read_only_fields = ("id",)


class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_email_verified",
            "addresses",
            "created_at",
        )
        read_only_fields = ("id", "is_email_verified", "created_at")


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data
