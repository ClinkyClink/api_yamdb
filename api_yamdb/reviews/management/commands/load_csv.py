import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from tqdm import tqdm

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import CustomUser


class Command(BaseCommand):
    def add_from_csv(self, model, filename, related_fields=None):
        related_fields = related_fields or {}
        path = os.path.join(settings.BASE_DIR, 'static/data/', filename)
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
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
                    print(f'Произошла ошибка: {error}')

    def add_arguments(self, parser):
        parser.add_argument(
            'data_type',
            nargs='?',
            choices=['category', 'genre', 'titles', 'users',
                     'review', 'comments', 'genre_title'],
        )

    def handle(self, *args, **options):
        try:
            data_type = options['data_type']
            if data_type == 'category':
                self.add_from_csv(Category, 'category.csv')
            elif data_type == 'genre':
                self.add_from_csv(Genre, 'genre.csv')
            elif data_type == 'titles':
                self.add_from_csv(Title, 'titles.csv',
                                  related_fields={'category': Category})
            elif data_type == 'users':
                self.add_from_csv(CustomUser, 'users.csv')
            elif data_type == 'review':
                self.add_from_csv(Review, 'review.csv',
                                  related_fields={'title': Title,
                                                  'author': CustomUser})
            elif data_type == 'comments':
                self.add_from_csv(Comment, 'comments.csv',
                                  related_fields={'review': Review,
                                                  'author': CustomUser})
            elif data_type == 'genre_title':
                self.add_from_csv(TitleGenre, 'genre_title.csv',
                                  related_fields={'title': Title,
                                                  'genre': Genre})
            else:
                self.add_from_csv(Category, 'category.csv')
                self.add_from_csv(Genre, 'genre.csv')
                self.add_from_csv(Title, 'titles.csv',
                                         related_fields={'category': Category})
                self.add_from_csv(CustomUser, 'users.csv')
                self.add_from_csv(Review, 'review.csv',
                                          related_fields={'title': Title,
                                                          'author': CustomUser})
                self.add_from_csv(Comment, 'comments.csv',
                                           related_fields={'review': Review,
                                                           'author': CustomUser})
                self.add_from_csv(TitleGenre, 'genre_title.csv',
                                  related_fields={'title': Title,
                                                  'genre': Genre})
            self.stdout.write(self.style.SUCCESS('Загрузка данных завершена'))
        except Exception as error:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {error}'))
