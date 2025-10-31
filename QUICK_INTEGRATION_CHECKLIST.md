# ✅ БЫСТРЫЙ ЧЕКЛИСТ ИНТЕГРАЦИИ

## 🎯 ОЦЕНКА ГОТОВНОСТИ (5 минут)

### **1. Проверьте Payment Bot API:**
```bash
# ✅ API запущен?
curl http://localhost:8001/health

# ✅ Эндпоинты работают?
curl http://localhost:8001/get-api-key
```

### **2. Проверьте основной бот:**
```bash
# ✅ Есть ли PaymentClient?
grep -r "PaymentClient" /path/to/main/bot/

# ✅ Есть ли команды?
grep -r "def.*pay_command" /path/to/main/bot/
grep -r "def.*wallet_command" /path/to/main/bot/
```

### **3. Проверьте базу данных:**
```bash
# ✅ Есть ли таблицы?
sqlite3 bot_database.db ".tables"

# ✅ Есть ли поле wallet_address?
sqlite3 bot_database.db "PRAGMA table_info(users);"
```

---

## 🚀 БЫСТРАЯ ИНТЕГРАЦИЯ (30 минут)

### **ШАГ 1: Добавьте PaymentClient (5 минут)**
```python
# Скопируйте класс PaymentClient из INTEGRATION_TEMPLATES.py
# Обновите PAYMENT_API_KEY в config.py
```

### **ШАГ 2: Обновите базу данных (5 минут)**
```sql
-- Добавьте поле wallet_address
ALTER TABLE users ADD COLUMN wallet_address TEXT;

-- Создайте таблицы
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    currency TEXT DEFAULT 'USDT',
    wallet_address TEXT,
    tx_hash TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_balances (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0.0,
    currency TEXT DEFAULT 'USDT',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **ШАГ 3: Добавьте команды (10 минут)**
```python
# Скопируйте команды из INTEGRATION_TEMPLATES.py:
# - wallet_command
# - pay_command  
# - balance_command
# - check_payment_callback
```

### **ШАГ 4: Зарегистрируйте обработчики (5 минут)**
```python
# Добавьте в основной бот:
register_handlers(application)
```

### **ШАГ 5: Протестируйте (5 минут)**
```bash
# 1. Запустите основной бот
# 2. Отправьте /wallet TTestWallet123456789
# 3. Отправьте /pay
# 4. Нажмите "Проверить платеж"
```

---

## 🔧 НАСТРОЙКИ

### **config.py:**
```python
PAYMENT_API_URL = "http://localhost:8001"
PAYMENT_API_KEY = "your_api_key_here"  # Получите через GET /get-api-key
```

### **Получение API ключа:**
```bash
curl http://localhost:8001/get-api-key
```

---

## 🚨 БЫСТРОЕ УСТРАНЕНИЕ ПРОБЛЕМ

### **Проблема: API ключ не работает**
```bash
# Решение: Получите новый ключ
curl http://localhost:8001/get-api-key
# Обновите PAYMENT_API_KEY в config.py
```

### **Проблема: Payment Bot API не отвечает**
```bash
# Решение: Запустите API
./start_simple_api.sh
# Проверьте: curl http://localhost:8001/health
```

### **Проблема: База данных не найдена**
```bash
# Решение: Создайте таблицы
sqlite3 bot_database.db < create_tables.sql
```

### **Проблема: Команды не работают**
```bash
# Решение: Проверьте регистрацию обработчиков
grep -r "register_handlers" /path/to/main/bot/
```

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА

### **✅ Все работает, если:**
- [ ] Payment Bot API отвечает на `/health`
- [ ] API ключ получается через `/get-api-key`
- [ ] Команда `/wallet` сохраняет кошелек
- [ ] Команда `/pay` показывает адрес для оплаты
- [ ] Кнопка "Проверить платеж" работает
- [ ] Команда `/balance` показывает баланс

### **🎉 Готово к использованию!**

---

## 📞 ПОДДЕРЖКА

**Если что-то не работает:**
1. Проверьте логи: `tail -f bot.log`
2. Проверьте API: `curl http://localhost:8001/health`
3. Проверьте базу данных: `sqlite3 bot_database.db ".tables"`
4. Используйте готовые шаблоны из `INTEGRATION_TEMPLATES.py`

**Время интеграции: 30 минут** ⏱️






