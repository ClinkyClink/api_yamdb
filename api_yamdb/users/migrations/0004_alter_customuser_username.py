# Generated by Django 3.2 on 2024-07-07 07:52

import django.core.validators
from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'Пользователь с таким именем уже существует.'}, help_text='Обязательное поле, не может быть пустым.', max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Символы латинского алфавита, цифры и знак подчёркивания', regex='^[-a-zA-Z0-9_.@-]+$'), reviews.validators.validate_username]),
        ),
    ]
