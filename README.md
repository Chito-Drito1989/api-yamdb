# API YaMDb

Сервис отзывов на произведения (фильмы, книги, музыку). Запросы к API начинаются с префикса **`/api/v1/`**.

Полная спецификация: откройте после запуска проекта **http://127.0.0.1:8000/redoc/** (описание схем, коды ответов, примеры тел запросов).

## Роли и права

| Роль | Возможности |
|------|-------------|
| **Аноним** | Просмотр произведений, отзывов, комментариев |
| **user** | Как аноним + отзывы и оценки (1 отзыв на произведение), комментарии, правка своих отзывов/комментариев |
| **moderator** | Как user + правка и удаление любых отзывов и комментариев |
| **admin** | Управление категориями, жанрами, произведениями, пользователями и ролями |
| **Django superuser** | Права администратора |

## Регистрация и JWT

1. **POST** `/api/v1/auth/signup/` — тело: `email`, `username` (не `me`, пары email/username уникальны). Ответ **200**: `{ "email", "username" }`; код подтверждения уходит на почту (локально — в каталог `sent_emails/`).
2. **POST** `/api/v1/auth/token/` — `username`, `confirmation_code`. Ответ **200**: `{ "token": "<JWT>" }`. **404**, если пользователь не найден; **400** при неверном коде или данных.
3. Заголовок для защищённых методов: `Authorization: Bearer <token>`.
4. **GET/PATCH** `/api/v1/users/me/` — свой профиль (роль через `/me/` не меняется).

Пользователь, созданный админом через **POST** `/api/v1/users/`, письмо с кодом не получает; дальше он сам вызывает **signup** → **token**, как при обычной регистрации.

## Основные эндпоинты (кратко)

- **Категории:** `GET/POST /categories/`, `DELETE /categories/{slug}/` (список с `?search=`), детального GET нет.
- **Жанры:** аналогично `/genres/`.
- **Произведения:** `GET /titles/?category=&genre=&year=&name=`, CRUD по id для админа; в ответе `genre` — массив объектов `{name, slug}`, `category` — объект, `rating` — средняя оценка.
- **Отзывы:** `/titles/{title_id}/reviews/` и `/titles/{title_id}/reviews/{review_id}/`.
- **Комментарии:** `/titles/{title_id}/reviews/{review_id}/comments/` и `.../comments/{comment_id}/`.
- **Пользователи (админ):** `/users/`, `/users/{username}/`.

## Стек

Python 3.9+, Django 5.1, DRF 3.15, SimpleJWT, SQLite.

## Установка

```bash
git clone <url>
cd api-yamdb/api_yamdb
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

## Импорт данных из CSV

Файлы в **`api_yamdb/static/data/`**: `category.csv`, `genre.csv`, `users.csv`, `titles.csv`, `genre_title.csv`, `review.csv`, `comments.csv`.

Порядок загрузки в команде: категории → жанры → пользователи → произведения → связи жанр–произведение → отзывы → комментарии.

```bash
python manage.py import_csv
```

У пользователей из CSV выставляется ненастраиваемый пароль; для входа в API они проходят `/auth/signup/` и `/auth/token/`, как в ТЗ.

## Каскадное удаление (как в ТЗ)

| Удаляется | Поведение |
|-----------|-----------|
| **User** | Каскадом удаляются все его **Review** и **Comment** (`on_delete=CASCADE`). |
| **Title** | Удаляются все **Review** к произведению и **Comment** к этим отзывам. |
| **Review** | Удаляются все **Comment** к отзыву. |
| **Category** | Произведения **не** удаляются; у них `category` становится `NULL` (`SET_NULL`). |
| **Genre** | Произведения **не** удаляются; снимается только связь M2M. |

## Примеры

```http
POST /api/v1/auth/signup/
{"email": "user@example.com", "username": "user1"}

POST /api/v1/auth/token/
{"username": "user1", "confirmation_code": "<из письма>"}

GET /api/v1/titles/?category=films&year=2020
```

## Авторство

Учебный проект. Команда: Nazar Tomaily, Илья Абакунчик, Вадим Гусейнов.
