import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / 'static' / 'data'

        with open(data_dir / 'category.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

        with open(data_dir / 'genre.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

        with open(data_dir / 'titles.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    description=row.get('description', ''),
                    category_id=row['category']
                )

        with open(data_dir / 'genre_title.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                except Exception:
                    pass

        self.stdout.write(
            self.style.SUCCESS('✅ Все данные из CSV успешно загружены!')
        )
