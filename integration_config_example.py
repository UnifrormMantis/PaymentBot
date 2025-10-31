#!/usr/bin/env python3
"""
Пример конфигурации для интеграции Payment Bot в основной бот
"""

# API ключ для интеграции (получите через кнопку "Получить API ключ" в боте)
PAYMENT_API_KEY = "YOUR_API_KEY_HERE"  # Замените на ваш API ключ

# URL API сервиса
PAYMENT_API_URL = "http://localhost:8001"

# Настройки для интеграции
PAYMENT_SETTINGS = {
    "default_currency": "USDT",
    "timeout": 30,  # секунд
    "retry_attempts": 3,
    "check_interval": 10,  # секунд между проверками статуса
}

# Пример использования в основном боте
"""
from simple_client import SimplePaymentClient
import asyncio

# Инициализация клиента
payment_client = SimplePaymentClient(PAYMENT_API_KEY)

async def create_payment_for_user(user_id: int, amount: float, currency: str = "USDT"):
    '''Создать платеж для пользователя'''
    try:
        # Создаем платеж
        payment = payment_client.create_payment(amount, currency)
        
        # Отправляем пользователю информацию о платеже
        message = f"""
💰 **Платеж создан!**

💳 **Сумма:** {amount} {currency}
🏦 **Адрес для оплаты:** `{payment['wallet_address']}`
🆔 **ID платежа:** {payment['payment_id']}

⏰ **Время ожидания:** 30 минут
        """
        
        return {
            "success": True,
            "payment_id": payment['payment_id'],
            "wallet_address": payment['wallet_address'],
            "amount": amount,
            "currency": currency,
            "message": message
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def check_payment_status(payment_id: str):
    '''Проверить статус платежа'''
    try:
        status = payment_client.check_payment_status(payment_id)
        return {
            "success": True,
            "status": status['status'],
            "confirmed": status.get('confirmed', False)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Пример использования в команде бота
async def payment_command(update, context):
    '''Команда для создания платежа'''
    user_id = update.effective_user.id
    
    # Получаем сумму из аргументов команды
    if not context.args:
        await update.message.reply_text("❌ Укажите сумму платежа!\nПример: /payment 100")
        return
    
    try:
        amount = float(context.args[0])
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть больше 0!")
            return
        
        # Создаем платеж
        result = await create_payment_for_user(user_id, amount)
        
        if result["success"]:
            await update.message.reply_text(
                result["message"],
                parse_mode='Markdown'
            )
            
            # Запускаем проверку статуса в фоне
            asyncio.create_task(check_payment_periodically(
                update, context, result["payment_id"]
            ))
        else:
            await update.message.reply_text(f"❌ Ошибка создания платежа: {result['error']}")
            
    except ValueError:
        await update.message.reply_text("❌ Неверный формат суммы!")

async def check_payment_periodically(update, context, payment_id: str):
    '''Периодическая проверка статуса платежа'''
    import time
    
    for _ in range(18):  # Проверяем 18 раз по 10 секунд = 3 минуты
        await asyncio.sleep(10)
        
        result = await check_payment_status(payment_id)
        
        if result["success"] and result["confirmed"]:
            await update.message.reply_text(
                "✅ **Платеж подтвержден!**\n\n"
                "Спасибо за оплату! Ваш заказ будет обработан в ближайшее время."
            )
            break
    else:
        await update.message.reply_text(
            "⏰ Время ожидания платежа истекло.\n"
            "Если вы уже отправили платеж, обратитесь в поддержку."
        )
"""






