# 🔗 ПОЛНОЕ РУКОВОДСТВО ПО ИНТЕГРАЦИИ ПЛАТЕЖНОГО БОТА

## 📋 ОБЗОР СИСТЕМЫ

Наш платежный бот предоставляет API для интеграции с вашим основным ботом. Система автоматически отслеживает USDT платежи и уведомляет о поступлениях.

---

## 🔑 API КЛЮЧИ И ДОСТУП

### Текущий API ключ:
```
U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI
```

### Базовый URL:
```
http://localhost:8001
```

### Заголовки для всех запросов:
```
X-API-Key: U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI
Content-Type: application/json
```

---

## 🌐 API ENDPOINTS

### 1. Получение API ключа
```http
GET /get-api-key
```

**Ответ:**
```json
{
    "success": true,
    "api_key": "U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI",
    "message": "API ключ создан успешно",
    "usage": {
        "header": "X-API-Key",
        "example": "X-API-Key: U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI"
    }
}
```

### 2. Создание платежа
```http
POST /create-payment
```

**Тело запроса:**
```json
{
    "user_id": 123456789,
    "amount": 10.50,
    "currency": "USDT",
    "description": "Оплата за услуги"
}
```

**Ответ:**
```json
{
    "success": true,
    "payment_id": "pay_123456",
    "wallet_address": "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx",
    "amount": 10.50,
    "currency": "USDT",
    "status": "pending",
    "message": "Платеж создан успешно"
}
```

### 3. Проверка статуса платежа
```http
GET /payment-status/{payment_id}
```

**Ответ:**
```json
{
    "success": true,
    "payment_id": "pay_123456",
    "status": "confirmed",
    "amount": 10.50,
    "currency": "USDT",
    "transaction_hash": "abc123...",
    "confirmed_at": "2025-10-06T13:45:00Z"
}
```

### 4. Получение баланса кошелька
```http
GET /wallet-balance
```

**Ответ:**
```json
{
    "success": true,
    "balance": 0.908897,
    "currency": "USDT",
    "wallet_address": "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
}
```

### 5. Получение истории платежей
```http
GET /payment-history?user_id=123456789&limit=10
```

**Ответ:**
```json
{
    "success": true,
    "payments": [
        {
            "payment_id": "pay_123456",
            "user_id": 123456789,
            "amount": 10.50,
            "currency": "USDT",
            "status": "confirmed",
            "created_at": "2025-10-06T13:40:00Z",
            "confirmed_at": "2025-10-06T13:45:00Z"
        }
    ],
    "total": 1
}
```

---

## 🐍 PYTHON КЛИЕНТ ДЛЯ ИНТЕГРАЦИИ

### Установка зависимостей:
```bash
pip install requests
```

### Пример интеграции:

```python
import requests
import json
from typing import Optional, Dict, Any

class PaymentBotClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8001"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def create_payment(self, user_id: int, amount: float, currency: str = "USDT", description: str = "") -> Dict[str, Any]:
        """Создать новый платеж"""
        url = f"{self.base_url}/create-payment"
        data = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "description": description
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Получить статус платежа"""
        url = f"{self.base_url}/payment-status/{payment_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """Получить баланс кошелька"""
        url = f"{self.base_url}/wallet-balance"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_payment_history(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """Получить историю платежей пользователя"""
        url = f"{self.base_url}/payment-history"
        params = {"user_id": user_id, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

# Использование
client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")

# Создать платеж
payment = client.create_payment(
    user_id=123456789,
    amount=25.00,
    description="Оплата за подписку"
)
print(f"Платеж создан: {payment['payment_id']}")

# Проверить статус
status = client.get_payment_status(payment['payment_id'])
print(f"Статус: {status['status']}")

# Получить баланс
balance = client.get_wallet_balance()
print(f"Баланс: {balance['balance']} USDT")
```

---

## 🔄 ИНТЕГРАЦИЯ В TELEGRAM БОТА

### Пример обработчика команды оплаты:

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /pay"""
    user_id = update.effective_user.id
    
    # Создаем платеж
    client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")
    payment = client.create_payment(
        user_id=user_id,
        amount=10.00,
        description="Оплата за услуги"
    )
    
    if payment['success']:
        # Создаем клавиатуру с кнопкой проверки
        keyboard = [
            [InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_payment_{payment['payment_id']}")],
            [InlineKeyboardButton("💰 Баланс кошелька", callback_data="wallet_balance")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
💳 **Платеж создан!**

💰 Сумма: {payment['amount']} {payment['currency']}
🏦 Кошелек: `{payment['wallet_address']}`
🆔 ID платежа: `{payment['payment_id']}`

**Инструкция:**
1. Отправьте {payment['amount']} {payment['currency']} на указанный кошелек
2. Нажмите "✅ Проверить оплату" после отправки
3. Платеж будет подтвержден автоматически

⚠️ **Важно:** Отправляйте точную сумму!
        """
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Ошибка создания платежа. Попробуйте позже.")

