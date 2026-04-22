# Birmarket Portfolio Dashboard

Командный дашборд с ролями, комментариями и задачами по партнёрам.

## Роли и логины (по умолчанию)

| Логин    | Пароль      | Роль          | Видит                        |
|----------|-------------|---------------|------------------------------|
| admin    | admin123    | Администратор | Весь портфель                |
| cco      | cco123      | CCO           | Весь портфель + BDM-ы        |
| aslan    | aslan123    | BDM           | Только свой портфель         |
| maya     | maya123     | BDM           | Только свой портфель         |
| movsum   | movsum123   | BDM           | Только свой портфель         |
| zamir    | zamir123    | BDM           | Только свой портфель         |
| ayten    | ayten123    | BDM           | Только свой портфель         |

---

## Деплой на Railway (бесплатно, 5 минут)

### Шаг 1 — Загрузите код на GitHub

1. Зайдите на [github.com](https://github.com) и создайте аккаунт (если нет)
2. Нажмите **New repository** → назовите `birmarket-dashboard` → Create
3. Загрузите все файлы этой папки в репозиторий

### Шаг 2 — Деплой на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **Start a New Project**
3. Выберите **Deploy from GitHub repo**
4. Выберите `birmarket-dashboard`
5. Railway автоматически запустит приложение (1-2 минуты)
6. Нажмите **Generate Domain** — получите ссылку вида `birmarket-xxx.railway.app`

**Готово!** Поделитесь ссылкой с командой.

---

## Локальный запуск (для разработчика)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Откройте http://localhost:8000

---

## Смена паролей

Откройте `backend/main.py`, найдите список `users` и измените пароли:

```python
users = [
    ("admin", pw("ВАШ_НОВЫЙ_ПАРОЛЬ"), "admin", None),
    ...
]
```

Затем удалите файл `birmarket.db` и перезапустите — база пересоздастся с новыми паролями.

---

## Структура файлов

```
birmarket-dashboard/
├── backend/
│   ├── main.py          # FastAPI сервер + API
│   └── requirements.txt # Python зависимости
├── frontend/
│   └── index.html       # Весь фронтенд (один файл)
├── Procfile             # Railway конфиг запуска
├── railway.json         # Railway настройки
└── README.md            # Эта инструкция
```
