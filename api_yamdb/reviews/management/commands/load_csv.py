import csv
import os
from contextlib import contextmanager

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.db.transaction import atomic

from tqdm import tqdm

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import CustomUser

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'data_type',
            nargs='?',
            choices=['category', 'genre', 'titles', 'users', 'review', 'comments', 'genre_title'],
        )

    @contextmanager
    def open_csv(self, filename):
        path = os.path.join(settings.BASE_DIR, 'static/data/', filename)
        with open(path, 'r', encoding='utf-8') as file:
            yield csv.DictReader(file)

    def add_from_csv(self, model, filename, related_fields=None):
        related_fields = related_fields or {}
        with self.open_csv(filename) as reader:
            with transaction.atomic():
                for row in tqdm(reader, desc=f'Загрузка {filename}'):
                    for field, related_model in related_fields.items():
                        if field in row:
                            related_instance, _ = (
                                related_model.objects
                                .get_or_create(id=row[field]))
                            row[field] = related_instance
                    try:
                        model.objects.get_or_create(**row)
                    except IntegrityError as error:
                        logger.error(f'Ошибка целостности: {error}')
                        raise CommandError(f'Ошибка при импорте данных {error}')

    def handle(self, *args, **options):
        data_types = {
            'category': (Category, 'category.csv', None),
            'genre': (Genre, 'genre.csv', None),
            'titles': (Title, 'titles.csv', {'category': Category}),
            'users': (CustomUser, 'users.csv', None),
            'review': (Review, 'review.csv', {'title': Title, 'author': CustomUser}),
            'comments': (Comment, 'comments.csv', {'review': Review, 'author': CustomUser}),
            'genre_title': (TitleGenre, 'genre_title.csv', {'title': Title, 'genre': Genre}),
        }

        data_type = options['data_type']
        if data_type:
            if data_type in data_types:
                for model, filename, related_fields in data_types.values():
                    if related_fields is None:
                        self.add_from_csv(model, filename)
                    else:
                        self.add_from_csv(model, filename, related_fields)
            else:
                raise CommandError(f'Неизвестный тип данных: {data_type}')
        else:
            for model, filename, related_fields in data_types.values():
                self.add_from_csv(model, filename, related_fields)

        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена'))