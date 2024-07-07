from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.validators import characters_validator, validate_username
from reviews.constants import (
    MAX_USER_LENGHT,
    MAX_EMAIL_LENGHT,
    MAX_ROLE_LENGHT
)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USER_LENGHT,
        unique=True,
        help_text='Обязательное поле, не может быть пустым.',
        validators=[characters_validator, validate_username],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGHT,
        unique=True,
        help_text='Обязательное поле, не может быть пустым.'
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_USER_LENGHT,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_USER_LENGHT,
        blank=True
    )
    bio = models.TextField('Биография', blank=True, null=True)
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    role = models.CharField(
        verbose_name='Роль',
        max_length=MAX_ROLE_LENGHT,
        choices=ROLE_CHOICES,
        default=USER,
        help_text=(
            'Администратор, модератор или пользователь.'
            ' По умолчанию Пользователь.'
        )
    )

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    def save(self, *args, **kwargs):
        if not self.username and not self.email:
            raise ValueError(
                'Должно быть установлено имя пользователя и email.'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username