async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса платежа"""
    query = update.callback_query
    await query.answer()
    
    payment_id = query.data.split("_")[2]
    
    client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")
    status = client.get_payment_status(payment_id)
    
    if status['success']:
        if status['status'] == 'confirmed':
            await query.edit_message_text(
                f"✅ **Платеж подтвержден!**\n\n"
                f"💰 Сумма: {status['amount']} {status['currency']}\n"
                f"🔗 Транзакция: `{status.get('transaction_hash', 'N/A')}`\n"
                f"⏰ Время: {status.get('confirmed_at', 'N/A')}",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"⏳ **Платеж в обработке**\n\n"
                f"Статус: {status['status']}\n"
                f"Попробуйте проверить через несколько минут.",
                parse_mode='Markdown'
            )
    else:
        await query.edit_message_text("❌ Ошибка проверки платежа.")

async def wallet_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс кошелька"""
    query = update.callback_query
    await query.answer()
    
    client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")
    balance = client.get_wallet_balance()
    
    if balance['success']:
        await query.edit_message_text(
            f"💰 **Баланс кошелька**\n\n"
            f"💵 Сумма: {balance['balance']} {balance['currency']}\n"
            f"🏦 Адрес: `{balance['wallet_address']}`",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Ошибка получения баланса.")
```

---

## ⚙️ НАСТРОЙКА И УПРАВЛЕНИЕ

### Запуск системы:
```bash
# Запуск бота с API
./start_bot_with_api.sh

# Проверка статуса
./status_bot_with_api.sh

# Остановка
./stop_bot_with_api.sh
```

### Мониторинг:
```bash
# Логи бота
tail -f bot.log

# Логи API
tail -f api.log

# Статус процессов
ps aux | grep -E "(private_bot|simple_payment_api)"
```

---

## 🔒 БЕЗОПАСНОСТЬ

### Важные моменты:
1. **API ключ** - держите в секрете
2. **HTTPS** - используйте в продакшене
3. **Валидация** - проверяйте все входящие данные
4. **Логирование** - ведите логи всех операций

### Рекомендации:
- Используйте переменные окружения для API ключа
- Реализуйте rate limiting
- Добавьте проверку подписи запросов
- Регулярно обновляйте API ключи

---

## 📊 МОНИТОРИНГ И ЛОГИ

### Логи бота (`bot.log`):
- Запуск/остановка
- Обработка платежей
- Ошибки API
- Статистика

### Логи API (`api.log`):
- HTTP запросы
- Ошибки валидации
- Время ответа
- Статистика использования

### Метрики для отслеживания:
- Количество созданных платежей
- Время подтверждения
- Успешность платежей
- Нагрузка на API

---

## 🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### 1. Простая оплата:
```python
# Создать платеж на 50 USDT
payment = client.create_payment(123456789, 50.00, "USDT", "Покупка товара")
print(f"Отправьте {payment['amount']} USDT на {payment['wallet_address']}")
```

### 2. Проверка статуса:
```python
# Проверить платеж
status = client.get_payment_status("pay_123456")
if status['status'] == 'confirmed':
    print("Платеж подтвержден!")
```

### 3. Получение истории:
```python
# История платежей пользователя
history = client.get_payment_history(123456789, limit=5)
for payment in history['payments']:
    print(f"{payment['amount']} {payment['currency']} - {payment['status']}")
```

---

## 📞 ПОДДЕРЖКА

### При возникновении проблем:
1. Проверьте логи: `tail -f bot.log api.log`
2. Проверьте статус: `./status_bot_with_api.sh`
3. Перезапустите систему: `./stop_bot_with_api.sh && ./start_bot_with_api.sh`
4. Проверьте подключение к API: `curl http://localhost:8001/get-api-key`

### Контакты:
- Логи системы: `bot.log`, `api.log`
- Статус: `./status_bot_with_api.sh`
- Управление: `./start_bot_with_api.sh`, `./stop_bot_with_api.sh`


