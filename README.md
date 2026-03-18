# API YaMDb

## Описание проекта

Проект YaMDb собирает отзывы пользователей на произведения (фильмы, книги, музыку). Сами произведения в сервисе не хранятся — только метаданные, категории, жанры, оценки и текстовые отзывы с комментариями.

## Стек технологий

- Python 3.9+
- Django 5.1
- Django REST Framework 3.15
- djangorestframework-simplejwt (JWT)
- SQLite (по умолчанию)

## Установка и запуск

```bash
git clone <url-репозитория>
cd api-yamdb/api_yamdb
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

Базовый URL API: `http://127.0.0.1:8000/api/v1/`

## Наполнение БД из CSV

CSV-файлы размещаются в каталоге `api_yamdb/static/data/` (например: `category.csv`, `genre.csv`, `titles.csv` и т.д.).

После миграций выполните:

```bash
python manage.py import_csv
```

Команда импортирует данные из указанных файлов в соответствующие модели.

## Документация API

После запуска сервера: **http://127.0.0.1:8000/redoc/**

## Примеры запросов

**Регистрация**

`POST /api/v1/auth/signup/`

```json
{"email": "user@example.com", "username": "user1"}
```

Ответ `200`: в письме (папка `sent_emails/`) — код подтверждения.

**Получение JWT**

`POST /api/v1/auth/token/`

```json
{"username": "user1", "confirmation_code": "<код из письма>"}
```

Ответ: `{"token": "eyJ..."}`

**Список произведений с фильтрами**

`GET /api/v1/titles/?category=movies&genre=drama&year=2020&name=книга`

## Авторство

Проект выполнен в рамках учебного курса.

- Тимлид: Nazar Tomaily
- Разработчики: Илья Абакунчик (User, Auth), Вадим Гусейнов (Titles, Categories, Genres), Nazar Tomaily (Reviews, Comments, Rating)
