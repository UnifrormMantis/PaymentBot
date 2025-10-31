#!/usr/bin/env python3
"""
Пример интеграции Payment Bot API в ваш второй бот
Показывает, как добавить платежи в существующий бот
"""

import asyncio
import aiohttp
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YourBotWithPayments:
    """
    Ваш бот с интегрированными платежами через API
    """
    
    def __init__(self, bot_token: str, payment_api_url: str = "http://localhost:8000"):
        self.bot_token = bot_token
        self.payment_api_url = payment_api_url
        self.session = None
    
    async def start(self):
        """Запуск бота"""
        # Создаем HTTP сессию для API запросов
        self.session = aiohttp.ClientSession()
        
        # Создаем приложение
        self.application = Application.builder().token(self.bot_token).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("pay", self.pay_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("setup_wallet", self.setup_wallet_command))
        
        # Добавляем обработчик callback запросов
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        print("🤖 Ваш бот с платежами запущен!")
        print(f"💳 API платежей: {self.payment_api_url}")
        
        # Запускаем бота
        self.application.run_polling()
    
    async def stop(self):
        """Остановка бота"""
        if self.session:
            await self.session.close()
        print("🛑 Бот остановлен!")
    
    # API методы для работы с платежами
    async def create_payment(self, user_id: int, amount: float, description: str = None):
        """Создание платежа через API"""
        try:
            async with self.session.post(
                f"{self.payment_api_url}/payment/create",
                json={
                    "user_id": user_id,
                    "amount": amount,
                    "currency": "USDT",
                    "description": description
                }
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_auto_payment(self, user_id: int, wallet_address: str):
        """Настройка автоматического платежа через API"""
        try:
            async with self.session.post(
                f"{self.payment_api_url}/payment/auto",
                json={
                    "user_id": user_id,
                    "wallet_address": wallet_address,
                    "description": "Автоматический платеж"
                }
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            logger.error(f"Ошибка настройки автоматического платежа: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_balance(self, user_id: int):
        """Получение баланса через API"""
        try:
            async with self.session.get(
                f"{self.payment_api_url}/payment/balance/{user_id}"
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_payment_status(self, user_id: int):
        """Получение статуса платежей через API"""
        try:
            async with self.session.get(
                f"{self.payment_api_url}/payment/status/{user_id}"
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            logger.error(f"Ошибка получения статуса платежей: {e}")
            return {"success": False, "error": str(e)}
    
    # Обработчики команд
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        
        keyboard = [
            [InlineKeyboardButton("💳 Создать платеж", callback_data="create_payment")],
            [InlineKeyboardButton("💰 Мой баланс", callback_data="check_balance")],
            [InlineKeyboardButton("📊 История платежей", callback_data="payment_history")],
            [InlineKeyboardButton("⚙️ Настроить кошелек", callback_data="setup_wallet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 Добро пожаловать в бот с платежами!\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def pay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /pay - создание платежа"""
        user_id = update.effective_user.id
        
        # Получаем сумму из аргументов команды
        if not context.args:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ Укажите сумму платежа!\n\n"
                "Пример: /pay 100",
                reply_markup=reply_markup
            )
            return
        
        try:
            amount = float(context.args[0])
        except ValueError:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ Неверная сумма!\n\n"
                "Пример: /pay 100",
                reply_markup=reply_markup
            )
            return
        
        # Создаем платеж
        result = await self.create_payment(
            user_id=user_id,
            amount=amount,
            description=f"Платеж от пользователя {user_id}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if result['success']:
            data = result['data']
            await update.message.reply_text(
                f"✅ Платеж создан!\n\n"
                f"💰 Сумма: {amount} USDT\n"
                f"📱 Кошелек: `{data['wallet_address']}`\n"
                f"🆔 ID платежа: {data['payment_id']}\n\n"
                f"Отправьте {amount} USDT на указанный кошелек для подтверждения платежа.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка создания платежа: {result['error']}",
                reply_markup=reply_markup
            )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /balance - проверка баланса"""
        user_id = update.effective_user.id
        
        result = await self.get_balance(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if result['success']:
            await update.message.reply_text(
                f"💰 Баланс кошелька:\n\n"
                f"📱 Адрес: `{result['wallet_address']}`\n"
                f"💵 {result['currency']}: {result['balance']:.2f}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ {result['error']}\n\n"
                "Сначала настройте кошелек командой /setup_wallet",
                reply_markup=reply_markup
            )
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /history - история платежей"""
        user_id = update.effective_user.id
        
        result = await self.get_payment_status(user_id)
        
        if result['success']:
            data = result['data']
            pending = data['pending_payments']
            confirmed = data['confirmed_payments']
            
            message = "📊 История платежей:\n\n"
            
            if pending:
                message += "⏳ Ожидающие платежи:\n"
                for payment in pending[:5]:  # Показываем последние 5
                    message += f"💰 {payment['amount']} {payment['currency']}\n"
                message += "\n"
            
            if confirmed:
                message += "✅ Подтвержденные платежи:\n"
                for payment in confirmed[:5]:  # Показываем последние 5
                    message += f"💰 {payment['amount']} {payment['currency']}\n"
                    message += f"🔗 `{payment['transaction_hash']}`\n"
                    message += f"📅 {payment['confirmed_at']}\n\n"
            else:
                message += "📭 Подтвержденных платежей пока нет\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"❌ {result['error']}", reply_markup=reply_markup)
    
    async def setup_wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /setup_wallet - настройка кошелька"""
        user_id = update.effective_user.id
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ Настройка кошелька\n\n"
            "Отправьте адрес вашего Tron кошелька:\n\n"
            "Пример: `TYourAddress1234567890123456789012345`\n\n"
            "После настройки все платежи на этот кошелек будут автоматически зачислены!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_wallet_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка адреса кошелька"""
        user_id = update.effective_user.id
        wallet_address = update.message.text.strip()
        
        # Валидация адреса
        if not wallet_address.startswith('T') or len(wallet_address) != 34:
            await update.message.reply_text(
                "❌ Неверный формат адреса кошелька!\n\n"
                "Адрес должен начинаться с 'T' и содержать 34 символа.\n"
                "Пример: TYourAddress1234567890123456789012345"
            )
            return
        
        # Настраиваем автоматический платеж
        result = await self.setup_auto_payment(user_id, wallet_address)
        
        if result['success']:
            await update.message.reply_text(
                f"✅ Кошелек настроен!\n\n"
                f"📱 Адрес: `{wallet_address}`\n"
                f"🤖 Режим: Автоматическое зачисление\n\n"
                f"Теперь все платежи на этот кошелек будут автоматически зачислены!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка настройки кошелька: {result['error']}"
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "create_payment":
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "💳 Создание платежа\n\n"
                "Используйте команду /pay <сумма>\n\n"
                "Пример: /pay 100",
                reply_markup=reply_markup
            )
        elif data == "check_balance":
            result = await self.get_balance(user_id)
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if result['success']:
                await query.edit_message_text(
                    f"💰 Баланс: {result['balance']:.2f} {result['currency']}\n"
                    f"📱 Кошелек: `{result['wallet_address']}`",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    f"❌ {result['error']}",
                    reply_markup=reply_markup
                )
        elif data == "payment_history":
            await self.history_command(update, context)
        elif data == "setup_wallet":
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "⚙️ Настройка кошелька\n\n"
                "Отправьте адрес вашего Tron кошелька:\n\n"
                "Пример: `TYourAddress1234567890123456789012345`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif data == "main_menu":
            # Возвращаемся к главному меню
            keyboard = [
                [InlineKeyboardButton("💳 Создать платеж", callback_data="create_payment")],
                [InlineKeyboardButton("💰 Мой баланс", callback_data="check_balance")],
                [InlineKeyboardButton("📊 История платежей", callback_data="payment_history")],
                [InlineKeyboardButton("⚙️ Настроить кошелек", callback_data="setup_wallet")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🤖 Добро пожаловать в бот с платежами!\n\n"
                "Выберите действие:",
                reply_markup=reply_markup
            )

# Пример использования
async def main():
    """Главная функция"""
    # Замените на токен вашего бота
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    PAYMENT_API_URL = "http://localhost:8000"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("❌ Ошибка: Замените YOUR_BOT_TOKEN на токен вашего бота!")
        return
    
    # Создаем бота
    bot = YourBotWithPayments(BOT_TOKEN, PAYMENT_API_URL)
    
    try:
        # Запускаем бота
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Останавливаем бота
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())





