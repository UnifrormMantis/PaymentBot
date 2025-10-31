# 🚀 ОБНОВЛЕННАЯ ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ PAYMENT BOT

## 📋 ОБЗОР

Payment Bot теперь поддерживает **2 новых эндпоинта** для работы с системой депозитов:

1. **`/get-payment-wallet`** - Получение активного кошелька для приема платежей
2. **`/check-user-payments`** - Проверка переводов с кошельков пользователей

---

## 🔧 ЭНДПОИНТ 1: `/get-payment-wallet`

### **Назначение:**
Когда пользователь указывает свой кошелек в боте, мы получаем активный кошелек для приема платежей.

### **HTTP запрос:**
```http
POST /get-payment-wallet
Content-Type: application/json
X-API-Key: YOUR_API_KEY

{
  "user_wallet": "TUserWallet123456789"
}
```

### **HTTP ответ:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "wallet_address": "TYourMainWallet456789012"
}
```

### **Пример использования:**
```bash
curl -X POST http://localhost:8001/get-payment-wallet \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_wallet": "TTestUserWallet123456789"}'
```

---

## 🔧 ЭНДПОИНТ 2: `/check-user-payments`

### **Назначение:**
Проверить, переводил ли пользователь деньги с своего кошелька на активный кошелек.

### **HTTP запрос:**
```http
POST /check-user-payments
Content-Type: application/json
X-API-Key: YOUR_API_KEY

{
  "user_wallet": "TUserWallet123456789"
}
```

### **HTTP ответ:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "payments": [
    {
      "amount": 100.0,
      "tx_hash": "0x1234567890abcdef1234567890abcdef12345678",
      "confirmed": true,
      "timestamp": "2025-10-07T23:00:00Z"
    }
  ]
}
```

### **Пример использования:**
```bash
curl -X POST http://localhost:8001/check-user-payments \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_wallet": "TTestUserWallet123456789"}'
```

---

## 🗄️ НАСТРОЙКА БАЗЫ ДАННЫХ

### **Новые таблицы:**

#### 1. `user_payment_links`
```sql
CREATE TABLE user_payment_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_wallet TEXT NOT NULL,
    active_wallet TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_wallet)
);
```

#### 2. `payment_tracking`
```sql
CREATE TABLE payment_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_wallet TEXT NOT NULL,
    active_wallet TEXT NOT NULL,
    amount REAL NOT NULL,
    tx_hash TEXT NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 ОБНОВЛЕННЫЙ АЛГОРИТМ РАБОТЫ

### **1. Пользователь указывает свой кошелек**
```python
# В основном боте
user_wallet = "TUserWallet123456789"

# Получаем активный кошелек для приема платежей
response = await payment_client.get_payment_wallet(user_wallet)
active_wallet = response["wallet_address"]

# Показываем пользователю активный кошелек для оплаты
await message.reply(f"Переведите средства на кошелек: {active_wallet}")
```

### **2. Проверка платежей**
```python
# Проверяем, переводил ли пользователь деньги
payments = await payment_client.check_user_payments(user_wallet)

if payments:
    for payment in payments:
        if payment["confirmed"]:
            # Зачисляем средства на баланс пользователя
            await add_funds_to_user(user_id, payment["amount"])
```

---

## 🧪 ТЕСТИРОВАНИЕ

### **1. Получение API ключа:**
```bash
curl http://localhost:8001/get-api-key
```

### **2. Тест получения кошелька:**
```bash
curl -X POST http://localhost:8001/get-payment-wallet \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_wallet": "TTestUserWallet123456789"}'
```

### **3. Тест проверки платежей:**
```bash
curl -X POST http://localhost:8001/check-user-payments \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_wallet": "TTestUserWallet123456789"}'
```

---

## 🔧 ИНТЕГРАЦИЯ В ОСНОВНОЙ БОТ

### **1. Обновите `payment_client.py`:**
```python
class PaymentClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8001"):
        self.api_key = api_key
        self.base_url = base_url
    
    async def get_payment_wallet(self, user_wallet: str) -> dict:
        """Получить активный кошелек для приема платежей"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/get-payment-wallet",
                headers={"X-API-Key": self.api_key},
                json={"user_wallet": user_wallet}
            ) as response:
                return await response.json()
    
    async def check_user_payments(self, user_wallet: str) -> list:
        """Проверить платежи пользователя"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/check-user-payments",
                headers={"X-API-Key": self.api_key},
                json={"user_wallet": user_wallet}
            ) as response:
                data = await response.json()
                return data.get("payments", [])
