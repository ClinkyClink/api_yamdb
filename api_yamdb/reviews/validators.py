"""Кастомные валидаторы."""

from django.utils import timezone

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


characters_validator = RegexValidator(
    regex = r'^[-a-zA-Z0-9_]+$',
    message = 'Символы латинского алфавита, цифры и знак подчёркивания'
)

def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Год произведения не может быть больше текущего.'
        )