# 🔗 Руководство по интеграции Payment Bot

## 📋 Быстрый старт

### 1. Получение API ключа
1. Запустите Payment Bot
2. Нажмите кнопку "🔑 Получить API ключ" в главном меню
3. Скопируйте сгенерированный API ключ

### 2. Настройка конфигурации
Добавьте в ваш `config.py`:
```python
PAYMENT_API_KEY = "ваш_api_ключ_здесь"
PAYMENT_API_URL = "http://localhost:8001"
```

### 3. Установка зависимостей
```bash
pip install requests
```

### 4. Базовое использование
```python
from simple_client import SimplePaymentClient

# Инициализация
client = SimplePaymentClient(PAYMENT_API_KEY)

# Создание платежа
payment = client.create_payment(100.0, "USDT")
print(f"Адрес: {payment['wallet_address']}")
print(f"ID: {payment['payment_id']}")

# Проверка статуса
status = client.check_payment_status(payment['payment_id'])
print(f"Статус: {status['status']}")
```

## 🚀 Примеры интеграции

### Telegram Bot
```python
async def payment_command(update, context):
    user_id = update.effective_user.id
    amount = float(context.args[0])
    
    # Создаем платеж
    payment = client.create_payment(amount, "USDT")
    
    # Отправляем пользователю
    await update.message.reply_text(
        f"💰 Оплатите {amount} USDT на адрес: `{payment['wallet_address']}`",
        parse_mode='Markdown'
    )
```

### Web приложение
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
client = SimplePaymentClient(PAYMENT_API_KEY)

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = request.json
    amount = data['amount']
    
    payment = client.create_payment(amount, "USDT")
    
    return jsonify({
        "success": True,
        "wallet_address": payment['wallet_address'],
        "payment_id": payment['payment_id']
    })
```

## 🔧 API Endpoints

### Создание платежа
```bash
POST /create-payment
Headers: X-API-Key: ваш_ключ
Body: {"amount": 100.0, "currency": "USDT"}
```

### Проверка статуса
```bash
GET /payment-status/{payment_id}
Headers: X-API-Key: ваш_ключ
```

### Получение информации
```bash
GET /payment-info/{payment_id}
Headers: X-API-Key: ваш_ключ
```

## 🛡️ Безопасность

- ✅ API ключи генерируются криптографически стойким способом
- ✅ Каждый пользователь имеет уникальный API ключ
- ✅ Проверка принадлежности кошельков пользователям
- ✅ Логирование всех операций

## 📚 Дополнительные ресурсы

- **Документация API**: http://localhost:8001/docs
- **Пример конфигурации**: `integration_config_example.py`
- **Клиент для Python**: `simple_client.py`

## ❓ Поддержка

При возникновении проблем:
1. Проверьте, что Payment Bot запущен
2. Убедитесь, что API ключ правильный
3. Проверьте логи бота
4. Обратитесь к документации API