#!/usr/bin/env python3
"""
Приватный Telegram Bot для отслеживания TRC20 платежей
Доступ только для зарегистрированных пользователей
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database
from tron_tracker import TronTracker
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PrivatePaymentBot:
    def __init__(self):
        self.db = Database()
        self.tron_tracker = TronTracker()
        self.application = None
        
        # Whitelist пользователей (можно расширить)
        self.allowed_users = set()
        self.load_allowed_users()
    
    def load_allowed_users(self):
        """Загрузка списка разрешенных пользователей из базы данных"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Получаем всех пользователей из базы
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()
            
            for (user_id,) in users:
                self.allowed_users.add(user_id)
            
            conn.close()
            
            logger.info(f"Загружено {len(self.allowed_users)} разрешенных пользователей")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки разрешенных пользователей: {e}")
    
    def is_user_allowed(self, user_id: int) -> bool:
        """Проверка, разрешен ли пользователю доступ к боту"""
        return user_id in self.allowed_users
    
    def add_user_to_whitelist(self, user_id: int) -> bool:
        """Добавление пользователя в whitelist"""
        try:
            self.allowed_users.add(user_id)
            logger.info(f"Пользователь {user_id} добавлен в whitelist")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя в whitelist: {e}")
            return False
    
    def remove_user_from_whitelist(self, user_id: int) -> bool:
        """Удаление пользователя из whitelist"""
        try:
            if user_id in self.allowed_users:
                self.allowed_users.remove(user_id)
                logger.info(f"Пользователь {user_id} удален из whitelist")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя из whitelist: {e}")
            return False
    
    async def check_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Проверка доступа пользователя"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text(
                "🚫 **ДОСТУП ЗАПРЕЩЕН**\n\n"
                "❌ У вас нет доступа к этому боту.\n"
                "🔒 Этот бот доступен только для авторизованных пользователей.\n\n"
                "📞 Для получения доступа обратитесь к администратору.",
                parse_mode='Markdown'
            )
            return False
        
        return True
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        # Проверяем доступ
        if not await self.check_access(update, context):
            return
        
        user = update.effective_user
        user_id = user.id
        username = user.username
        
        # Добавляем пользователя в базу данных (только если его еще нет)
        existing_user = self.db.get_user(user_id)
        if not existing_user:
            self.db.add_user(user_id, username, "")
        
        # Получаем информацию о пользователе из новой системы кошельков
        active_wallet = self.db.get_active_wallet(user_id)
        user_wallets = self.db.get_user_wallets(user_id)
        
        wallet_info = ""
        if active_wallet:
            wallet_info = f"\n💳 **Активный кошелек:** `{active_wallet['wallet_address']}`"
            wallet_info += f"\n📱 **Название:** {active_wallet['wallet_name']}"
            wallet_info += f"\n📊 **Всего кошельков:** {len(user_wallets)}"
        elif user_wallets:
            wallet_info = f"\n💳 **Кошельков:** {len(user_wallets)} (нет активного)"
        else:
            wallet_info = "\n💳 **Кошельки не добавлены** - нажмите кнопку ниже"
        
        welcome_text = f"""
🤖 **ГЛАВНОЕ МЕНЮ**

Привет, {user.first_name}! 

🔒 **Приватный режим активен** - доступ только для авторизованных пользователей.
{wallet_info}

**Выберите действие:**
        """
        
        # Создаем клавиатуру с кнопками для главного меню
        keyboard = []
        
        # Основные кнопки (всегда доступны)
        keyboard.append([InlineKeyboardButton("📊 Статус", callback_data="check_status")])
        keyboard.append([InlineKeyboardButton("💰 Баланс", callback_data="check_balance")])
        keyboard.append([InlineKeyboardButton("🤖 Авто", callback_data="auto_mode")])
        
        # Кнопки управления кошельками
        if user_wallets:
            keyboard.append([InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")])
        else:
            keyboard.append([InlineKeyboardButton("💳 Добавить кошелек", callback_data="add_wallet")])
        
        # Дополнительные кнопки
        keyboard.append([InlineKeyboardButton("🔑 Получить API ключ", callback_data="get_api_key")])
        keyboard.append([InlineKeyboardButton("❓ Помощь", callback_data="show_help")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        if not await self.check_access(update, context):
            return
        
        help_text = """
📚 **СПРАВКА ПО БОТУ**

**Основные функции:**
• 💳 Управление кошельками - добавление и настройка кошельков
• 📊 Статус платежей - просмотр статистики и истории
• 💰 Баланс кошелька - проверка текущего баланса
• 🔑 API интеграция - получение ключа для интеграции

**Как использовать:**
1. Добавьте кошелек через кнопку "Управление кошельками"
2. Активируйте нужный кошелек
3. Получайте уведомления о платежах
4. Используйте API для интеграции в свои проекты

**Безопасность:**
🔒 Приватный режим - доступ только для авторизованных пользователей
✅ Все данные защищены
🛡️ Безопасное хранение кошельков
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔑 Получить API ключ", callback_data="get_api_key")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /wallet - управление кошельками"""
        if not await self.check_access(update, context):
            return
        
        user_id = update.effective_user.id
        
        # Если адрес указан, добавляем новый кошелек
        if context.args:
            wallet_address = context.args[0].strip()
            
            # Валидация адреса
            if not wallet_address.startswith('T') or len(wallet_address) != 34:
                await update.message.reply_text(
                    "❌ **Неверный формат адреса кошелька!**\n\n"
                    "Адрес должен:\n"
                    "• Начинаться с 'T'\n"
                    "• Содержать 34 символа\n\n"
                    "Пример: `TYourAddress1234567890123456789012345`",
                    parse_mode='Markdown'
                )
                return
            
            # Добавляем кошелек
            self.db.add_user_wallet(user_id, wallet_address)
            
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **Кошелек добавлен!**\n\n"
                f"📱 Адрес: `{wallet_address}`\n\n"
                f"Используйте кнопки ниже для управления кошельками",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Показываем список кошельков с кнопками
        await self.show_wallet_management(update, context)
    
    async def show_wallet_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать управление кошельками"""
        user_id = update.effective_user.id
        wallets = self.db.get_user_wallets(user_id)
        
        if not wallets:
            wallet_text = """
💳 **Управление кошельками**

📭 **У вас пока нет кошельков**

**Для добавления кошелька:**
`/wallet <адрес_кошелька>`

**Пример:**
`/wallet TYourAddress1234567890123456789012345`

**Требования:**
• Адрес должен начинаться с 'T'
• Длина адреса: 34 символа
• Только TRC20 совместимые адреса
            """
            
            keyboard = [
                [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
        else:
            wallet_text = f"""
💳 **Управление кошельками**

📊 **Всего кошельков:** {len(wallets)}

**Ваши кошельки:**
            """
            
            keyboard = []
            for wallet in wallets:
                status = "🟢 АКТИВНЫЙ" if wallet['is_active'] else "⚪ Неактивный"
                button_text = f"{status} {wallet['wallet_name']}"
                callback_data = f"wallet_{wallet['id']}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")])
            keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(wallet_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(wallet_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def auto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Включить/выключить автоматический режим зачисления платежей"""
        if not await self.check_access(update, context):
            return
        
        user_id = update.effective_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        user_data = self.db.get_user(user_id)
        current_auto_mode = user_data.get('auto_mode', False)
        new_auto_mode = not current_auto_mode
        self.db.update_user_auto_mode(user_id, new_auto_mode)

        status = "ВКЛЮЧЕН" if new_auto_mode else "ВЫКЛЮЧЕН"
        status_emoji = "✅" if new_auto_mode else "❌"
        
        auto_text = f"""
🤖 **Автоматический режим {status}!**

📱 **Активный кошелек:** {active_wallet['wallet_name']}
🏦 **Адрес:** `{active_wallet['wallet_address']}`

**Что это означает:**
• {'Любой платеж на ваш кошелек будет автоматически зачислен' if new_auto_mode else 'Платежи не будут зачисляться автоматически'}
• {'Независимо от суммы платежа' if new_auto_mode else 'Требуется ручное подтверждение'}
• {'Вы будете получать уведомления о всех поступлениях' if new_auto_mode else 'Уведомления отключены'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Переключить режим", callback_data="auto_mode")],
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(auto_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        if not await self.check_access(update, context):
            return
        
        user_id = update.effective_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        user_wallets = self.db.get_user_wallets(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        wallet_address = active_wallet['wallet_address']
        
        # Получаем ожидающие платежи
        pending_payments = self.db.get_pending_payments(wallet_address)
        
        # Получаем подтвержденные платежи
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount, currency, transaction_hash, confirmed_at
            FROM confirmed_payments 
            WHERE user_id = ?
            ORDER BY confirmed_at DESC
            LIMIT 10
        ''', (user_id,))
        confirmed_payments = cursor.fetchall()
        conn.close()
        
        status_text = f"""
📊 **Статус платежей**

📱 **Активный кошелек:** {active_wallet['wallet_name']}
🏦 **Адрес:** `{wallet_address}`
📊 **Всего кошельков:** {len(user_wallets)}

⏳ **Ожидающие платежи:** {len(pending_payments)}
✅ **Подтвержденные платежи:** {len(confirmed_payments)}
        """
        
        if pending_payments:
            status_text += "\n\n**Ожидающие платежи:**\n"
            for payment in pending_payments[:5]:  # Показываем последние 5
                status_text += f"💰 {payment['amount']} {payment['currency']}\n"
        
        if confirmed_payments:
            status_text += "\n\n**Последние подтвержденные платежи:**\n"
            for payment in confirmed_payments[:5]:  # Показываем последние 5
                status_text += f"💰 {payment[0]} {payment[1]}\n"
                status_text += f"🔗 `{payment[2]}`\n"
                status_text += f"📅 {payment[3]}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить статус", callback_data="check_status")],
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(status_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /balance"""
        if not await self.check_access(update, context):
            return
        
        user_id = update.effective_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        wallet_address = active_wallet['wallet_address']
        
        try:
            # Получаем баланс кошелька
            balance = self.tron_tracker.get_usdt_balance(wallet_address)
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить баланс", callback_data="check_balance")],
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"💰 **Баланс активного кошелька**\n\n"
                f"📱 **Название:** {active_wallet['wallet_name']}\n"
                f"🏦 **Адрес:** `{wallet_address}`\n"
                f"💵 **USDT:** {balance:.2f}\n\n"
                f"*Баланс обновляется в реальном времени*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data="check_balance")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ **Ошибка получения баланса**\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def check_payments_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Задача проверки платежей - автоматическое зачисление"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Получаем всех пользователей с включенным автоматическим режимом
            cursor.execute("SELECT user_id, wallet_address FROM users WHERE auto_mode = 1")
            users_in_auto_mode = cursor.fetchall()
            conn.close()

            for user_id, wallet_address in users_in_auto_mode:
                if not wallet_address:
                    continue

                try:
                    # Получаем новые транзакции
                    new_transfers = self.tron_tracker.get_new_transfers(wallet_address)
                    
                    for transfer in new_transfers:
                        # Проверяем, был ли этот платеж уже подтвержден
                        if not self.db.is_transaction_confirmed(transfer['tx_hash']):
                            # Автоматически подтверждаем любой платеж
                            self.db.confirm_payment(
                                user_id, 
                                transfer['amount'], 
                                transfer['currency'],
                                transfer['tx_hash'],
                                wallet_address
                            )
                            
                            # Отправляем уведомление пользователю
                            try:
                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text=f"🎉 **Получен автоматический платеж!**\n\n"
                                         f"💰 **Сумма:** {transfer['amount']} {transfer['currency']}\n"
                                         f"🔗 **Транзакция:** `{transfer['tx_hash']}`\n"
                                         f"📱 **Кошелек:** `{wallet_address}`\n\n"
                                         f"✅ **Платеж автоматически зачислен!**",
                                    parse_mode='Markdown'
                                )
                            except Exception as e:
                                logger.error(f"Ошибка отправки уведомления об авто-платеже: {e}")
                
                except Exception as e:
                    logger.error(f"Ошибка обработки платежей для пользователя {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка в задаче проверки платежей: {e}")
    
    # Административные команды (только для определенных пользователей)
    async def admin_add_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление пользователя в whitelist (только для админов)"""
        user_id = update.effective_user.id
        
        # Проверяем, является ли пользователь админом
        if user_id not in [8489431460]:  # ID администраторов
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ID пользователя!\n\n"
                "Пример: /admin_add_user 123456789"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            
            if self.add_user_to_whitelist(target_user_id):
                await update.message.reply_text(
                    f"✅ Пользователь {target_user_id} добавлен в whitelist."
                )
            else:
                await update.message.reply_text(
                    f"❌ Ошибка добавления пользователя {target_user_id}."
                )
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID пользователя.")
    
    async def admin_remove_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление пользователя из whitelist (только для админов)"""
        user_id = update.effective_user.id
        
        # Проверяем, является ли пользователь админом
        if user_id not in [8489431460]:  # ID администраторов
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ID пользователя!\n\n"
                "Пример: /admin_remove_user 123456789"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
            
            if self.remove_user_from_whitelist(target_user_id):
                await update.message.reply_text(
                    f"✅ Пользователь {target_user_id} удален из whitelist."
                )
            else:
                await update.message.reply_text(
                    f"❌ Пользователь {target_user_id} не найден в whitelist."
                )
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID пользователя.")
    
    async def admin_list_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Список пользователей в whitelist (только для админов)"""
        user_id = update.effective_user.id
        
        # Проверяем, является ли пользователь админом
        if user_id not in [8489431460]:  # ID администраторов
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        users_list = list(self.allowed_users)
        users_text = f"👥 **Пользователи в whitelist ({len(users_list)}):**\n\n"
        
        for i, user_id in enumerate(users_list, 1):
            users_text += f"{i}. `{user_id}`\n"
        
        await update.message.reply_text(users_text, parse_mode='Markdown')
    
    async def api_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для получения API информации"""
        if not await self.check_access(update, context):
            return
        
        user_id = update.effective_user.id
        
        # Создаем клавиатуру с кнопкой для получения API ключа
        keyboard = [
            [InlineKeyboardButton("🔑 Получить API ключ", callback_data="get_api_key")],
            [InlineKeyboardButton("📚 Документация", callback_data="api_docs")],
            [InlineKeyboardButton("💡 Примеры", callback_data="api_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        api_info = f"""
🔗 **API для интеграции бота**

🚀 **ПРОСТОЙ API (как у популярных ботов):**
• Один API ключ - и все работает!
• Автоматическая проверка платежей
• Callback уведомления
• Работает с любым языком программирования

🌐 **Базовый URL:** `http://localhost:8001`

📡 **Основные endpoints:**
• `GET /get-api-key` - Получить API ключ
• `POST /create-payment` - Создать платеж
• `GET /check-payment/{{id}}` - Проверить статус
• `GET /health` - Проверка здоровья

🎯 **Нажмите кнопку ниже для получения API ключа!**
        """
        
        await update.message.reply_text(api_info, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def get_api_key_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение API ключа через кнопку"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        try:
            # Получаем API ключ от простого API
            import requests
            response = requests.get("http://localhost:8001/get-api-key", timeout=10)
            
            if response.status_code == 200:
                api_data = response.json()
                api_key = api_data['api_key']
                
                # Сохраняем API ключ для пользователя в базе данных
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Создаем таблицу для API ключей если её нет
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_api_keys (
                        user_id INTEGER PRIMARY KEY,
                        api_key TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Сохраняем API ключ пользователя
                cursor.execute('''
                    INSERT OR REPLACE INTO user_api_keys (user_id, api_key)
                    VALUES (?, ?)
                ''', (user_id, api_key))
                
                conn.commit()
                conn.close()
                
                api_key_info = f"""
🔑 **ВАШ API КЛЮЧ:**

```
{api_key}
```

🌐 **Базовый URL:** `http://localhost:8001`

💡 **Примеры использования:**

**Создать платеж:**
```bash
curl -X POST http://localhost:8001/create-payment \\
     -H "X-API-Key: {api_key}" \\
     -H "Content-Type: application/json" \\
     -d '{{"amount": 100.0, "currency": "USDT"}}'
```

**Python:**
```python
from simple_client import SimplePaymentClient

client = SimplePaymentClient("{api_key}")
result = client.create_payment(100.0, "USDT")
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8001/create-payment', {{
    method: 'POST',
    headers: {{
        'X-API-Key': '{api_key}',
        'Content-Type': 'application/json'
    }},
    body: JSON.stringify({{amount: 100.0, currency: 'USDT'}})
}});
```

📚 **Документация:** http://localhost:8001/docs

⚠️ **Сохраните этот ключ в безопасном месте!**
                """
                
                await query.edit_message_text(api_key_info, parse_mode='Markdown')
                
            else:
                await query.edit_message_text(
                    "❌ **Ошибка получения API ключа**\n\n"
                    "Проверьте, что Simple API запущен:\n"
                    "```bash\n./start_simple_api.sh\n```",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Ошибка:** {str(e)}\n\n"
                "Убедитесь, что Simple API запущен на порту 8001",
                parse_mode='Markdown'
            )
    
    async def api_docs_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать документацию API"""
        query = update.callback_query
        await query.answer()
        
        docs_info = """
📚 **ДОКУМЕНТАЦИЯ API**

🌐 **Swagger UI:** http://localhost:8001/docs

📡 **Endpoints:**
• `GET /get-api-key` - Получить API ключ
• `POST /create-payment` - Создать платеж
• `GET /check-payment/{id}` - Проверить статус
• `GET /health` - Проверка здоровья

🔑 **Авторизация:**
Заголовок: `X-API-Key: your_api_key`

📖 **Полное руководство:** `SIMPLE_API_GUIDE.md`
        """
        
        await query.edit_message_text(docs_info, parse_mode='Markdown')
    
    async def api_examples_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать примеры использования API"""
        query = update.callback_query
        await query.answer()
        
        examples_info = """
💡 **ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ**

**1. Получить API ключ:**
```bash
curl http://localhost:8001/get-api-key
```

**2. Создать платеж:**
```bash
curl -X POST http://localhost:8001/create-payment \\
     -H "X-API-Key: your_api_key" \\
     -H "Content-Type: application/json" \\
     -d '{"amount": 100.0, "currency": "USDT"}'
```

**3. Проверить статус:**
```bash
curl -H "X-API-Key: your_api_key" \\
     http://localhost:8001/check-payment/payment_id
```

**Python клиент:**
```python
from simple_client import SimplePaymentClient

client = SimplePaymentClient("your_api_key")
result = client.create_payment(100.0, "USDT")
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8001/create-payment', {
    method: 'POST',
    headers: {
        'X-API-Key': 'your_api_key',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({amount: 100.0, currency: 'USDT'})
});
```
        """
        
        await query.edit_message_text(examples_info, parse_mode='Markdown')
    
    async def add_wallet_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки добавления кошелька"""
        query = update.callback_query
        await query.answer()
        
        # Устанавливаем состояние ожидания ввода адреса
        context.user_data['waiting_for_wallet'] = True
        
        wallet_text = """
💳 **Добавление кошелька**

Отправьте адрес вашего Tron кошелька:

⚠️ **Требования:**
• Адрес должен начинаться с 'T'
• Длина адреса: 34 символа
• Только TRC20 совместимые адреса

Пример: `TYourTronWalletAddress1234567890123456789012345`

Отправьте адрес или /cancel для отмены.
        """
        
        await query.edit_message_text(wallet_text, parse_mode='Markdown')
    
    async def check_status_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки проверки статуса"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        user_id = query.from_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        user_wallets = self.db.get_user_wallets(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        wallet_address = active_wallet['wallet_address']
        
        # Получаем ожидающие платежи
        pending_payments = self.db.get_pending_payments(wallet_address)
        
        # Получаем подтвержденные платежи
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount, currency, transaction_hash, confirmed_at
            FROM confirmed_payments 
            WHERE user_id = ?
            ORDER BY confirmed_at DESC
            LIMIT 10
        ''', (user_id,))
        confirmed_payments = cursor.fetchall()
        conn.close()
        
        status_text = f"""
📊 **Статус платежей**

📱 **Активный кошелек:** {active_wallet['wallet_name']}
🏦 **Адрес:** `{wallet_address}`
📊 **Всего кошельков:** {len(user_wallets)}

⏳ **Ожидающие платежи:** {len(pending_payments)}
✅ **Подтвержденные платежи:** {len(confirmed_payments)}
        """
        
        if pending_payments:
            status_text += "\n\n**Ожидающие платежи:**\n"
            for payment in pending_payments[:5]:  # Показываем последние 5
                status_text += f"💰 {payment['amount']} {payment['currency']}\n"
        
        if confirmed_payments:
            status_text += "\n\n**Последние подтвержденные платежи:**\n"
            for payment in confirmed_payments[:5]:  # Показываем последние 5
                status_text += f"💰 {payment[0]} {payment[1]}\n"
                status_text += f"🔗 `{payment[2]}`\n"
                status_text += f"📅 {payment[3]}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить статус", callback_data="check_status")],
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(status_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def check_balance_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки проверки баланса"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        user_id = query.from_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        wallet_address = active_wallet['wallet_address']
        
        try:
            balance = self.tron_tracker.get_usdt_balance(wallet_address)
            balance_text = f"""
💰 **Баланс активного кошелька**

📱 **Название:** {active_wallet['wallet_name']}
🏦 **Адрес:** `{wallet_address}`
💵 **USDT:** {balance:.2f}

*Баланс обновляется в реальном времени*
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить баланс", callback_data="check_balance")],
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(balance_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data="check_balance")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ **Ошибка получения баланса**\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def show_help_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки помощи"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        help_text = """
📚 **СПРАВКА ПО БОТУ**

**Основные функции:**
• 💳 Управление кошельками - добавление и настройка кошельков
• 📊 Статус платежей - просмотр статистики и истории
• 💰 Баланс кошелька - проверка текущего баланса
• 🔑 API интеграция - получение ключа для интеграции

**Как использовать:**
1. Добавьте кошелек через кнопку "Управление кошельками"
2. Активируйте нужный кошелек
3. Получайте уведомления о платежах
4. Используйте API для интеграции в свои проекты

**Безопасность:**
🔒 Приватный режим - доступ только для авторизованных пользователей
✅ Все данные защищены
🛡️ Безопасное хранение кошельков
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔑 Получить API ключ", callback_data="get_api_key")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_wallet_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ввода адреса кошелька"""
        if not await self.check_access(update, context):
            return
        
        # Проверяем, ожидаем ли мы ввод адреса кошелька
        if not context.user_data.get('waiting_for_wallet', False):
            return
        
        user_id = update.effective_user.id
        wallet_address = update.message.text.strip()
        
        # Проверяем команду отмены
        if wallet_address.lower() in ['/cancel', 'отмена', 'cancel']:
            context.user_data['waiting_for_wallet'] = False
            await update.message.reply_text("❌ Добавление кошелька отменено.")
            return
        
        # Валидация адреса
        if not self.tron_tracker.validate_address(wallet_address):
            await update.message.reply_text(
                "❌ **Неверный адрес кошелька!**\n\n"
                "Проверьте:\n"
                "• Адрес начинается с 'T'\n"
                "• Длина адреса: 34 символа\n"
                "• Это Tron адрес\n\n"
                "Попробуйте еще раз или отправьте /cancel для отмены.",
                parse_mode='Markdown'
            )
            return
        
        # Сохраняем адрес в базе данных
        try:
            # Используем новую систему кошельков
            self.db.add_user_wallet(user_id, wallet_address)
            context.user_data['waiting_for_wallet'] = False
            
            success_text = f"""
✅ **Кошелек успешно добавлен!**

🏦 Адрес: `{wallet_address}`

🤖 **Следующие шаги:**
1. Активируйте кошелек в управлении
2. Включите автоматический режим
3. Отправьте USDT на ваш кошелек
            """
            
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            context.user_data['waiting_for_wallet'] = False
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data="add_wallet")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"❌ **Ошибка сохранения кошелька:** {str(e)}\n\n"
                "Попробуйте еще раз или обратитесь к администратору.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def wallet_management_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатия на кошелек или кнопку управления"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        # Если это кнопка "Управление кошельками"
        if query.data == "wallet_management":
            await self.show_wallet_management(update, context)
            return
        
        # Парсим ID кошелька из callback_data
        wallet_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        # Получаем информацию о кошельке
        wallets = self.db.get_user_wallets(user_id)
        wallet = None
        for w in wallets:
            if w['id'] == wallet_id:
                wallet = w
                break
        
        if not wallet:
            await query.edit_message_text("❌ Кошелек не найден")
            return
        
        # Показываем меню действий для кошелька
        wallet_text = f"""
💳 **Управление кошельком**

📱 **Название:** {wallet['wallet_name']}
🏦 **Адрес:** `{wallet['wallet_address']}`
🟢 **Статус:** {'АКТИВНЫЙ' if wallet['is_active'] else 'Неактивный'}
📅 **Добавлен:** {wallet['created_at']}

**Выберите действие:**
        """
        
        keyboard = []
        if not wallet['is_active']:
            keyboard.append([InlineKeyboardButton("🟢 Сделать активным", callback_data=f"wallet_action_activate_{wallet_id}")])
        
        keyboard.append([InlineKeyboardButton("🗑️ Удалить кошелек", callback_data=f"wallet_action_delete_{wallet_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад к списку", callback_data="wallet_back")])
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(wallet_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def wallet_action_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик действий с кошельком"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        try:
            user_id = query.from_user.id
            parts = query.data.split('_')
            if len(parts) < 4:
                logger.error(f"Неверный формат callback_data: {query.data}")
                await query.answer("❌ Ошибка обработки", show_alert=True)
                return
            
            action = parts[2]
            wallet_id = int(parts[3])
        
            if action == "activate":
                # Активируем кошелек
                self.db.set_active_wallet(user_id, wallet_id)
                await query.answer("✅ Кошелек активирован!", show_alert=False)
                # Сразу показываем обновленный список
                await self.show_wallet_management(update, context)
                
            elif action == "delete":
                # Удаляем кошелек
                self.db.delete_user_wallet(user_id, wallet_id)
                await query.answer("🗑️ Кошелек удален!", show_alert=False)
                # Сразу показываем обновленный список
                await self.show_wallet_management(update, context)
            else:
                await query.answer("❌ Неизвестное действие", show_alert=False)
                logger.warning(f"Неизвестное действие: {action} для wallet_id={wallet_id}")
        except Exception as e:
            logger.error(f"Ошибка в wallet_action_callback: {e}, callback_data: {query.data}")
            await query.answer("❌ Ошибка обработки действия", show_alert=True)
    
    async def wallet_back_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Назад к списку'"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        try:
            await self.show_wallet_management(update, context)
        except Exception as e:
            logger.error(f"Ошибка в wallet_back_callback: {e}")
            await query.answer("❌ Ошибка", show_alert=True)
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Главное меню'"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        try:
            # Показываем главное меню через callback
            await self.show_main_menu_callback(update, context)
        except Exception as e:
            logger.error(f"Ошибка в main_menu_callback: {e}")
            await query.answer("❌ Ошибка", show_alert=True)
    
    async def show_main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню через callback"""
        query = update.callback_query
        user = query.from_user
        user_id = user.id
        username = user.username
        
        # Получаем информацию о пользователе из новой системы кошельков
        active_wallet = self.db.get_active_wallet(user_id)
        user_wallets = self.db.get_user_wallets(user_id)
        
        wallet_info = ""
        if active_wallet:
            wallet_info = f"\n💳 **Активный кошелек:** `{active_wallet['wallet_address']}`"
            wallet_info += f"\n📱 **Название:** {active_wallet['wallet_name']}"
            wallet_info += f"\n📊 **Всего кошельков:** {len(user_wallets)}"
        elif user_wallets:
            wallet_info = f"\n💳 **Кошельков:** {len(user_wallets)} (нет активного)"
        else:
            wallet_info = "\n💳 **Кошельки не добавлены** - нажмите кнопку ниже"
        
        welcome_text = f"""
🤖 **ГЛАВНОЕ МЕНЮ**

Привет, {user.first_name}! 

🔒 **Приватный режим активен** - доступ только для авторизованных пользователей.
{wallet_info}

**Выберите действие:**
        """
        
        # Создаем клавиатуру с кнопками для главного меню
        keyboard = []
        
        # Основные кнопки (всегда доступны)
        keyboard.append([InlineKeyboardButton("📊 Статус", callback_data="check_status")])
        keyboard.append([InlineKeyboardButton("💰 Баланс", callback_data="check_balance")])
        keyboard.append([InlineKeyboardButton("🤖 Авто", callback_data="auto_mode")])
        
        # Кнопки управления кошельками
        if user_wallets:
            keyboard.append([InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")])
        else:
            keyboard.append([InlineKeyboardButton("💳 Добавить кошелек", callback_data="add_wallet")])
        
        # Дополнительные кнопки
        keyboard.append([InlineKeyboardButton("🔑 Получить API ключ", callback_data="get_api_key")])
        keyboard.append([InlineKeyboardButton("❓ Помощь", callback_data="show_help")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def auto_mode_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки 'Авто'"""
        query = update.callback_query
        await query.answer()
        
        if not await self.check_access(update, context):
            return
        
        user_id = query.from_user.id
        
        # Получаем активный кошелек
        active_wallet = self.db.get_active_wallet(user_id)
        
        if not active_wallet:
            keyboard = [
                [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
                [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "❌ **У вас нет активного кошелька!**\n\n"
                "Сначала добавьте и активируйте кошелек",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return

        user_data = self.db.get_user(user_id)
        current_auto_mode = user_data.get('auto_mode', False)
        new_auto_mode = not current_auto_mode
        self.db.update_user_auto_mode(user_id, new_auto_mode)

        status = "ВКЛЮЧЕН" if new_auto_mode else "ВЫКЛЮЧЕН"
        status_emoji = "✅" if new_auto_mode else "❌"
        
        auto_text = f"""
🤖 **Автоматический режим {status}!**

📱 **Активный кошелек:** {active_wallet['wallet_name']}
🏦 **Адрес:** `{active_wallet['wallet_address']}`

**Что это означает:**
• {'Любой платеж на ваш кошелек будет автоматически зачислен' if new_auto_mode else 'Платежи не будут зачисляться автоматически'}
• {'Независимо от суммы платежа' if new_auto_mode else 'Требуется ручное подтверждение'}
• {'Вы будете получать уведомления о всех поступлениях' if new_auto_mode else 'Уведомления отключены'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Переключить режим", callback_data="auto_mode")],
            [InlineKeyboardButton("💳 Управление кошельками", callback_data="wallet_management")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(auto_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("wallet", self.wallet_command))
        self.application.add_handler(CommandHandler("auto", self.auto_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("api", self.api_command))
        
        # Административные команды
        self.application.add_handler(CommandHandler("admin_add_user", self.admin_add_user_command))
        self.application.add_handler(CommandHandler("admin_remove_user", self.admin_remove_user_command))
        self.application.add_handler(CommandHandler("admin_list_users", self.admin_list_users_command))
        
        # Обработчики callback кнопок
        from telegram.ext import CallbackQueryHandler
        self.application.add_handler(CallbackQueryHandler(self.get_api_key_callback, pattern="^get_api_key$"))
        self.application.add_handler(CallbackQueryHandler(self.api_docs_callback, pattern="^api_docs$"))
        self.application.add_handler(CallbackQueryHandler(self.api_examples_callback, pattern="^api_examples$"))
        
        # Обработчики кнопок главного меню
        self.application.add_handler(CallbackQueryHandler(self.add_wallet_callback, pattern="^add_wallet$"))
        self.application.add_handler(CallbackQueryHandler(self.check_status_callback, pattern="^check_status$"))
        self.application.add_handler(CallbackQueryHandler(self.check_balance_callback, pattern="^check_balance$"))
        self.application.add_handler(CallbackQueryHandler(self.show_help_callback, pattern="^show_help$"))
        
        # Обработчики управления кошельками (ВАЖНО: порядок! Сначала специфичные, потом общие)
        self.application.add_handler(CallbackQueryHandler(self.wallet_action_callback, pattern="^wallet_action_"))
        self.application.add_handler(CallbackQueryHandler(self.wallet_back_callback, pattern="^wallet_back$"))
        self.application.add_handler(CallbackQueryHandler(self.wallet_management_callback, pattern="^wallet_management$"))
        self.application.add_handler(CallbackQueryHandler(self.wallet_management_callback, pattern="^wallet_"))
        
        # Обработчик главного меню
        self.application.add_handler(CallbackQueryHandler(self.main_menu_callback, pattern="^main_menu$"))
        
        # Обработчик авто режима
        self.application.add_handler(CallbackQueryHandler(self.auto_mode_callback, pattern="^auto_mode$"))
        
        # Обработчик сообщений для ввода адреса кошелька
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_wallet_input))
        
        # Запускаем задачу проверки платежей
        self.application.job_queue.run_repeating(
            self.check_payments_task,
            interval=config.CHECK_INTERVAL,
            first=10
        )
        
        # Запускаем бота
        print("🔒 Запуск приватного Payment Bot...")
        print(f"⏰ Интервал проверки: {config.CHECK_INTERVAL} секунд")
        print("🤖 Режим: Автоматическое зачисление ЛЮБЫХ платежей")
        print(f"👥 Разрешенных пользователей: {len(self.allowed_users)}")
        print("🛡️ Приватный режим: ВКЛЮЧЕН")
        
        self.application.run_polling()

if __name__ == "__main__":
    bot = PrivatePaymentBot()
    bot.run()
