from rest_framework import serializers
from django.core.validators import RegexValidator, MaxLengthValidator

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        error_messages={
            'max_length': 'Email не должен быть длиннее 254 символов.'
        }
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Username может содержать только буквы,'
                         ' числа, и @/./+/-/_ символы.')
            ),
            MaxLengthValidator(
                150, message='Username не должен быть длиннее 150 символов.')
        ]
    )
    first_name = serializers.CharField(
        max_length=150,
        error_messages={
            'max_length': 'Имя не должно быть длиннее 150 символов.'
        },
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        error_messages={
            'max_length': 'Фамилия не должна быть длиннее 150 символов.'
        },
        allow_blank=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'bio',
            'role'
        )


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Username может содержать только буквы,'
                         ' числа, и @/./+/-/_ символы.')
            )
        ]
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Username 'me' is not allowed.")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Username может содержать только буквы,'
                         ' числа, и @/./+/-/_ символы.')
            )
        ]
    )
    confirmation_code = serializers.CharField(max_length=50)
