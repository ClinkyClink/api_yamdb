"""Сериализаторы приложения api."""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import Review, Title, Genre, Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализация категорий."""
    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализация жанров."""
    class Meta:
        exclude = ['id']
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализация произведений."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'category',
            'genre',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализация отзывов к публикациям."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(
                title=title,
                author=request.user
            ).exists():
                raise ValidationError(
                    'Можно добавлять только'
                    'один отзыв на произведение'
                )
        return data
