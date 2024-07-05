from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug', lookup_expr='exact')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
