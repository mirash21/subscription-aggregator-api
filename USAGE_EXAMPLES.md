# 📚 Примеры использования API

## 🚀 Быстрые примеры

### 1. Создание подписки

```bash
curl -X POST "http://localhost:8000/subscriptions/" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "Yandex Plus",
    "price": 400,
    "user_id": "60601fee-2bf1-4721-ae6f-7636e79a0cba",
    "start_date": "07-2025"
  }'
```

**Ответ:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_name": "Yandex Plus",
  "price": 400,
  "user_id": "60601fee-2bf1-4721-ae6f-7636e79a0cba",
  "start_date": "07-2025",
  "end_date": null,
  "created_at": "2026-02-26T15:30:00",
  "updated_at": "2026-02-26T15:30:00"
}
```

### 2. Получение подписки по ID

```bash
curl -X GET "http://localhost:8000/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### 3. Обновление подписки

```bash
curl -X PUT "http://localhost:8000/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 450,
    "end_date": "07-2026"
  }'
```

### 4. Удаление подписки

```bash
curl -X DELETE "http://localhost:8000/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### 5. Список подписок с фильтрацией

```bash
# Все подписки пользователя
curl -X GET "http://localhost:8000/subscriptions/?user_id=60601fee-2bf1-4721-ae6f-7636e79a0cba"

# Подписки с пагинацией
curl -X GET "http://localhost:8000/subscriptions/?skip=0&limit=10"

# Поиск по названию сервиса
curl -X GET "http://localhost:8000/subscriptions/?service_name=yandex"
```

### 6. Расчет суммарной стоимости

```bash
# Общая стоимость за 2025 год
curl -X GET "http://localhost:8000/subscriptions/cost/?start_period=01-2025&end_period=12-2025"

# Стоимость для конкретного пользователя
curl -X GET "http://localhost:8000/subscriptions/cost/?start_period=01-2025&end_period=12-2025&user_id=60601fee-2bf1-4721-ae6f-7636e79a0cba"

# Стоимость конкретного сервиса
curl -X GET "http://localhost:8000/subscriptions/cost/?start_period=01-2025&end_period=12-2025&service_name=Netflix"
```

**Ответ расчета стоимости:**
```json
{
  "total_cost": 2400,
  "period_start": "01-2025",
  "period_end": "12-2025",
  "count": 3
}
```

## 🐍 Примеры на Python

### Использование requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Создание подписки
subscription_data = {
    "service_name": "Spotify Premium",
    "price": 200,
    "user_id": "60601fee-2bf1-4721-ae6f-7636e79a0cba",
    "start_date": "03-2025"
}

response = requests.post(f"{BASE_URL}/subscriptions/", json=subscription_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Расчет стоимости
params = {
    "start_period": "01-2025",
    "end_period": "12-2025"
}

response = requests.get(f"{BASE_URL}/subscriptions/cost/", params=params)
cost_data = response.json()
print(f"Total cost: {cost_data['total_cost']} RUB")
print(f"Subscriptions count: {cost_data['count']}")
```

### Использование httpx (асинхронно)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Создание подписки
        subscription_data = {
            "service_name": "Apple Music",
            "price": 150,
            "user_id": "60601fee-2bf1-4721-ae6f-7636e79a0cba",
            "start_date": "05-2025"
        }
        
        response = await client.post(
            "http://localhost:8000/subscriptions/",
            json=subscription_data
        )
        print(response.json())

asyncio.run(main())
```

## 🛠️ Примеры с использованием Swagger UI

1. Откройте `http://localhost:8000/docs`
2. Выберите нужный endpoint
3. Нажмите "Try it out"
4. Введите параметры
5. Нажмите "Execute"

## 🧪 Тестирование

### Запуск автоматических тестов

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с подробным выводом
pytest tests/ -v -s

# Запуск конкретного теста
pytest tests/test_subscriptions.py::test_create_subscription -v
```

### Интерактивное тестирование

```bash
python run_local_test.py
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# База данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=subscription_db
DB_USER=postgres
DB_PASSWORD=postgres

# Приложение
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Логирование
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 📊 Мониторинг

### Health check

```bash
curl -X GET "http://localhost:8000/health"
```

**Ответ:**
```json
{
  "status": "healthy"
}
```

## 🔐 Валидация данных

### Форматы данных

- **Дата**: `MM-YYYY` (например: "07-2025")
- **Цена**: целое число рублей (без копеек)
- **User ID**: UUID формат
- **Название сервиса**: строка 1-255 символов

### Примеры валидации

```json
// ❌ Неверный формат даты
{
  "start_date": "2025-07"  // Должно быть "07-2025"
}

// ❌ Отрицательная цена
{
  "price": -100  // Должно быть > 0
}

// ❌ Неверный UUID
{
  "user_id": "invalid-uuid"  // Должен быть валидный UUID
}
```