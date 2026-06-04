# API Requests

Примеры рассчитаны на запуск после:

```bash
docker compose up --build
```

Базовый адрес:

```bash
BASE_URL=http://127.0.0.1:8000
```

## Healthcheck

```bash
curl "$BASE_URL/health"
```

## Login User

```bash
USER_TOKEN=$(curl -s -X POST "$BASE_URL/auth/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user12345"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

## Login Admin

```bash
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin12345"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

## Current User

```bash
curl "$BASE_URL/users/me" \
  -H "Authorization: Bearer $USER_TOKEN"
```

## User Accounts

```bash
curl "$BASE_URL/users/me/accounts" \
  -H "Authorization: Bearer $USER_TOKEN"
```

## User Payments

```bash
curl "$BASE_URL/users/me/payments" \
  -H "Authorization: Bearer $USER_TOKEN"
```

## Current Admin

```bash
curl "$BASE_URL/admins/me" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Admin List Users

```bash
curl "$BASE_URL/admins/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Admin Create User

На чистой базе этот пользователь получит `id = 2`.

```bash
curl -X POST "$BASE_URL/admins/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "created-by-admin@example.com",
    "password": "created12345",
    "full_name": "Created By Admin"
  }'
```

## Admin Update User

Route:

```text
PATCH /admins/users/<user_id:int>
```

```bash
curl -X PATCH "$BASE_URL/admins/users/2" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated-by-admin@example.com",
    "full_name": "Updated By Admin",
    "password": "updated12345"
  }'
```

## Admin Delete User

Route:

```text
DELETE /admins/users/<user_id:int>
```

```bash
curl -X DELETE "$BASE_URL/admins/users/2" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Payment Webhook

Для Docker Compose используется:

```text
WEBHOOK_SECRET_KEY=dev-webhook-secret-change-me
```

Подписываем строку:

```text
1100curl-payment-0011dev-webhook-secret-change-me
```

Где:

- `1` - account_id;
- `100` - amount;
- `curl-payment-001` - transaction_id;
- `1` - user_id;
- `dev-webhook-secret-change-me` - secret key.

```bash
curl -X POST "$BASE_URL/webhooks/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "curl-payment-001",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "b6144d8b31adc437c90ddb62be37f9553a5c1fde1b850502a90234052e44953f"
  }'
```

## Repeat Payment Webhook

Повтор этого же запроса должен вернуть `already_processed`, а баланс не должен увеличиться второй раз.

```bash
curl -X POST "$BASE_URL/webhooks/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "curl-payment-001",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "b6144d8b31adc437c90ddb62be37f9553a5c1fde1b850502a90234052e44953f"
  }'
```

## Invalid Signature

```bash
curl -X POST "$BASE_URL/webhooks/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "curl-payment-invalid-signature",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "wrong-signature"
  }'
```
