from rest_framework import filters


class TitleFilter(filters.BaseFilterBackend):
    """Кастомный фильтр произведений по полям category, genre, year, name."""

    filter_fields = ('category', 'genre', 'year', 'name')

    def filter_queryset(self, request, queryset, view):
        category = request.query_params.get('category')
        genre = request.query_params.get('genre')
        year = request.query_params.get('year')
        name = request.query_params.get('name')

        if category:
            queryset = queryset.filter(category__slug=category)
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if year:
            queryset = queryset.filter(year=year)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()
