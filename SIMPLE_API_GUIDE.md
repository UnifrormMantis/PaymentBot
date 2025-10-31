# 🚀 Simple Payment API - Простая интеграция

## 📋 Что это?

Простой API для интеграции TRC20 платежей, как у популярных платежных ботов. **Один API ключ - и все работает!**

## 🎯 Особенности

- ✅ **Простая интеграция** - один API ключ
- ✅ **Автоматическая проверка** платежей
- ✅ **Callback уведомления** при получении платежа
- ✅ **REST API** - работает с любым языком программирования
- ✅ **Автоматическая документация** (Swagger)

## 🚀 Быстрый старт

### 1. Запуск API
```bash
./start_simple_api.sh
```

### 2. Получение API ключа
```bash
curl http://localhost:8001/get-api-key
```

**Ответ:**
```json
{
  "success": true,
  "api_key": "your_api_key_here",
  "message": "API ключ создан успешно"
}
```

### 3. Создание платежа
```bash
curl -X POST http://localhost:8001/create-payment \
     -H "X-API-Key: your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 100.0,
       "currency": "USDT",
       "description": "Платеж за услуги",
       "callback_url": "https://yourbot.com/webhook/payment"
     }'
```

**Ответ:**
```json
{
  "success": true,
  "payment_id": "payment_id_here",
  "wallet_address": "TYourPaymentWallet1234567890123456789012345",
  "amount": 100.0,
  "currency": "USDT",
  "status": "pending"
}
```

### 4. Проверка статуса
```bash
curl -H "X-API-Key: your_api_key_here" \
     http://localhost:8001/check-payment/payment_id_here
```

**Ответ:**
```json
{
  "success": true,
  "payment_id": "payment_id_here",
  "status": "completed",
  "amount": 100.0,
  "currency": "USDT",
  "transaction_hash": "0x1234567890abcdef..."
}
```

## 💻 Примеры интеграции

### Python
```python
import requests

# Получаем API ключ
response = requests.get("http://localhost:8001/get-api-key")
api_key = response.json()['api_key']

# Создаем платеж
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
data = {
    "amount": 100.0,
    "currency": "USDT",
    "description": "Платеж за услуги"
}

response = requests.post(
    "http://localhost:8001/create-payment",
    headers=headers,
    json=data
)

payment = response.json()
print(f"Кошелек: {payment['wallet_address']}")
print(f"Сумма: {payment['amount']} {payment['currency']}")

# Проверяем статус
response = requests.get(
    f"http://localhost:8001/check-payment/{payment['payment_id']}",
    headers=headers
)

status = response.json()
print(f"Статус: {status['status']}")
```

### JavaScript
```javascript
// Получаем API ключ
const apiResponse = await fetch('http://localhost:8001/get-api-key');
const { api_key } = await apiResponse.json();

// Создаем платеж
const paymentResponse = await fetch('http://localhost:8001/create-payment', {
    method: 'POST',
    headers: {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        amount: 100.0,
        currency: 'USDT',
        description: 'Платеж за услуги'
    })
});

const payment = await paymentResponse.json();
console.log(`Кошелек: ${payment.wallet_address}`);
console.log(`Сумма: ${payment.amount} ${payment.currency}`);

// Проверяем статус
const statusResponse = await fetch(
    `http://localhost:8001/check-payment/${payment.payment_id}`,
    {
        headers: { 'X-API-Key': api_key }
    }
);

const status = await statusResponse.json();
console.log(`Статус: ${status.status}`);
```

### PHP
```php
<?php
// Получаем API ключ
$apiResponse = file_get_contents('http://localhost:8001/get-api-key');
$apiData = json_decode($apiResponse, true);
$apiKey = $apiData['api_key'];

// Создаем платеж
$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

$data = [
    'amount' => 100.0,
    'currency' => 'USDT',
    'description' => 'Платеж за услуги'
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'http://localhost:8001/create-payment');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$payment = json_decode($response, true);

echo "Кошелек: " . $payment['wallet_address'] . "\n";
echo "Сумма: " . $payment['amount'] . " " . $payment['currency'] . "\n";

curl_close($ch);
?>
```

## 🔔 Callback уведомления

При получении платежа API автоматически отправляет POST запрос на указанный `callback_url`:

```json
{
  "payment_id": "payment_id_here",
  "status": "completed",
  "amount": 100.0,
  "currency": "USDT",
  "transaction_hash": "0x1234567890abcdef..."
}
```

## 📡 Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/get-api-key` | Получить API ключ |
| POST | `/create-payment` | Создать платеж |
| GET | `/check-payment/{id}` | Проверить статус платежа |
| GET | `/health` | Проверка здоровья API |
| GET | `/docs` | Swagger документация |

## 🔑 Авторизация

Все запросы (кроме `/get-api-key`) требуют заголовок:
```
X-API-Key: your_api_key_here
```

## 📊 Статусы платежей

- `pending` - Ожидает поступления
- `completed` - Платеж получен
- `failed` - Платеж не прошел

## 🛡️ Безопасность

- ✅ API ключи генерируются автоматически
- ✅ Каждый API ключ уникален
- ✅ Все запросы логируются
- ✅ Автоматическая проверка платежей

## 🚀 Готовые клиенты

Используйте готовый Python клиент:
```python
from simple_client import SimplePaymentClient

# Создаем клиент
client = SimplePaymentClient("your_api_key")

# Создаем платеж
result = client.create_payment(100.0, "USDT", "Платеж за услуги")

if result['success']:
    print(f"Кошелек: {result['wallet_address']}")
    print(f"Сумма: {result['amount']} {result['currency']}")
```

## 📚 Документация

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

**Готово! Теперь интеграция платежей стала простой как у популярных ботов!** 🎉





