# Payment Ledger API

Асинхронное REST API для тестового backend-задания: пользователи, администраторы, счета и платежный webhook для пополнения баланса.

## Стек

- Python 3.11
- Sanic
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker Compose
- pytest
- ruff

## Что реализовано

- Авторизация пользователя и администратора по email/password.
- JWT access tokens с проверкой роли.
- Получение профиля, счетов и платежей пользователя.
- CRUD пользователей для администратора.
- Список пользователей со счетами для администратора.
- Payment webhook с SHA256-подписью.
- Idempotency по `transaction_id`: повторный webhook не начисляет баланс второй раз.
- Alembic-миграция со стартовым пользователем, счетом и администратором.
- Docker Compose для PostgreSQL и приложения.

## Тестовые аккаунты

Пользователь:

```text
email: user@example.com
password: user12345
```

Администратор:

```text
email: admin@example.com
password: admin12345
```

## Запуск через Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно на:

```text
http://127.0.0.1:8000
```

Контейнер приложения перед стартом API выполняет:

```bash
alembic upgrade head
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
```

Остановка:

```bash
docker compose down
```

Остановка с удалением локальных данных PostgreSQL:

```bash
docker compose down -v
```

## Запуск без Docker

Нужен локальный PostgreSQL и база `payment_ledger`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m app.main
```

На Windows активация окружения:

```powershell
.\.venv\Scripts\activate
```

## Endpoints

```text
GET    /health

POST   /auth/user/login
POST   /auth/admin/login

GET    /users/me
GET    /users/me/accounts
GET    /users/me/payments

GET    /admins/me
GET    /admins/users
POST   /admins/users
PATCH  /admins/users/<user_id:int>
DELETE /admins/users/<user_id:int>

POST   /webhooks/payments
```

## Login example

```bash
curl -X POST http://127.0.0.1:8000/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user12345"}'
```

## Payment webhook

Подпись считается через SHA256 от строки:

```text
{account_id}{amount}{transaction_id}{user_id}{secret_key}
```

Поле `signature` в расчет подписи не входит.

Для Docker Compose используется dev-secret:

```text
dev-webhook-secret-change-me
```

Пример webhook-запроса:

```bash
curl -X POST http://127.0.0.1:8000/webhooks/payments \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "e04d73f97897343c4ea1b864d9ee648eac6b5df1f77444d8c924bdfe898731b7"
  }'
```

Посчитать подпись можно так:

```bash
python -c "import hashlib; print(hashlib.sha256('11005eae174f-7cd0-472c-bd36-35660f00132b1dev-webhook-secret-change-me'.encode()).hexdigest())"
```

Больше готовых запросов лежит в [docs/API.md](docs/API.md).

## Проверка

```bash
python -m ruff format .
python -m ruff check . --fix
python -m compileall app
python -m pytest -q
docker compose config --quiet
```

## Makefile

```bash
make run
make test
make lint
make format
make migrate
```
