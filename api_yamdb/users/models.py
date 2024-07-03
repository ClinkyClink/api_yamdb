from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text='Не является обязательным, но не может быть пустым.',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=('Имя пользователя должно состоять из букв,'
                         ' цифр и символов: @/./+/-/_'),
                code='invalid_username'
            ),
        ],
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        help_text='Не является обязательным, но не может быть пустым.'
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
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
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        help_text=(
            'Администратор, модератор или пользователь.'
            ' По умолчанию Пользователь.'
        )
    )

    def save(self, *args, **kwargs):
        if not self.username and not self.email:
            raise ValueError(
                "Должно быть установлено либо имя пользователя, либо email."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username
