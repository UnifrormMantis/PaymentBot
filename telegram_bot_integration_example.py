#!/usr/bin/env python3
"""
Пример интеграции платежного бота в Telegram бота
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
from payment_integration_client import PaymentBotClient

# Конфигурация
PAYMENT_API_KEY = "U0LcNppTYxc3EO0sXIyTQQ-OKrFDVwt3qLoNto9VakI"
PAYMENT_BASE_URL = "http://localhost:8001"

# Инициализация клиента платежей
payment_client = PaymentBotClient(PAYMENT_API_KEY, PAYMENT_BASE_URL)

class PaymentBotIntegration:
    """Интеграция платежного бота в основной бот"""
    
    def __init__(self, application: Application):
        self.application = application
        self.payment_client = payment_client
        
        # Регистрируем обработчики
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация обработчиков команд и кнопок"""
        # Команды
        self.application.add_handler(CommandHandler("pay", self.payment_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        
        # Обработчики кнопок
        self.application.add_handler(CallbackQueryHandler(self.check_payment_callback, pattern="^check_payment_"))
        self.application.add_handler(CallbackQueryHandler(self.wallet_balance_callback, pattern="^wallet_balance$"))
        self.application.add_handler(CallbackQueryHandler(self.payment_history_callback, pattern="^payment_history$"))
        self.application.add_handler(CallbackQueryHandler(self.main_menu_callback, pattern="^main_menu$"))
    
    async def payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /pay"""
        user_id = update.effective_user.id
        
        # Получаем сумму из аргументов команды
        if not context.args:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **Укажите сумму для оплаты!**\n\n"
                "Пример: `/pay 10.50`\n"
                "Минимальная сумма: 1 USDT",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        try:
            amount = float(context.args[0])
            if amount < 1.0:
                keyboard = [
                    [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "❌ **Минимальная сумма: 1 USDT**",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return
        except ValueError:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **Неверный формат суммы!**\n\n"
                "Пример: `/pay 10.50`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Создаем платеж
        payment = self.payment_client.create_payment(
            user_id=user_id,
            amount=amount,
            currency="USDT",
            description=f"Платеж от пользователя {update.effective_user.first_name}"
        )
        
        if payment.get('success'):
            # Создаем клавиатуру
            keyboard = [
                [InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_payment_{payment['payment_id']}")],
                [InlineKeyboardButton("💰 Баланс кошелька", callback_data="wallet_balance")],
                [InlineKeyboardButton("📋 История платежей", callback_data="payment_history")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
💳 **Платеж создан успешно!**

💰 **Сумма:** {payment['amount']} {payment['currency']}
🏦 **Кошелек:** `{payment['wallet_address']}`
🆔 **ID платежа:** `{payment['payment_id']}`

**📋 Инструкция:**
1️⃣ Отправьте **{payment['amount']} {payment['currency']}** на указанный кошелек
2️⃣ Нажмите **"✅ Проверить оплату"** после отправки
3️⃣ Платеж будет подтвержден автоматически

⚠️ **Важно:** 
• Отправляйте **точную сумму**
• Используйте **USDT (TRC20)**
• Сохраните ID платежа для отслеживания

🔄 **Статус:** {payment['status']}
            """
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"❌ **Ошибка создания платежа**\n\n"
                f"Причина: {payment.get('error', 'Неизвестная ошибка')}\n\n"
                f"Попробуйте позже или обратитесь в поддержку.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /balance"""
        balance = self.payment_client.get_wallet_balance()
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if balance.get('success'):
            message = f"""
💰 **Баланс кошелька**

💵 **Сумма:** {balance['balance']} {balance['currency']}
🏦 **Адрес:** `{balance['wallet_address']}`

💡 **Для пополнения:** используйте команду `/pay`
            """
        else:
            message = f"""
❌ **Ошибка получения баланса**

Причина: {balance.get('error', 'Неизвестная ошибка')}

Попробуйте позже.
            """
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /history"""
        user_id = update.effective_user.id
        
        # Получаем лимит из аргументов
        limit = 5
        if context.args:
            try:
                limit = int(context.args[0])
                limit = min(max(limit, 1), 20)  # Ограничиваем от 1 до 20
            except ValueError:
                pass
        
        history = self.payment_client.get_payment_history(user_id, limit)
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if history.get('success'):
            payments = history.get('payments', [])
            
            if payments:
                message = f"📋 **История платежей** (последние {len(payments)})\n\n"
                
                for payment in payments:
                    status_emoji = "✅" if payment['status'] == 'confirmed' else "⏳"
                    message += f"{status_emoji} **{payment['amount']} {payment['currency']}** - {payment['status']}\n"
                    message += f"   ID: `{payment['payment_id']}`\n"
                    if payment.get('confirmed_at'):
                        message += f"   Время: {payment['confirmed_at']}\n"
                    message += "\n"
            else:
                message = "📋 **История платежей пуста**\n\nСоздайте первый платеж командой `/pay`"
        else:
            message = f"""
❌ **Ошибка получения истории**

Причина: {history.get('error', 'Неизвестная ошибка')}

Попробуйте позже.
            """
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def check_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки проверки платежа"""
        query = update.callback_query
        await query.answer()
        
        payment_id = query.data.split("_")[2]
        
        # Показываем индикатор загрузки
        await query.edit_message_text("⏳ Проверяем статус платежа...")
        
        status = self.payment_client.get_payment_status(payment_id)
        
        if status.get('success'):
            if status['status'] == 'confirmed':
                message = f"""
✅ **Платеж подтвержден!**

💰 **Сумма:** {status['amount']} {status['currency']}
🔗 **Транзакция:** `{status.get('transaction_hash', 'N/A')}`
⏰ **Время подтверждения:** {status.get('confirmed_at', 'N/A')}
🆔 **ID платежа:** `{payment_id}`

🎉 **Спасибо за оплату!**
                """
            elif status['status'] == 'pending':
                message = f"""
⏳ **Платеж в обработке**

💰 **Сумма:** {status['amount']} {status['currency']}
🆔 **ID платежа:** `{payment_id}`

**Статус:** {status['status']}

💡 **Попробуйте проверить через несколько минут**
                """
            else:
                message = f"""
❓ **Неизвестный статус платежа**

🆔 **ID платежа:** `{payment_id}`
**Статус:** {status['status']}

💡 **Обратитесь в поддержку**
                """
        else:
            message = f"""
❌ **Ошибка проверки платежа**

🆔 **ID платежа:** `{payment_id}`
**Причина:** {status.get('error', 'Неизвестная ошибка')}

💡 **Попробуйте позже или обратитесь в поддержку**
            """
        
        # Создаем кнопку для повторной проверки
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить снова", callback_data=f"check_payment_{payment_id}")],
            [InlineKeyboardButton("💰 Баланс", callback_data="wallet_balance")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def wallet_balance_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки баланса кошелька"""
        query = update.callback_query
        await query.answer()
        
        balance = self.payment_client.get_wallet_balance()
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if balance.get('success'):
            message = f"""
💰 **Баланс кошелька**

💵 **Сумма:** {balance['balance']} {balance['currency']}
🏦 **Адрес:** `{balance['wallet_address']}`

💡 **Для пополнения:** используйте команду `/pay`
            """
        else:
            message = f"""
❌ **Ошибка получения баланса**

Причина: {balance.get('error', 'Неизвестная ошибка')}

Попробуйте позже.
            """
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def payment_history_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки истории платежей"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        history = self.payment_client.get_payment_history(user_id, 5)
        
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if history.get('success'):
            payments = history.get('payments', [])
            
            if payments:
                message = f"📋 **История платежей** (последние {len(payments)})\n\n"
                
                for payment in payments:
                    status_emoji = "✅" if payment['status'] == 'confirmed' else "⏳"
                    message += f"{status_emoji} **{payment['amount']} {payment['currency']}** - {payment['status']}\n"
                    message += f"   ID: `{payment['payment_id']}`\n\n"
            else:
                message = "📋 **История платежей пуста**\n\nСоздайте первый платеж командой `/pay`"
        else:
            message = f"""
❌ **Ошибка получения истории**

Причина: {history.get('error', 'Неизвестная ошибка')}

Попробуйте позже.
            """
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Главное меню'"""
        query = update.callback_query
        await query.answer()
        
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


# Пример использования в основном боте
async def main():
    """Пример запуска бота с интеграцией платежей"""
    # Замените на ваш токен бота
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Инициализируем интеграцию платежей
    payment_integration = PaymentBotIntegration(application)
    
    # Добавляем базовые команды
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 **Добро пожаловать!**\n\n"
            "Доступные команды:\n"
            "• `/pay <сумма>` - создать платеж\n"
            "• `/balance` - баланс кошелька\n"
            "• `/history` - история платежей\n"
            "• `/help` - помощь",
            parse_mode='Markdown'
        )
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    
    # Запускаем бота
    print("🚀 Запуск бота с интеграцией платежей...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


