from rest_framework import filters


class TitleFilter(filters.BaseFilterBackend):
    """
    Кастомный фильтр произведений.
    Поля query-параметров: category, genre, year, name.
    """

    FILTER_PARAM_TO_LOOKUP = {
        'category': ('category__slug', 'exact'),
        'genre': ('genre__slug', 'exact'),
        'year': ('year', 'exact'),
        'name': ('name', 'icontains'),
    }

    def filter_queryset(self, request, queryset, view):
        for param, (lookup, kind) in self.FILTER_PARAM_TO_LOOKUP.items():
            value = request.query_params.get(param)
            if value is None or value == '':
                continue
            if kind == 'exact':
                queryset = queryset.filter(**{lookup: value})
            else:
                queryset = queryset.filter(**{f'{lookup}__icontains': value})
        return queryset.distinct()
