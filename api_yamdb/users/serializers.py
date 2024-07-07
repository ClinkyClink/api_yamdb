from django.core.validators import MaxLengthValidator, RegexValidator

from rest_framework import serializers

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
