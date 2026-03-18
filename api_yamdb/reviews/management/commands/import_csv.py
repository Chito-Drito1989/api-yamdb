"""
Импорт данных из CSV в каталоге static/data/.
Порядок: категории и жанры → пользователи → произведения → связи жанр–title
→ отзывы → комментарии.
"""
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Загрузка данных из CSV (static/data/) в БД'

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / 'static' / 'data'
        self._import_categories(data_dir)
        self._import_genres(data_dir)
        self._import_users(data_dir)
        self._import_titles(data_dir)
        self._import_genre_title(data_dir)
        self._import_reviews(data_dir)
        self._import_comments(data_dir)
        self.stdout.write(self.style.SUCCESS('Импорт из CSV завершён.'))

    def _import_categories(self, data_dir):
        path = data_dir / 'category.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Category.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    },
                )

    def _import_genres(self, data_dir):
        path = data_dir / 'genre.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Genre.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    },
                )

    def _import_users(self, data_dir):
        path = data_dir / 'users.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                uid = int(row['id'])
                defaults = {
                    'username': row['username'],
                    'email': row['email'],
                    'role': row['role'],
                    'bio': row.get('bio') or '',
                    'first_name': row.get('first_name') or '',
                    'last_name': row.get('last_name') or '',
                }
                user, created = User.objects.update_or_create(
                    id=uid,
                    defaults=defaults,
                )
                if created or not user.has_usable_password():
                    user.set_unusable_password()
                    user.save(update_fields=['password'])

    def _import_titles(self, data_dir):
        path = data_dir / 'titles.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                cat = row.get('category') or ''
                category_id = int(cat) if str(cat).strip() else None
                Title.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'year': int(row['year']),
                        'description': row.get('description') or '',
                        'category_id': category_id,
                    },
                )

    def _import_genre_title(self, data_dir):
        path = data_dir / 'genre_title.csv'
        if not path.exists():
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    title = Title.objects.get(id=int(row['title_id']))
                    genre = Genre.objects.get(id=int(row['genre_id']))
                    title.genre.add(genre)
                except (
                    Title.DoesNotExist,
                    Genre.DoesNotExist,
                    ValueError,
                ) as err:
                    self.stderr.write(f'genre_title: {err}')

    def _import_reviews(self, data_dir):
        path = data_dir / 'review.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    rid = int(row['id'])
                    Review.objects.update_or_create(
                        id=rid,
                        defaults={
                            'title_id': int(row['title_id']),
                            'text': row['text'],
                            'author_id': int(row['author']),
                            'score': int(row['score']),
                        },
                    )
                    dt = parse_datetime(row['pub_date'])
                    if dt:
                        Review.objects.filter(pk=rid).update(pub_date=dt)
                except (ValueError, KeyError) as e:
                    self.stderr.write(f'review id={row.get("id")}: {e}')

    def _import_comments(self, data_dir):
        path = data_dir / 'comments.csv'
        if not path.exists():
            self.stderr.write(f'Нет файла: {path}')
            return
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    cid = int(row['id'])
                    Comment.objects.update_or_create(
                        id=cid,
                        defaults={
                            'review_id': int(row['review_id']),
                            'text': row['text'],
                            'author_id': int(row['author']),
                        },
                    )
                    dt = parse_datetime(row['pub_date'])
                    if dt:
                        Comment.objects.filter(pk=cid).update(pub_date=dt)
                except (ValueError, KeyError) as e:
                    self.stderr.write(f'comment id={row.get("id")}: {e}')
