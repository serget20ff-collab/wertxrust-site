# WertxRust Site

<<<<<<< HEAD
Django-платформа для проекта игровых серверов Rust **WertxRust**.

Главный принцип архитектуры: **Steam ID является центральным идентификатором игрока**. Все покупки, права, статистика, входы, заметки админов, будущие Discord-связки и серверные данные должны быть привязаны к `SteamProfile.steam_id`.

## Локальный запуск

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
=======
Django-платформа для проекта WertxRust.

Главная идея архитектуры: **Steam ID — центральный идентификатор игрока**. Все будущие данные игрока, покупки, роли, серверная статистика и действия в админке должны привязываться к единой таблице профилей Steam.

## Стек

- Python 3.12
- Django 5.x
- PostgreSQL
- Django Templates
- Tailwind-подобная CSS-структура без сборщика на старте
- Docker Compose

## Основные приложения

- `accounts` — Steam-профили и пользователи проекта
- `core` — главная, настройки проекта, базовые страницы
- `servers` — игровые серверы, онлайн, вайпы
- `shop` — товары, привилегии, заказы
- `news` — новости и анонсы
- `rules` — правила сервера, Discord и магазина

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
>>>>>>> ef57d6502a638dacbef4c9b431d73d8a9c4ba20a
python manage.py createsuperuser
python manage.py runserver
```

<<<<<<< HEAD
URL: `/`, `/admin/`, `/auth/steam/login/`, `/servers/`, `/shop/`, `/rules/`, `/news/`.

## Steam

Прод:
```env
SITE_URL=https://wertxrust.ru
STEAM_RETURN_URL=https://wertxrust.ru/auth/steam/callback/
STEAM_REALM=https://wertxrust.ru/
STEAM_API_KEY=твой_ключ
```
=======
## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Важные URL

- `/` — главная
- `/admin/` — Django Admin
- `/servers/` — серверы
- `/shop/` — магазин
- `/rules/` — правила
- `/news/` — новости
>>>>>>> ef57d6502a638dacbef4c9b431d73d8a9c4ba20a
