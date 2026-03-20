import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр произведений по category, genre, year и name."""

    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year', 'name')
