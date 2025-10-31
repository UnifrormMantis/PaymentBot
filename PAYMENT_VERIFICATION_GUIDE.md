# 💳 РУКОВОДСТВО: Система проверки USDT платежей

## 📋 ОПИСАНИЕ СИСТЕМЫ

Это API для проверки поступления USDT платежей от пользователей. Система работает следующим образом:

1. **Пользователь** в вашем основном боте указывает свой кошелек и сумму
2. **Ваш бот** отправляет эти данные в наш API
3. **Наш API** проверяет поступление USDT от указанного кошелька
4. **API возвращает** информацию о полученной сумме
5. **Ваш бот** использует эту информацию для своих нужд

---

## 🔑 АКТУАЛЬНЫЕ ДАННЫЕ

### API Ключ:
```
QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ
```

### Базовый URL:
```
http://localhost:8002
```

### Кошелек для приема платежей:
```
TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx
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
    "api_key": "QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ",
    "message": "API ключ создан успешно",
    "usage": {
        "header": "X-API-Key",
        "example": "X-API-Key: QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ"
    }
}
```

### 2. Проверка платежа (ОСНОВНОЙ)
```http
POST /verify-payment
```

**Заголовки:**
```
X-API-Key: QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ
Content-Type: application/json
```

**Тело запроса:**
```json
{
    "user_wallet": "TUserWallet1234567890123456789012345",
    "expected_amount": 10.50,
    "currency": "USDT",
    "description": "Покупка товара"
}
```

**Ответ:**
```json
{
    "success": true,
    "payment_found": true,
    "received_amount": 10.50,
    "currency": "USDT",
    "transaction_hash": "abc123...",
    "confirmed_at": "2025-10-06T13:45:00Z",
    "user_wallet": "TUserWallet1234567890123456789012345",
    "message": "Платеж найден: 10.50 USDT"
}
```

### 3. Информация о кошельке
```http
GET /wallet-info
```

**Ответ:**
```json
{
    "success": true,
    "wallet_address": "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx",
    "balance": 0.908897,
    "currency": "USDT",
    "message": "Информация о кошельке для приема платежей"
}
```

### 4. Проверка здоровья API
```http
GET /health
```

---

## 🐍 PYTHON КЛИЕНТ

### Установка:
```bash
pip install requests
```

### Использование:

```python
from payment_verification_client import PaymentVerificationClient

# Инициализация
client = PaymentVerificationClient("QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ")

# Проверка платежа
result = client.verify_payment(
    user_wallet="TUserWallet1234567890123456789012345",
    expected_amount=10.50,
    currency="USDT",
    description="Покупка товара"
)

if result["success"] and result["payment_found"]:
    print(f"✅ Платеж подтвержден: {result['received_amount']} USDT")
    print(f"🔗 Транзакция: {result['transaction_hash']}")
else:
    print(f"❌ Платеж не найден: {result['message']}")
```

---

## 📱 ИНТЕГРАЦИЯ В TELEGRAM БОТА

### Пример обработчика команды покупки:

