#!/usr/bin/env python3
"""
Пример интеграции платежной системы в ваш бот
Показывает, как добавить TRC20 платежи в существующий бот
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from payment_integration import PaymentIntegration
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class YourBotWithPayments:
    """
    Ваш бот с интегрированной платежной системой
    """
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.payment_system = PaymentIntegration(bot_token)
        
        # Регистрируем callback для уведомлений о платежах
        self.payment_system.register_payment_callback(
            user_id=0,  # Будет заменен на реальный user_id
            callback=self.on_payment_received
        )
    
    async def on_payment_received(self, user_id: int, amount: float, 
                                currency: str, transaction_hash: str, 
                                wallet_address: str):
        """
        Обработчик получения платежа
        Вызывается автоматически при поступлении платежа
        """
        try:
            # Отправляем уведомление пользователю
            message = (
                f"🎉 Получен платеж!\n\n"
                f"💰 Сумма: {amount:.2f} {currency}\n"
                f"🔗 Транзакция: `{transaction_hash}`\n"
                f"📱 Кошелек: `{wallet_address}`\n\n"
                f"✅ Платеж автоматически зачислен!"
            )
            
            # Здесь можно добавить логику обработки платежа
            # Например, активация подписки, пополнение баланса и т.д.
            await self.process_payment_logic(user_id, amount, currency)
            
            logger.info(f"Платеж обработан для пользователя {user_id}: {amount} {currency}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки платежа: {e}")
    
    async def process_payment_logic(self, user_id: int, amount: float, currency: str):
        """
        Ваша логика обработки платежа
        Здесь можно добавить:
        - Активацию подписки
        - Пополнение баланса
        - Выдачу товаров/услуг
        - Уведомления администратора
        """
        # Пример: активация подписки на основе суммы
        if amount >= 100:
            await self.activate_premium_subscription(user_id)
        elif amount >= 50:
            await self.activate_standard_subscription(user_id)
        else:
            await self.add_credits(user_id, amount)
    
    async def activate_premium_subscription(self, user_id: int):
        """Активация премиум подписки"""
        # Ваша логика активации подписки
        logger.info(f"Активирована премиум подписка для пользователя {user_id}")
    
    async def activate_standard_subscription(self, user_id: int):
        """Активация стандартной подписки"""
        # Ваша логика активации подписки
        logger.info(f"Активирована стандартная подписка для пользователя {user_id}")
    
    async def add_credits(self, user_id: int, amount: float):
        """Добавление кредитов"""
        # Ваша логика добавления кредитов
        logger.info(f"Добавлено {amount} кредитов для пользователя {user_id}")
    
    # Обработчики команд вашего бота
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Добавляем пользователя в базу данных платежной системы
        from database import Database
        db = Database()
        db.add_user(user_id, username, "")
        
        # Регистрируем callback для этого пользователя
        self.payment_system.register_payment_callback(
            user_id=user_id,
            callback=self.on_payment_received
        )
        
        keyboard = [
            [InlineKeyboardButton("💳 Настроить платежи", callback_data="setup_payments")],
            [InlineKeyboardButton("💰 Мой баланс", callback_data="check_balance")],
            [InlineKeyboardButton("📊 История платежей", callback_data="payment_history")],
            [InlineKeyboardButton("🛒 Купить подписку", callback_data="buy_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 Добро пожаловать в бот с платежной системой!\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def setup_payments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда настройки платежей"""
        user_id = update.effective_user.id
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💳 Настройка платежей\n\n"
            "Для настройки платежей отправьте адрес вашего Tron кошелька:\n\n"
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
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ Неверный формат адреса кошелька!\n\n"
                "Адрес должен начинаться с 'T' и содержать 34 символа.\n"
                "Пример: TYourAddress1234567890123456789012345",
                reply_markup=reply_markup
            )
            return
        
        # Настраиваем автоматический платеж
        result = await self.payment_system.create_auto_payment_request(
            user_id=user_id,
            wallet_address=wallet_address,
            description="Автоматический платеж"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if result['success']:
            await update.message.reply_text(
                f"✅ Кошелек настроен!\n\n"
                f"📱 Адрес: `{wallet_address}`\n"
                f"🤖 Режим: Автоматическое зачисление\n\n"
                f"Теперь все платежи на этот кошелек будут автоматически зачислены!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка настройки кошелька: {result['error']}",
                reply_markup=reply_markup
            )
    
    async def check_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда проверки баланса"""
        user_id = update.effective_user.id
        
        result = await self.payment_system.get_wallet_balance(user_id)
        
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
                "Сначала настройте кошелек командой /setup_payments",
                reply_markup=reply_markup
            )
    
    async def payment_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда истории платежей"""
        user_id = update.effective_user.id
        
        result = await self.payment_system.check_payment_status(user_id)
        
        if result['success']:
            confirmed_payments = result['confirmed_payments']
            
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if confirmed_payments:
                message = "📊 История платежей:\n\n"
                for payment in confirmed_payments[:10]:  # Показываем последние 10
                    message += (
                        f"💰 {payment['amount']:.2f} {payment['currency']}\n"
                        f"🔗 `{payment['transaction_hash']}`\n"
                        f"📅 {payment['confirmed_at']}\n\n"
                    )
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text("📊 Платежей пока нет", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"❌ {result['error']}", reply_markup=reply_markup)
    
    async def buy_subscription_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда покупки подписки"""
        keyboard = [
            [InlineKeyboardButton("🥉 Стандарт - 50 USDT", callback_data="buy_standard")],
            [InlineKeyboardButton("🥇 Премиум - 100 USDT", callback_data="buy_premium")],
            [InlineKeyboardButton("💎 VIP - 200 USDT", callback_data="buy_vip")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🛒 Выберите подписку:\n\n"
            "🥉 Стандарт - 50 USDT\n"
            "🥇 Премиум - 100 USDT\n"
            "💎 VIP - 200 USDT\n\n"
            "После оплаты подписка активируется автоматически!",
            reply_markup=reply_markup
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "setup_payments":
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "💳 Настройка платежей\n\n"
                "Отправьте адрес вашего Tron кошелька:\n\n"
                "Пример: `TYourAddress1234567890123456789012345`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif data == "check_balance":
            result = await self.payment_system.get_wallet_balance(user_id)
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
            await self.payment_history_command(update, context)
        elif data == "buy_subscription":
            await self.buy_subscription_command(update, context)
        elif data.startswith("buy_"):
            subscription_type = data.split("_")[1]
            await self.handle_subscription_purchase(query, subscription_type)
        elif data == "main_menu":
            # Возвращаемся к главному меню
            keyboard = [
                [InlineKeyboardButton("💳 Настроить платежи", callback_data="setup_payments")],
                [InlineKeyboardButton("💰 Мой баланс", callback_data="check_balance")],
                [InlineKeyboardButton("📊 История платежей", callback_data="payment_history")],
                [InlineKeyboardButton("🛒 Купить подписку", callback_data="buy_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🤖 Добро пожаловать в бот с платежной системой!\n\n"
                "Выберите действие:",
                reply_markup=reply_markup
            )
    
    async def handle_subscription_purchase(self, query, subscription_type: str):
        """Обработка покупки подписки"""
        user_id = query.from_user.id
        
        # Создаем платеж
        amount = {"standard": 50, "premium": 100, "vip": 200}[subscription_type]
        
        result = await self.payment_system.create_payment_request(
            user_id=user_id,
            amount=amount,
            currency="USDT",
            description=f"Подписка {subscription_type.title()}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if result['success']:
            await query.edit_message_text(
                f"💳 Создан платеж на {amount} USDT\n\n"
                f"📱 Кошелек: `{result['wallet_address']}`\n"
                f"💰 Сумма: {amount} USDT\n\n"
                f"После поступления платежа подписка активируется автоматически!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ Ошибка создания платежа: {result['error']}",
                reply_markup=reply_markup
            )
    
    async def process_payments_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Задача обработки платежей (вызывается периодически)"""
        await self.payment_system.process_payments()
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(self.bot_token).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("setup_payments", self.setup_payments_command))
        application.add_handler(CommandHandler("balance", self.check_balance_command))
        application.add_handler(CommandHandler("history", self.payment_history_command))
        application.add_handler(CommandHandler("buy", self.buy_subscription_command))
        
        # Добавляем обработчик callback запросов
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Добавляем обработчик текстовых сообщений (для адресов кошельков)
        from telegram.ext import MessageHandler, filters
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_wallet_address))
        
        # Добавляем задачу обработки платежей
        application.job_queue.run_repeating(
            self.process_payments_task,
            interval=config.CHECK_INTERVAL,
            first=10
        )
        
        print("🤖 Бот с платежной системой запущен!")
        print("💳 Интегрированы TRC20 платежи")
        print(f"⏰ Интервал проверки: {config.CHECK_INTERVAL} секунд")
        
        # Запускаем бота
        application.run_polling()

if __name__ == "__main__":
    # Замените на токен вашего бота
    BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    
    if not BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен!")
        exit(1)
    
    bot = YourBotWithPayments(BOT_TOKEN)
    bot.run()





