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

class PaymentBot:
    def __init__(self):
        self.db = Database()
        self.tron_tracker = TronTracker()
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        username = user.username
        
        # Добавляем пользователя в базу данных
        self.db.add_user(user_id, username)
        
        welcome_text = f"""
🤖 Добро пожаловать в бот для отслеживания TRC20 платежей!

Привет, {user.first_name}! 

Этот бот поможет вам:
• Отслеживать поступления USDT на ваш кошелек
• Автоматически подтверждать платежи
• Получать уведомления о новых транзакциях

Для начала работы используйте команды:
/wallet - добавить кошелек для отслеживания
/payment - создать ожидающий платеж
/status - проверить статус платежей
/help - помощь

Нажмите /wallet чтобы добавить ваш Tron кошелек.
        """
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 Справка по командам:

/wallet - Добавить или изменить кошелек для отслеживания
/payment - Создать ожидающий платеж
/status - Проверить статус ваших платежей
/history - История подтвержденных платежей
/balance - Проверить баланс кошелька
/help - Показать эту справку

🔧 Как это работает:
1. Добавьте ваш Tron кошелек командой /wallet
2. Создайте ожидающий платеж командой /payment
3. Бот будет отслеживать поступления на ваш кошелек
4. При поступлении нужной суммы платеж автоматически подтвердится

