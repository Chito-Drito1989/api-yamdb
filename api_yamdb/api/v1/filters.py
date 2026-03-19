try:
    import django_filters
except ModuleNotFoundError:  # pragma: no cover - fallback for offline envs
    django_filters = None

from reviews.models import Title


if django_filters:
    class TitleFilter(django_filters.FilterSet):
        """Фильтр произведений по category, genre, year и name."""

        category = django_filters.CharFilter(field_name='category__slug')
        genre = django_filters.CharFilter(field_name='genre__slug')
        year = django_filters.NumberFilter(field_name='year')
        name = django_filters.CharFilter(
            field_name='name',
            lookup_expr='icontains',
        )

        class Meta:
            model = Title
            fields = ('category', 'genre', 'year', 'name')
else:
    class TitleFilter:
        """Fallback-фильтр, если пакет django-filter недоступен."""

        @staticmethod
        def apply(params, queryset):
            category = params.get('category')
            genre = params.get('genre')
            year = params.get('year')
            name = params.get('name')

            if category:
                queryset = queryset.filter(category__slug=category)
            if genre:
                queryset = queryset.filter(genre__slug=genre)
            if year:
                try:
                    queryset = queryset.filter(year=int(year))
                except (TypeError, ValueError):
                    pass
            if name:
                queryset = queryset.filter(name__icontains=name)
            return queryset.distinct()
