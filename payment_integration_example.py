#!/usr/bin/env python3
"""
Пример интеграции Payment Bot в основной Telegram бот
Готовый код для копирования и адаптации
"""

import requests
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

# Настройки Payment Bot API
PAYMENT_API_URL = "http://localhost:8001"
PAYMENT_API_KEY = "f5Szv3xPoYKE8sngedRfjemrRURVjJ6_yYCQ7WSdfzI"

# =============================================================================
# КЛИЕНТ ДЛЯ РАБОТЫ С PAYMENT BOT API
# =============================================================================

class PaymentClient:
    def __init__(self):
        self.api_url = PAYMENT_API_URL
        self.api_key = PAYMENT_API_KEY
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_payment_wallet(self, user_wallet: str) -> dict:
        """Получить активный кошелек для приема платежей"""
        try:
            response = requests.post(
                f"{self.api_url}/get-payment-wallet",
                headers=self.headers,
                json={
                    "user_wallet": user_wallet
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения кошелька: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Payment API: {e}")
            return {"success": False, "error": str(e)}
    
    def check_user_payments(self, user_wallet: str) -> dict:
        """Проверить платежи пользователя"""
        try:
            response = requests.post(
                f"{self.api_url}/check-user-payments",
                headers=self.headers,
                json={
                    "user_wallet": user_wallet
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка проверки платежей: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Payment API: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_payment(self, wallet_address: str, amount: float, currency: str = "USDT") -> dict:
        """Проверить платеж на кошелек (устаревший метод)"""
        try:
            response = requests.post(
                f"{self.api_url}/verify-payment",
                headers=self.headers,
                json={
                    "wallet_address": wallet_address,
                    "amount": amount,
                    "currency": currency
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка проверки платежа: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Payment API: {e}")
            return {"success": False, "error": str(e)}
    
    def get_wallet_info(self, wallet_address: str) -> dict:
        """Получить информацию о кошельке"""
        try:
            response = requests.get(
                f"{self.api_url}/wallet-info",
                headers=self.headers,
                params={"wallet_address": wallet_address},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ошибка получения информации о кошельке: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Payment API: {e}")
            return {"success": False, "error": str(e)}

# Глобальный экземпляр клиента
payment_client = PaymentClient()

# =============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ (АДАПТИРУЙТЕ ПОД ВАШУ БД)
# =============================================================================

def get_user_wallet(user_id: int) -> str:
    """Получить кошелек пользователя из базы данных"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ ПОЛУЧЕНИЯ КОШЕЛЬКА
    # Пример:
    # conn = sqlite3.connect('your_database.db')
    # cursor = conn.cursor()
    # cursor.execute('SELECT wallet_address FROM user_wallets WHERE user_id = ?', (user_id,))
    # result = cursor.fetchone()
    # conn.close()
    # return result[0] if result else None
    
    # ВРЕМЕННАЯ ЗАГЛУШКА - ЗАМЕНИТЕ НА РЕАЛЬНУЮ ФУНКЦИЮ
    return "TJR44gwdyGhLa4833zJtutNepRoNVFpMzX"  # Тестовый кошелек

def save_user_wallet(user_id: int, wallet_address: str):
    """Сохранить кошелек пользователя в базу данных"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ СОХРАНЕНИЯ КОШЕЛЬКА
    # Пример:
    # conn = sqlite3.connect('your_database.db')
    # cursor = conn.cursor()
    # cursor.execute('INSERT OR REPLACE INTO user_wallets (user_id, wallet_address) VALUES (?, ?)', 
    #                (user_id, wallet_address))
    # conn.commit()
    # conn.close()
    
    logger.info(f"Сохранен кошелек {wallet_address} для пользователя {user_id}")

def save_pending_payment(user_id: int, amount: float, wallet_address: str) -> int:
    """Сохранить ожидающий платеж в базу данных"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ СОХРАНЕНИЯ ПЛАТЕЖА
    # Пример:
    # conn = sqlite3.connect('your_database.db')
    # cursor = conn.cursor()
    # cursor.execute('INSERT INTO pending_payments (user_id, amount, wallet_address) VALUES (?, ?, ?)', 
    #                (user_id, amount, wallet_address))
    # payment_id = cursor.lastrowid
    # conn.commit()
    # conn.close()
    # return payment_id
    
    # ВРЕМЕННАЯ ЗАГЛУШКА
    return 1

def get_pending_payments():
    """Получить все ожидающие платежи"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ ПОЛУЧЕНИЯ ПЛАТЕЖЕЙ
    return []

def mark_payment_confirmed(payment_id: int, tx_hash: str):
    """Отметить платеж как подтвержденный"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ ОБНОВЛЕНИЯ СТАТУСА
    logger.info(f"Платеж {payment_id} подтвержден с хешем {tx_hash}")

def add_user_balance(user_id: int, amount: float):
    """Добавить средства на баланс пользователя"""
    # ЗАМЕНИТЕ НА ВАШУ ФУНКЦИЮ ОБНОВЛЕНИЯ БАЛАНСА
    logger.info(f"Добавлено {amount} USDT на баланс пользователя {user_id}")

# =============================================================================
# ОБРАБОТЧИКИ КОМАНД
# =============================================================================

async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /pay"""
    user_id = update.effective_user.id
    
    # Получаем сумму из аргументов команды
    if not context.args:
        await update.message.reply_text("❌ Укажите сумму для оплаты\nПример: /pay 100")
        return
    
    try:
        amount = float(context.args[0])
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть больше 0")
            return
    except ValueError:
        await update.message.reply_text("❌ Неверная сумма. Используйте числа.\nПример: /pay 100")
        return
    
    # Получаем кошелек пользователя
    user_wallet = get_user_wallet(user_id)
    
    if not user_wallet:
        await update.message.reply_text(
            "❌ У вас не настроен кошелек для оплаты\n\n"
            "Используйте команду /setwallet для настройки кошелька"
        )
        return
    
    # Получаем активный кошелек для приема платежей
    await update.message.reply_text("🔄 Получаем адрес для оплаты...")
    
    result = payment_client.get_payment_wallet(user_wallet)
    
    if not result.get("success"):
        await update.message.reply_text(
            f"❌ Ошибка получения адреса для оплаты\n\n"
            f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
        )
        return
    
    active_wallet = result["wallet_address"]
    
    # Создаем сообщение с адресом для оплаты
    payment_message = f"""
💳 **Оплата {amount} USDT**

🏦 **Ваш кошелек:** `{user_wallet}`
💰 **Адрес для оплаты:** `{active_wallet}`

💵 **Сумма:** {amount} USDT
⏰ **Время на оплату:** 5 минут

📱 Переведите {amount} USDT с вашего кошелька на указанный адрес, затем нажмите "✅ Проверить оплату"
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_payment_{amount}")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await update.message.reply_text(
        payment_message, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )
    
    # Сохраняем информацию о платеже
    context.user_data['payment_amount'] = amount
    context.user_data['user_wallet'] = user_wallet
    context.user_data['active_wallet'] = active_wallet
    context.user_data['payment_message_id'] = message.message_id
    context.user_data['payment_time'] = datetime.now()
    
    # Сохраняем в базу данных
    payment_id = save_pending_payment(user_id, amount, user_wallet)
    context.user_data['payment_id'] = payment_id

async def setwallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для настройки кошелька пользователя"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "💳 **Настройка кошелька**\n\n"
            "Использование: /setwallet <адрес_кошелька>\n"
            "Пример: /setwallet TJR44gwdyGhLa4833zJtutNepRoNVFpMzX\n\n"
            "⚠️ Убедитесь, что это ваш кошелек TRC20!"
        )
        return
    
    wallet_address = context.args[0]
    
    # Проверяем валидность адреса (базовая проверка)
    if not wallet_address.startswith('T') or len(wallet_address) != 34:
        await update.message.reply_text(
            "❌ Неверный формат адреса TRC20 кошелька\n\n"
            "Адрес должен начинаться с 'T' и содержать 34 символа"
        )
        return
    
    # Сохраняем кошелек
    save_user_wallet(user_id, wallet_address)
    
    await update.message.reply_text(
        f"✅ **Кошелек настроен!**\n\n"
        f"🏦 **Адрес:** `{wallet_address}`\n\n"
        f"Теперь вы можете использовать команду /pay для создания платежей",
        parse_mode='Markdown'
    )

async def wallet_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки баланса кошелька"""
    user_id = update.effective_user.id
    
    wallet = get_user_wallet(user_id)
    if not wallet:
        await update.message.reply_text(
            "❌ У вас не настроен кошелек\n\n"
            "Используйте команду /setwallet для настройки"
        )
        return
    
    # Получаем информацию о кошельке
    result = payment_client.get_wallet_info(wallet)
    
    if result.get("success"):
        balance = result.get("balance", 0)
        await update.message.reply_text(
            f"💰 **Баланс кошелька**\n\n"
            f"🏦 **Адрес:** `{wallet}`\n"
            f"💵 **Баланс:** {balance} USDT",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Ошибка получения баланса")

# =============================================================================
# ОБРАБОТЧИКИ CALLBACK QUERY
# =============================================================================

async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    amount = context.user_data.get('payment_amount')
    user_wallet = context.user_data.get('user_wallet')
    
    if not amount or not user_wallet:
        await query.edit_message_text("❌ Информация о платеже не найдена")
        return
    
    # Проверяем, не истекло ли время
    payment_time = context.user_data.get('payment_time')
    if payment_time and datetime.now() - payment_time > timedelta(minutes=5):
        await query.edit_message_text("⏰ Время на оплату истекло")
        return
    
    # Показываем индикатор загрузки
    await query.edit_message_text("🔄 Проверяем платеж...")
    
    # Проверяем платежи пользователя через новый API
    result = payment_client.check_user_payments(user_wallet)
    
    if result.get("success"):
        payments = result.get("payments", [])
        
        # Ищем платеж с нужной суммой
        matching_payment = None
        for payment in payments:
            if abs(payment["amount"] - amount) < 0.01:  # Учитываем погрешность
                matching_payment = payment
                break
        
        if matching_payment:
            # Платеж найден и подтвержден
            tx_hash = matching_payment.get('tx_hash', 'N/A')
            
            success_message = f"""
✅ **Платеж подтвержден!**

💰 **Сумма:** {amount} USDT
🏦 **Ваш кошелек:** `{user_wallet}`
🔗 **Хеш транзакции:** `{tx_hash}`

🎉 Спасибо за оплату!
            """
            
            keyboard = [
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                success_message, 
                reply_markup=reply_markup, 
                parse_mode='Markdown'
            )
            
            # Обрабатываем успешный платеж
            await process_successful_payment(user_id, amount, tx_hash, context)
            
        else:
            # Платеж не найден
            error_message = f"""
❌ **Платеж не найден**

💰 **Ожидаемая сумма:** {amount} USDT
🏦 **Ваш кошелек:** `{user_wallet}`

💡 **Возможные причины:**
• Платеж еще не поступил (подождите 1-2 минуты)
• Неверная сумма
• Платеж не подтвержден в блокчейне

🔄 Попробуйте проверить еще раз через минуту
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_payment_{amount}")],
                [InlineKeyboardButton("❌ Отменить", callback_data="cancel_payment")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                error_message, 
                reply_markup=reply_markup, 
                parse_mode='Markdown'
            )
    else:
        # Ошибка API
        error_message = f"""
❌ **Ошибка проверки платежа**

Ошибка: {result.get('error', 'Неизвестная ошибка')}

🔄 Попробуйте проверить еще раз
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_payment_{amount}")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            error_message, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )

async def cancel_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки отмены платежа"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем данные о платеже
    context.user_data.pop('payment_amount', None)
    context.user_data.pop('user_wallet', None)
    context.user_data.pop('active_wallet', None)
    context.user_data.pop('payment_time', None)
    context.user_data.pop('payment_id', None)
    
    await query.edit_message_text("❌ Платеж отменен")

async def process_successful_payment(user_id: int, amount: float, tx_hash: str, context: ContextTypes.DEFAULT_TYPE):
    """Обработка успешного платежа"""
    try:
        # Добавляем средства на баланс пользователя
        add_user_balance(user_id, amount)
        
        # Отмечаем платеж как подтвержденный в базе данных
        payment_id = context.user_data.get('payment_id')
        if payment_id:
            mark_payment_confirmed(payment_id, tx_hash)
        
        # Очищаем данные о платеже
        context.user_data.pop('payment_amount', None)
        context.user_data.pop('user_wallet', None)
        context.user_data.pop('active_wallet', None)
        context.user_data.pop('payment_time', None)
        context.user_data.pop('payment_id', None)
        
        logger.info(f"Успешный платеж: пользователь {user_id}, сумма {amount} USDT, хеш {tx_hash}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки успешного платежа: {e}")

# =============================================================================
# АВТОМАТИЧЕСКАЯ ПРОВЕРКА ПЛАТЕЖЕЙ
# =============================================================================

async def auto_check_payments():
    """Автоматическая проверка ожидающих платежей"""
    try:
        # Получаем все ожидающие платежи
        pending_payments = get_pending_payments()
        
        for payment in pending_payments:
            user_id = payment['user_id']
            amount = payment['amount']
            wallet = payment['wallet_address']
            payment_id = payment['id']
            
            # Проверяем платеж
            result = payment_client.verify_payment(wallet, amount)
            
            if result.get("success") and result.get("confirmed"):
                # Платеж подтвержден
                tx_hash = result.get('tx_hash', 'N/A')
                
                # Отмечаем как подтвержденный
                mark_payment_confirmed(payment_id, tx_hash)
                
                # Добавляем средства на баланс
                add_user_balance(user_id, amount)
                
                logger.info(f"Автоматически подтвержден платеж: пользователь {user_id}, сумма {amount} USDT")
                
    except Exception as e:
        logger.error(f"Ошибка автоматической проверки платежей: {e}")

# =============================================================================
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ
# =============================================================================

def register_payment_handlers(application):
    """Регистрация обработчиков платежей"""
    
    # Команды
    application.add_handler(CommandHandler("pay", pay_command))
    application.add_handler(CommandHandler("setwallet", setwallet_command))
    application.add_handler(CommandHandler("walletbalance", wallet_balance_command))
    
    # Callback queries
    application.add_handler(CallbackQueryHandler(check_payment_callback, pattern="^check_payment_"))
    application.add_handler(CallbackQueryHandler(cancel_payment_callback, pattern="^cancel_payment$"))

def start_auto_payment_checker():
    """Запуск автоматической проверки платежей"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_check_payments, 'interval', minutes=1)
    scheduler.start()
    logger.info("Автоматическая проверка платежей запущена")

# =============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ В ОСНОВНОМ БОТЕ
# =============================================================================

"""
# В вашем основном файле бота добавьте:

from payment_integration_example import register_payment_handlers, start_auto_payment_checker

def main():
    # ... ваш существующий код ...
    
    # Регистрируем обработчики платежей
    register_payment_handlers(application)
    
    # Запускаем автоматическую проверку платежей
    start_auto_payment_checker()
    
    # ... остальной код ...
    
    application.run_polling()

if __name__ == '__main__':
    main()
"""

# =============================================================================
# ТЕСТИРОВАНИЕ
# =============================================================================

async def test_payment_client():
    """Тестирование клиента платежей"""
    print("🧪 Тестирование Payment Client...")
    
    # Тест получения кошелька для платежа
    test_user_wallet = "TTestUserWallet123456789"
    result = payment_client.get_payment_wallet(test_user_wallet)
    print(f"Получение кошелька для платежа: {result}")
    
    # Тест проверки платежей пользователя
    result = payment_client.check_user_payments(test_user_wallet)
    print(f"Проверка платежей пользователя: {result}")
    
    # Тест получения информации о кошельке
    test_wallet = "TJR44gwdyGhLa4833zJtutNepRoNVFpMzX"
    result = payment_client.get_wallet_info(test_wallet)
    print(f"Информация о кошельке: {result}")

if __name__ == "__main__":
    # Запуск тестов
    asyncio.run(test_payment_client())
