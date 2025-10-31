# 📡 Payment Bot API - Документация

## 🚀 Обзор

Payment Bot API предоставляет HTTP интерфейс для интеграции TRC20 платежей в ваши Telegram боты. API работает асинхронно и поддерживает все основные операции с платежами.

## 🔧 Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск API сервера
```bash
./start_api.sh
```

### 3. Проверка работы
```bash
curl http://localhost:8000/health
```

## 📚 Endpoints

### 🏠 Основные

#### `GET /`
Информация о API
```json
{
  "message": "Payment Bot API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": [...]
}
```

#### `GET /health`
Проверка здоровья API
```json
{
  "status": "healthy",
  "payment_system": "active",
  "database": "connected"
}
```

### 💳 Платежи

#### `POST /payment/create`
Создание платежа

**Запрос:**
```json
{
  "user_id": 12345,
  "amount": 100.0,
  "currency": "USDT",
  "description": "Платеж за услуги"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "payment_id": 1,
    "wallet_address": "TYourAddress...",
    "amount": 100.0,
    "currency": "USDT"
  }
}
```

#### `POST /payment/auto`
Настройка автоматического платежа

**Запрос:**
```json
{
  "user_id": 12345,
  "wallet_address": "TYourAddress...",
  "description": "Автоматический платеж"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "wallet_address": "TYourAddress...",
    "auto_mode": true
  }
}
```

#### `GET /payment/status/{user_id}`
Получение статуса платежей

**Параметры:**
- `user_id` (path) - ID пользователя
- `payment_id` (query, optional) - ID конкретного платежа

**Ответ:**
```json
{
  "success": true,
  "data": {
    "pending_payments": [...],
    "confirmed_payments": [...]
  }
}
```

#### `GET /payment/balance/{user_id}`
Получение баланса кошелька

**Ответ:**
```json
{
  "success": true,
  "wallet_address": "TYourAddress...",
  "balance": 150.75,
  "currency": "USDT"
}
```

### 🔔 Callbacks

#### `POST /payment/callback/{user_id}`
Регистрация callback для уведомлений

**Запрос:**
```json
{
  "callback_url": "https://yourbot.com/webhook/payment"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Callback зарегистрирован для пользователя 12345",
  "callback_url": "https://yourbot.com/webhook/payment"
}
```

#### `DELETE /payment/callback/{user_id}`
Отмена регистрации callback

#### `GET /payment/callbacks`
Список зарегистрированных callback'ов

### ℹ️ Информация

#### `GET /payment/info`
Информация о платежной системе

**Ответ:**
```json
{
  "success": true,
  "info": {
    "version": "1.0.0",
    "features": ["TRC20 платежи", "Автоматическое зачисление", ...],
    "supported_currencies": ["USDT"],
    "api_endpoints": [...]
  }
}
```

## 🔌 Интеграция в ваш бот

### Python клиент

```python
import aiohttp
import asyncio

class PaymentClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
    
    async def create_payment(self, user_id, amount, currency="USDT"):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/payment/create",
                json={
                    "user_id": user_id,
                    "amount": amount,
                    "currency": currency
                }
            ) as response:
                return await response.json()

# Использование
async def main():
    client = PaymentClient()
    result = await client.create_payment(12345, 100.0)
    print(result)

asyncio.run(main())
```

### JavaScript клиент

```javascript
class PaymentClient {
    constructor(apiUrl = 'http://localhost:8000') {
        this.apiUrl = apiUrl;
    }
    
    async createPayment(userId, amount, currency = 'USDT') {
        const response = await fetch(`${this.apiUrl}/payment/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                amount: amount,
                currency: currency
            })
        });
        
        return await response.json();
    }
}

// Использование
const client = new PaymentClient();
client.createPayment(12345, 100.0)
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

### cURL примеры

```bash
# Создание платежа
curl -X POST "http://localhost:8000/payment/create" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 12345,
       "amount": 100.0,
       "currency": "USDT",
       "description": "Платеж за услуги"
     }'

# Настройка автоматического платежа
curl -X POST "http://localhost:8000/payment/auto" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 12345,
       "wallet_address": "TYourAddress...",
       "description": "Автоматический платеж"
     }'

# Проверка статуса
curl "http://localhost:8000/payment/status/12345"

# Проверка баланса
curl "http://localhost:8000/payment/balance/12345"
```

## 🔄 Webhook уведомления

### Настройка webhook

1. Зарегистрируйте callback URL:
```bash
curl -X POST "http://localhost:8000/payment/callback/12345" \
     -H "Content-Type: application/json" \
     -d '{"callback_url": "https://yourbot.com/webhook/payment"}'
```

2. Создайте endpoint в вашем боте для получения уведомлений:
```python
@app.post("/webhook/payment")
async def payment_webhook(data: dict):
    user_id = data['user_id']
    amount = data['amount']
    currency = data['currency']
    transaction_hash = data['transaction_hash']
    wallet_address = data['wallet_address']
    
    # Ваша логика обработки платежа
    print(f"Получен платеж: {amount} {currency}")
    
    return {"status": "ok"}
```

### Формат webhook уведомления

```json
{
  "user_id": 12345,
  "amount": 100.0,
  "currency": "USDT",
  "transaction_hash": "0x1234567890abcdef...",
  "wallet_address": "TYourAddress..."
}
```

## 🛡️ Безопасность

### Аутентификация
В текущей версии API не требует аутентификации. Для продакшена рекомендуется добавить:
- API ключи
- JWT токены
- IP whitelist

### Валидация
- Все входные данные валидируются
- Адреса кошельков проверяются на корректность
- Суммы платежей валидируются

## 📊 Мониторинг

### Логи
API логирует все операции. Уровень логирования настраивается в коде.

### Метрики
- Количество запросов
- Время ответа
- Ошибки
- Активные пользователи

### Health check
```bash
curl http://localhost:8000/health
```

## 🚀 Развертывание

### Локальная разработка
```bash
./start_api.sh
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "payment_api.py"]
```

### Nginx конфигурация
```nginx
server {
    listen 80;
    server_name your-api.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Конфигурация

### Переменные окружения
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TRON_API_KEY="your_tron_api_key"
export CHECK_INTERVAL=30
```

### Настройки API
- `host`: 0.0.0.0 (все интерфейсы)
- `port`: 8000
- `reload`: True (автоперезагрузка)

## 📈 Производительность

### Ограничения
- До 1000 запросов в минуту
- До 100 одновременных пользователей
- Размер запроса: до 1MB

### Оптимизация
- Асинхронная обработка
- Кэширование запросов
- Батчинг операций

## 🐛 Отладка

### Логи
```bash
tail -f logs/payment_api.log
```

### Тестирование
```bash
python test_integration.py
```

### Проверка соединения
```bash
curl -v http://localhost:8000/health
```

## 📞 Поддержка

### Документация
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Примеры
- `payment_client.py` - Python клиент
- `example_integration.py` - Пример интеграции
- `test_integration.py` - Тесты

---

**Готово! Теперь ваш бот может работать с платежами через API!** 🎉