⚠️ Важно:
- Используйте только TRC20 USDT
- Адрес кошелька должен начинаться с 'T'
- Минимальная сумма для отслеживания: 1 USDT
        """
        
        await update.message.reply_text(help_text)
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /wallet"""
        user_id = update.effective_user.id
        
        if context.args:
            wallet_address = context.args[0]
            
            # Валидация адреса
            if not self.tron_tracker.validate_address(wallet_address):
                await update.message.reply_text(
                    "❌ Неверный формат адреса Tron кошелька!\n\n"
                    "Адрес должен:\n"
                    "• Начинаться с 'T'\n"
                    "• Содержать 34 символа\n"
                    "• Быть валидным Tron адресом\n\n"
                    "Попробуйте еще раз: /wallet <ваш_адрес>"
                )
                return
            
            # Обновляем адрес в базе данных
            self.db.add_user(user_id, update.effective_user.username, wallet_address)
            self.db.add_tracked_wallet(wallet_address, user_id)
            
            await update.message.reply_text(
                f"✅ Кошелек успешно добавлен!\n\n"
                f"Адрес: `{wallet_address}`\n"
                f"Теперь бот будет отслеживать поступления на этот кошелек.",
                parse_mode='Markdown'
            )
        else:
            # Показываем текущий кошелек
            user_data = self.db.get_user(user_id)
            if user_data and user_data.get('wallet_address'):
                await update.message.reply_text(
                    f"📱 Ваш текущий кошелек:\n\n"
                    f"`{user_data['wallet_address']}`\n\n"
                    f"Чтобы изменить кошелек, используйте:\n"
                    f"/wallet <новый_адрес>",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "📱 Кошелек не добавлен.\n\n"
                    "Чтобы добавить кошелек для отслеживания, используйте:\n"
                    "/wallet <ваш_tron_адрес>\n\n"
                    "Пример: /wallet TYourTronAddressHere123456789"
                )
    
    async def payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /payment"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли у пользователя кошелек
        user_data = self.db.get_user(user_id)
        if not user_data or not user_data.get('wallet_address'):
            await update.message.reply_text(
                "❌ Сначала добавьте кошелек командой /wallet"
            )
            return
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "💳 Создание ожидающего платежа\n\n"
                "Использование: /payment <сумма> <валюта>\n\n"
                "Примеры:\n"
                "/payment 100 USDT\n"
                "/payment 50.5 USDT\n\n"
                "Минимальная сумма: 1 USDT"
            )
            return
        
        try:
            amount = float(context.args[0])
            currency = context.args[1].upper()
            
            if amount < 1:
                await update.message.reply_text("❌ Минимальная сумма: 1 USDT")
                return
            
            if currency != 'USDT':
                await update.message.reply_text("❌ Поддерживается только USDT")
                return
            
            # Добавляем ожидающий платеж
            payment_id = self.db.add_pending_payment(
                user_id, amount, currency, user_data['wallet_address']
            )
            
            await update.message.reply_text(
                f"✅ Ожидающий платеж создан!\n\n"
                f"ID: {payment_id}\n"
                f"Сумма: {amount} {currency}\n"
                f"Кошелек: `{user_data['wallet_address']}`\n\n"
                f"Бот будет отслеживать поступления на ваш кошелек.\n"
                f"При поступлении {amount} {currency} платеж автоматически подтвердится.",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text("❌ Неверный формат суммы. Используйте числа.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        user_id = update.effective_user.id
        
        # Получаем ожидающие платежи
        user_data = self.db.get_user(user_id)
        if not user_data or not user_data.get('wallet_address'):
            await update.message.reply_text("❌ Сначала добавьте кошелек командой /wallet")
            return
        
        pending_payments = self.db.get_pending_payments(user_data['wallet_address'])
        
        if not pending_payments:
            await update.message.reply_text(
                "📊 Нет ожидающих платежей.\n\n"
                "Создайте ожидающий платеж командой /payment"
            )
            return
        
        status_text = "📊 Статус ваших платежей:\n\n"
        
        for payment in pending_payments:
            status_text += f"🔄 ID: {payment['id']}\n"
            status_text += f"💰 Сумма: {payment['amount']} {payment['currency']}\n"
            status_text += f"📅 Создан: {payment['created_at']}\n"
            status_text += f"📱 Кошелек: `{payment['wallet_address']}`\n\n"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /balance"""
        user_id = update.effective_user.id
        
        user_data = self.db.get_user(user_id)
        if not user_data or not user_data.get('wallet_address'):
            await update.message.reply_text("❌ Сначала добавьте кошелек командой /wallet")
            return
        
        wallet_address = user_data['wallet_address']
        
        # Получаем информацию об аккаунте
        account_info = self.tron_tracker.get_account_info(wallet_address)
        
        if account_info:
            balance = self.tron_tracker.get_balance(wallet_address)
            
            await update.message.reply_text(
                f"💰 Баланс кошелька:\n\n"
                f"Адрес: `{wallet_address}`\n"
                f"USDT: {balance:.6f}\n\n"
                f"*Баланс может обновляться с задержкой",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Не удалось получить информацию о кошельке")
    
    async def check_payments_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Задача для проверки новых платежей"""
        try:
            tracked_wallets = self.db.get_tracked_wallets()
            
            for wallet in tracked_wallets:
                wallet_address = wallet['wallet_address']
                user_id = wallet['user_id']
                
                # Получаем новые транзакции
                new_transfers = self.tron_tracker.check_new_transactions(wallet_address)
                
                for transfer in new_transfers:
                    # Проверяем, есть ли ожидающие платежи на эту сумму
                    pending_payments = self.db.get_pending_payments(wallet_address)
                    
                    for payment in pending_payments:
                        if (abs(transfer['amount'] - payment['amount']) < 0.01 and 
                            payment['status'] == 'pending'):
                            
                            # Подтверждаем платеж
                            self.db.confirm_payment(
                                user_id, 
                                payment['amount'], 
                                payment['currency'],
                                transfer['tx_hash'],
                                wallet_address
                            )
                            
                            # Отправляем уведомление пользователю
                            try:
                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text=f"🎉 Платеж подтвержден!\n\n"
                                         f"💰 Сумма: {payment['amount']} {payment['currency']}\n"
                                         f"🔗 Транзакция: `{transfer['tx_hash']}`\n"
                                         f"📱 Кошелек: `{wallet_address}`\n\n"
                                         f"Платеж ID: {payment['id']}",
                                    parse_mode='Markdown'
                                )
                            except Exception as e:
                                logger.error(f"Ошибка отправки уведомления: {e}")
                            
                            break
                            
        except Exception as e:
            logger.error(f"Ошибка в задаче проверки платежей: {e}")
    
    def run(self):
        """Запуск бота"""
        if not config.TELEGRAM_BOT_TOKEN:
            print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен!")
            return
        
        # Создаем приложение
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("wallet", self.wallet_command))
        self.application.add_handler(CommandHandler("payment", self.payment_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        
        # Добавляем задачу проверки платежей
        job_queue = self.application.job_queue
        job_queue.run_repeating(
            self.check_payments_task, 
            interval=config.CHECK_INTERVAL,
            first=10
        )
        
        print("🤖 Бот запущен!")
        print(f"⏰ Интервал проверки: {config.CHECK_INTERVAL} секунд")
        
        # Запускаем бота
        self.application.run_polling()

if __name__ == "__main__":
    bot = PaymentBot()
    bot.run()
