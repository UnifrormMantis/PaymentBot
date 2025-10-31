# 🚀 Быстрый старт интеграции Payment Bot

## 📋 Что нужно сделать

### 1. Запустить Payment Bot
```bash
# В директории Payment Bot
./start_bot.sh
./start_simple_api.sh
```

### 2. Получить API ключ
```bash
curl -s http://localhost:8002/get-api-key
```

### 3. Добавить в основной бот

#### В config.py:
```python
PAYMENT_API_URL = "http://localhost:8002"
PAYMENT_API_KEY = "ВАШ_API_КЛЮЧ"
```

#### В основной файл бота:
```python
from payment_integration_example import register_payment_handlers, start_auto_payment_checker

def main():
    # ... ваш код ...
    
    # Добавить эти строки:
    register_payment_handlers(application)
    start_auto_payment_checker()
    
    application.run_polling()
```

### 4. Готовые команды

- `/pay 100` - создать платеж на 100 USDT
- `/setwallet T...` - настроить кошелек
- `/walletbalance` - проверить баланс

## 📁 Файлы для копирования

1. `payment_integration_example.py` - основной код интеграции
2. `INTEGRATION_INSTRUCTIONS.md` - подробная инструкция

## ⚡ Быстрый тест

```python
# Тест API
import requests

response = requests.post('http://localhost:8002/verify-payment', 
    headers={'X-API-Key': 'ВАШ_КЛЮЧ'},
    json={'wallet_address': 'T...', 'amount': 1.0})
print(response.json())
```

## 🔧 Адаптация

В файле `payment_integration_example.py` найдите функции с комментариями:
- `# ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ`
- Адаптируйте под вашу базу данных

## 📞 Поддержка

При проблемах проверьте:
1. Запущен ли Payment Bot: `./status_bot.sh`
2. Работает ли API: `curl http://localhost:8002/health`
3. Правильный ли API ключ

---

**Готово! Ваш бот теперь поддерживает TRC20 платежи! 🎉**






