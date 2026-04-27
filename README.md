# WertxRust Site

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
python manage.py createsuperuser
python manage.py runserver
```

URL: `/`, `/admin/`, `/auth/steam/login/`, `/servers/`, `/shop/`, `/rules/`, `/news/`.

## Steam

Прод:
```env
SITE_URL=https://wertxrust.ru
STEAM_RETURN_URL=https://wertxrust.ru/auth/steam/callback/
STEAM_REALM=https://wertxrust.ru/
STEAM_API_KEY=твой_ключ
```
