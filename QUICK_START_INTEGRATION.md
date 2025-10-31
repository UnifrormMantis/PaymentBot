# 🚀 БЫСТРЫЙ СТАРТ: Интеграция платежного бота

## 📋 КЛЮЧЕВАЯ ИНФОРМАЦИЯ

### API Ключ:
```
U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI
```

### Базовый URL:
```
http://localhost:8001
```

### Кошелек для платежей:
```
TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx
```

---

## 🔧 БЫСТРАЯ ИНТЕГРАЦИЯ

### 1. Установка зависимостей:
```bash
pip install requests python-telegram-bot
```

### 2. Копирование клиента:
```python
# Скопируйте файл payment_integration_client.py в ваш проект
```

### 3. Базовое использование:
```python
from payment_integration_client import PaymentBotClient

# Инициализация
client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")

# Создать платеж
payment = client.create_payment(
    user_id=123456789,
    amount=10.00,
    description="Оплата за услуги"
)

# Проверить статус
status = client.get_payment_status(payment['payment_id'])

# Получить баланс
balance = client.get_wallet_balance()
```

---

## 📱 TELEGRAM БОТ - ГОТОВЫЙ КОД

### Команды для добавления в вашего бота:

```python
from payment_integration_client import PaymentBotClient

# Инициализация
payment_client = PaymentBotClient("U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI")

# Команда /pay
async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = float(context.args[0])  # Сумма из аргументов
    
    payment = payment_client.create_payment(user_id, amount, "USDT", "Платеж")
    
    if payment['success']:
        message = f"""
💳 **Платеж создан!**

💰 Сумма: {payment['amount']} USDT
🏦 Кошелек: `{payment['wallet_address']}`
🆔 ID: `{payment['payment_id']}`

Отправьте {payment['amount']} USDT на указанный кошелек
        """
        await update.message.reply_text(message, parse_mode='Markdown')

# Команда /balance
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = payment_client.get_wallet_balance()
    
    if balance['success']:
        message = f"💰 Баланс: {balance['balance']} USDT"
        await update.message.reply_text(message)
```

---

## 🌐 HTTP API - ПРЯМЫЕ ЗАПРОСЫ

### Создание платежа:
```bash
curl -X POST http://localhost:8001/create-payment \
  -H "X-API-Key: U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456789,
    "amount": 10.50,
    "currency": "USDT",
    "description": "Оплата за услуги"
  }'
```

### Проверка статуса:
```bash
curl -X GET http://localhost:8001/payment-status/pay_123456 \
  -H "X-API-Key: U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI"
```

### Получение баланса:
```bash
curl -X GET http://localhost:8001/wallet-balance \
  -H "X-API-Key: U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI"
```

---

## ⚙️ УПРАВЛЕНИЕ СИСТЕМОЙ

### Запуск:
```bash
./start_bot_with_api.sh
```

### Проверка статуса:
```bash
./status_bot_with_api.sh
```

### Остановка:
```bash
./stop_bot_with_api.sh
```

### Логи:
```bash
tail -f bot.log      # Логи бота
tail -f api.log      # Логи API
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Запуск тестов:
```bash
python payment_integration_client.py
```

### Проверка API:
```bash
curl http://localhost:8001/get-api-key
```

---

## 📊 СТАТУС СИСТЕМЫ

- **Бот:** ✅ Запущен
- **API:** ✅ Запущен на порту 8001
- **Баланс:** 0.908897 USDT
- **Кошелек:** TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx

---

## 🔗 ПОЛЕЗНЫЕ ФАЙЛЫ

- `payment_integration_client.py` - Готовый клиент
- `telegram_bot_integration_example.py` - Пример для Telegram
- `INTEGRATION_COMPLETE_GUIDE.md` - Полная документация
- `QUICK_START_INTEGRATION.md` - Этот файл

---

## 🆘 ПОДДЕРЖКА

При проблемах:
1. Проверьте статус: `./status_bot_with_api.sh`
2. Проверьте логи: `tail -f bot.log api.log`
3. Перезапустите: `./stop_bot_with_api.sh && ./start_bot_with_api.sh`
4. Проверьте API: `curl http://localhost:8001/get-api-key`


