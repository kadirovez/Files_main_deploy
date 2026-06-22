# HMChat — Web Chat с WebSocket

One-to-one чат поверх существующей системы регистрации и логина с JWT-сессиями.

## Возможности

- Регистрация и вход через многошаговый auth API
- Главная страница чата: слева дашборд с диалогами, по центру переписка
- Только личные чаты 1-на-1 (без групп)
- Создание чата по username — чат появляется у обоих пользователей
- Сообщения сохраняются в PostgreSQL, доставляются офлайн-пользователям
- WebSocket для real-time сообщений и статуса онлайн/офлайн
- Анимации UI (fade-in, slide-in)

## Стек

- **Backend:** FastAPI, SQLAlchemy (async), PostgreSQL, WebSocket, JWT
- **Frontend:** HTML, CSS, JavaScript (vanilla)

## Требования

- Python 3.12+
- PostgreSQL 14+
- Созданная база данных (по умолчанию `hmchat`)

## Установка

```bash
# 1. Клонировать / перейти в проект
cd /path/to/files

# 2. Создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить окружение
cp .env.example .env   # или создайте .env вручную
```

### Пример `.env`

```env
DATABASE_ENGINE=postgresql+psycopg
DATABASE_IP=localhost
DATABASE_PORT=5432
DATABASE_NAME=hmchat
DATABASE_USERNAME=your_user
DATABASE_PASSWORD=your_password

SECRET_KEY=your-secret-key-change-me
DEBUG=true
IP_CHECK_ENABLED=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Совет:** для локальной разработки установите `IP_CHECK_ENABLED=false`, чтобы JWT не привязывался к IP (удобно при переподключении WebSocket).

### База данных

```bash
# Создайте БД в PostgreSQL
createdb hmchat

# Таблицы создаются автоматически при первом запуске (init_db)
```

## Запуск

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте в браузере: **http://localhost:8000**

## Использование

### 1. Регистрация

1. Откройте http://localhost:8000
2. Вкладка **Регистрация** → заполните данные
3. OTP-код выводится **в консоль сервера** (email в dev-режиме не отправляется)
4. Задайте пароль (мин. 10 символов, цифры, спецсимволы)
5. После регистрации перейдите на вкладку **Вход**

### 2. Вход

1. Введите username или email
2. Для входа по username — подтвердите email
3. Введите пароль
4. Введите OTP из консоли сервера
5. Вы попадёте на страницу чата `/chat`

### 3. Чат

- **Слева:** список диалогов с последним сообщением и статусом собеседника
- **Создать чат:** введите username другого пользователя и нажмите `+`
- **Центр:** переписка в стиле Telegram
- Сообщения доставляются в реальном времени через WebSocket
- Если собеседник офлайн — сообщения сохраняются и загрузятся при следующем входе

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/me/` | Текущий пользователь |
| GET | `/api/v1/chats/` | Список чатов |
| POST | `/api/v1/chats/` | Создать чат `{"username": "..."}` |
| GET | `/api/v1/chats/{id}/messages` | История сообщений |
| POST | `/api/v1/chats/{id}/messages` | Отправить сообщение (REST) |
| WS | `/ws?token=JWT` | WebSocket чат |

Документация API (debug): http://localhost:8000/docs

## Архитектура

```
backend/
├── api/           # REST + WebSocket endpoints
├── crud/          # Операции с БД
├── services/      # Бизнес-логика
├── models/        # SQLAlchemy модели
├── schemas/       # Pydantic схемы
└── deps/          # FastAPI dependencies (auth, user)

frontend/
├── templates/     # HTML страницы
└── static/        # CSS, JS
```

## WebSocket события

**Клиент → сервер:**
```json
{"type": "message", "chat_id": 1, "text": "Привет!"}
```

**Сервер → клиент:**
```json
{"type": "message", "message": {...}}
{"type": "new_chat", "chat": {...}}
{"type": "chat_updated", "chat": {...}}
{"type": "presence", "online_user_ids": [1, 2]}
```

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Ошибка подключения к БД | Проверьте `.env` и что PostgreSQL запущен |
| 401 на WebSocket | Проверьте JWT, попробуйте `IP_CHECK_ENABLED=false` |
| OTP не приходит | Смотрите консоль uvicorn — код печатается там |
| Таблицы не созданы | Убедитесь, что БД существует и пользователь имеет права |