```python
from payment_verification_client import PaymentVerificationClient

# Инициализация клиента
payment_client = PaymentVerificationClient("QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ")

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /buy"""
    user_id = update.effective_user.id
    
    # Получаем данные от пользователя
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Укажите кошелек и сумму!**\n\n"
            "Пример: `/buy TYourWallet1234567890123456789012345 10.50`",
            parse_mode='Markdown'
        )
        return
    
    user_wallet = context.args[0]
    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Неверная сумма!")
        return
    
    # Показываем информацию о платеже
    wallet_info = payment_client.get_wallet_info()
    if wallet_info["success"]:
        message = f"""
💳 **Информация о платеже**

💰 **Сумма:** {amount} USDT
🏦 **Ваш кошелек:** `{user_wallet}`
📥 **Кошелек для оплаты:** `{wallet_info['wallet_address']}`

**📋 Инструкция:**
1️⃣ Отправьте **{amount} USDT** на указанный кошелек
2️⃣ Используйте **ваш кошелек** `{user_wallet}` как отправитель
3️⃣ Нажмите **"✅ Проверить оплату"** после отправки

⚠️ **Важно:** Отправляйте точную сумму!
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_{user_wallet}_{amount}")],
            [InlineKeyboardButton("💰 Информация о кошельке", callback_data="wallet_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка платежа"""
    query = update.callback_query
    await query.answer()
    
    # Парсим данные из callback_data
    parts = query.data.split("_")
    user_wallet = parts[1]
    amount = float(parts[2])
    
    # Показываем индикатор загрузки
    await query.edit_message_text("⏳ Проверяем платеж...")
    
    # Проверяем платеж
    result = payment_client.verify_payment(
        user_wallet=user_wallet,
        expected_amount=amount,
        currency="USDT",
        description=f"Покупка пользователем {query.from_user.id}"
    )
    
    if result["success"] and result["payment_found"]:
        # Платеж найден - зачисляем товар/услугу
        message = f"""
✅ **Платеж подтвержден!**

💰 **Получено:** {result['received_amount']} USDT
🔗 **Транзакция:** `{result['transaction_hash']}`
⏰ **Время:** {result['confirmed_at']}

🎉 **Товар/услуга зачислены!**
        """
        
        # Здесь добавьте логику зачисления товара/услуги пользователю
        
    else:
        message = f"""
❌ **Платеж не найден**

💰 **Ожидалось:** {amount} USDT
🏦 **От кошелька:** `{user_wallet}`

**Возможные причины:**
• Платеж еще не поступил (подождите 1-2 минуты)
• Неверная сумма
• Неверный кошелек отправителя
• Платеж в другой валюте (не USDT)

💡 **Попробуйте проверить еще раз**
        """
        
        # Кнопка для повторной проверки
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_{user_wallet}_{amount}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    await query.edit_message_text(message, parse_mode='Markdown')
```

---

## 🔧 УПРАВЛЕНИЕ СИСТЕМОЙ

### Запуск:
```bash
./start_payment_api.sh
```

### Проверка статуса:
```bash
./status_payment_api.sh
```

### Остановка:
```bash
./stop_payment_api.sh
```

### Логи:
```bash
tail -f payment_api.log
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Проверка API:
```bash
curl http://localhost:8002/health
```

### Получение API ключа:
```bash
curl http://localhost:8002/get-api-key
```

### Тестирование клиента:
```bash
python payment_verification_client.py
```

---

## 📊 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### 1. Простая проверка платежа:
```python
client = PaymentVerificationClient("QteR2mHB_hX7BLQAedfgXRWRcGiHsTR6HFtvMqaA-uQ")

result = client.verify_payment(
    user_wallet="TUserWallet1234567890123456789012345",
    expected_amount=25.00,
    currency="USDT"
)

if result["payment_found"]:
    print(f"Получено: {result['received_amount']} USDT")
```

### 2. Ожидание платежа:
```python
result = client.wait_for_payment(
    user_wallet="TUserWallet1234567890123456789012345",
    expected_amount=50.00,
    timeout=300,  # 5 минут
    check_interval=10  # проверка каждые 10 секунд
)
```

### 3. Получение информации о кошельке:
```python
wallet_info = client.get_wallet_info()
print(f"Кошелек: {wallet_info['wallet_address']}")
print(f"Баланс: {wallet_info['balance']} USDT")
```

---

## 🔒 БЕЗОПАСНОСТЬ

### Важные моменты:
1. **API ключ** - держите в секрете
2. **Валидация** - проверяйте все входящие данные
3. **Логирование** - ведите логи всех операций
4. **HTTPS** - используйте в продакшене

### Рекомендации:
- Используйте переменные окружения для API ключа
- Реализуйте rate limiting
- Добавьте проверку подписи запросов
- Регулярно обновляйте API ключи

---

## 🆘 ПОДДЕРЖКА

### При возникновении проблем:
1. Проверьте статус: `./status_payment_api.sh`
2. Проверьте логи: `tail -f payment_api.log`
3. Перезапустите API: `./stop_payment_api.sh && ./start_payment_api.sh`
4. Проверьте подключение: `curl http://localhost:8002/health`

### Контакты:
- Логи API: `payment_api.log`
- Статус: `./status_payment_api.sh`
- Управление: `./start_payment_api.sh`, `./stop_payment_api.sh`


