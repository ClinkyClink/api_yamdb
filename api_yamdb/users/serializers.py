from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model

from .models import CustomUser
from reviews.validators import characters_validator, validate_username
from reviews.constants import (
    MAX_USER_LENGHT,
    MAX_EMAIL_LENGHT,
    MAX_CODE_LENGHT
)


User = get_user_model()


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
        validators=[validate_username, characters_validator]
    )

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user_with_email = User.objects.filter(email=email).first()
        user_with_username = User.objects.filter(username=username).first()

        if user_with_email and user_with_username:
            if user_with_email == user_with_username:
                self.existing_user = user_with_email
            else:
                raise serializers.ValidationError(
                    {'email': user_with_email.email,
                     'username': user_with_username.username}
                )
        elif user_with_email:
            raise serializers.ValidationError(
                {'email': 'Эта почта уже зарегистрирована.'}
            )
        elif user_with_username:
            raise serializers.ValidationError(
                {'username': 'Это имя пользователя уже занято.'}
            )

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_USER_LENGHT,
        validators=[characters_validator]
    )
    confirmation_code = serializers.CharField(max_length=MAX_CODE_LENGHT)
