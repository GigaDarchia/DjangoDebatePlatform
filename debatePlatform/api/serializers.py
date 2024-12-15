from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from user.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer class for handling user registration.

    This serializer is used for creating a new User instance. It includes validation
    for ensuring password consistency, email uniqueness, and username uniqueness.

    :ivar username: Field for the username of the user, limited to 100 characters.
    :type username: serializers.CharField
    :ivar email: Field for the email address of the user.
    :type email: serializers.EmailField
    :ivar password: Field for the user's password.
    :type password: serializers.CharField
    :ivar confirm_password: Field to confirm the password during registration
        (write-only).
    :type confirm_password: serializers.CharField
    """
    username = serializers.CharField(
        max_length=100,
        error_messages={
            'required': _('Username field is required.')
        }
    )
    email = serializers.EmailField(
        error_messages={
            'required': _('Email field is required.')
        }
    )
    password = serializers.CharField(
        error_messages={
            'required': _('Password field is required.')
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('Confirm Password field is required.')
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {
                    "password": _("Passwords do not match.")
                }
            )

        validate_password(data['password'])

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {
                    "email": _("Email already exists.")
                }
            )

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {
                    "username": _("Username already exists.")
                }
            )
        data.pop('confirm_password', None)
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login information.

    This serializer is responsible for validating and handling user login
    credentials, specifically the username and password provided by the user
    during authentication.

    :ivar username: The unique identifier for the user.
    :type username: serializers.CharField
    :ivar password: The password corresponding to the username.
    :type password: serializers.CharField
    """
    username = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(required=True, write_only=True)
