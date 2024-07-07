from django.core.validators import MaxLengthValidator, RegexValidator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import CustomUser
from reviews.validators import characters_validator, validate_username
from reviews.constants import (
    MAX_USER_LENGHT,
    MAX_EMAIL_LENGHT,
    MAX_CODE_LENGHT
)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGHT,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
        error_messages={
            'max_length': 'Email не должен быть длиннее 254 символов.'
        }
    )
    username = serializers.CharField(
        max_length=MAX_USER_LENGHT,
        validators=[
            characters_validator,
            UniqueValidator(queryset=CustomUser.objects.all())
        ]
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
    read_only_fields = ('role',)

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=MAX_EMAIL_LENGHT)
    username = serializers.CharField(
        max_length=MAX_USER_LENGHT,
        validators=[characters_validator, validate_username]
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_USER_LENGHT,
        validators=[characters_validator]
    )
    confirmation_code = serializers.CharField(max_length=MAX_CODE_LENGHT)
