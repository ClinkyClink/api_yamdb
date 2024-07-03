"""Кастомные валидаторы."""

from django.core.validators import RegexValidator


characters_validator = RegexValidator(
    regex = r'^[-a-zA-Z0-9_]+$',
    message = 'Символы латинского алфавита, цифры и знак подчёркивания'
)