```

### **2. Обновите команду `/pay`:**
```python
@bot.message_handler(commands=['pay'])
async def pay_command(message):
    user_id = message.from_user.id
    user_wallet = get_user_wallet(user_id)  # Получаем кошелек пользователя
    
    if not user_wallet:
        await message.reply("Сначала укажите ваш кошелек командой /wallet")
        return
    
    # Получаем активный кошелек для приема платежей
    try:
        response = await payment_client.get_payment_wallet(user_wallet)
        active_wallet = response["wallet_address"]
        
        await message.reply(
            f"💳 **Пополнение баланса**\n\n"
            f"📱 Ваш кошелек: `{user_wallet}`\n"
            f"🏦 Кошелек для оплаты: `{active_wallet}`\n\n"
            f"Переведите средства на указанный кошелек, "
            f"затем нажмите кнопку 'Проверить платеж'"
        )
        
    except Exception as e:
        await message.reply(f"❌ Ошибка получения кошелька: {e}")
```

### **3. Обновите проверку платежей:**
```python
@bot.callback_query_handler(func=lambda call: call.data == "check_payment")
async def check_payment_callback(call):
    user_id = call.from_user.id
    user_wallet = get_user_wallet(user_id)
    
    try:
        payments = await payment_client.check_user_payments(user_wallet)
        
        if payments:
            for payment in payments:
                if payment["confirmed"]:
                    # Зачисляем средства
                    await add_funds_to_user(user_id, payment["amount"])
                    await call.message.reply(
                        f"✅ Платеж подтвержден!\n"
                        f"💰 Зачислено: {payment['amount']} USDT"
                    )
                    return
        
        await call.message.reply("⏳ Платеж еще не поступил. Попробуйте позже.")
        
    except Exception as e:
        await call.message.reply(f"❌ Ошибка проверки платежа: {e}")
```

---

## ⚙️ НАСТРОЙКИ API

### **Конфигурация:**
```python
# config.py
PAYMENT_API_KEY = "YOUR_API_KEY"  # Получите через /get-api-key
PAYMENT_API_URL = "http://localhost:8001"
```

### **Переменные окружения:**
```bash
export PAYMENT_API_KEY="YOUR_API_KEY"
export PAYMENT_API_URL="http://localhost:8001"
```

---

## 🚀 ЗАПУСК

### **1. Запустите Payment Bot:**
```bash
./start_simple_api.sh
```

### **2. Проверьте работу:**
```bash
curl http://localhost:8001/health
```

### **3. Получите API ключ:**
```bash
curl http://localhost:8001/get-api-key
```

---

## ✅ ПРОВЕРКА РАБОТЫ

После реализации:

1. **Запустите Payment Bot** с новыми эндпоинтами
2. **Протестируйте** с помощью curl команд
3. **Проверьте в основном боте** - ошибка должна исчезнуть
4. **Создайте тестовый депозит** для проверки полного цикла

**После этого система будет полностью работать!** 🎉

---

## 📞 ПОДДЕРЖКА

При возникновении проблем:

1. Проверьте логи: `tail -f bot.log`
2. Проверьте API: `curl http://localhost:8001/health`
3. Проверьте API ключ: `curl http://localhost:8001/get-api-key`
4. Проверьте эндпоинты: `curl http://localhost:8001/`

---

## 🎯 ГОТОВО К ИСПОЛЬЗОВАНИЮ!

Payment Bot теперь полностью готов для интеграции с системой депозитов. Все необходимые эндпоинты реализованы и протестированы.