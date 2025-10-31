#!/usr/bin/env python3
"""
Telegram Bot для автоматического зачисления любых платежей
Любой платеж на кошелек пользователя автоматически зачисляется
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import Database
from tron_tracker import TronTracker
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AutoPaymentBot:
    def __init__(self):
        self.db = Database()
        self.tron_tracker = TronTracker()
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Добавляем пользователя в базу
        self.db.add_user(user_id, username, "")
        
        await update.message.reply_text(
            "🎉 Добро пожаловать в Auto Payment Bot!\n\n"
            "🤖 Этот бот автоматически зачисляет ЛЮБЫЕ платежи на ваш кошелек!\n\n"
            "📋 Доступные команды:\n"
            "/wallet - Добавить кошелек для отслеживания\n"
            "/auto - Включить/выключить автоматический режим\n"
            "/status - Статус ваших платежей\n"
            "/balance - Баланс кошелька\n"
            "/help - Справка\n\n"
            "💡 В автоматическом режиме любой платеж на ваш кошелек будет зачислен!"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📋 Справка по командам:\n\n"
            "🔹 /wallet <адрес> - Добавить кошелек для отслеживания\n"
            "   Пример: /wallet TYourAddress123456789\n\n"
            "🔹 /auto - Включить/выключить автоматический режим\n"
            "   В автоматическом режиме любой платеж зачисляется\n\n"
            "🔹 /status - Показать статус ваших платежей\n\n"
            "🔹 /balance - Показать баланс кошелька\n\n"
            "🔹 /help - Показать эту справку\n\n"
            "💡 В автоматическом режиме бот зачисляет ЛЮБЫЕ платежи на ваш кошелек!"
        )
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /wallet - добавить кошелек"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите адрес кошелька!\n\n"
                "Пример: /wallet TYourAddress123456789"
            )
            return
        
        wallet_address = context.args[0]
        
        # Валидация адреса (базовая проверка)
        if not wallet_address.startswith('T') or len(wallet_address) != 34:
            await update.message.reply_text(
                "❌ Неверный формат адреса кошелька!\n\n"
                "Адрес должен начинаться с 'T' и содержать 34 символа.\n"
                "Пример: TYourAddress123456789"
            )
            return
        
        # Обновляем кошелек пользователя
        self.db.update_user_wallet(user_id, wallet_address)
        
        # Добавляем кошелек для отслеживания
        self.db.add_tracked_wallet(wallet_address, user_id)
        
        await update.message.reply_text(
            f"✅ Кошелек добавлен!\n\n"
            f"📱 Адрес: `{wallet_address}`\n"
            f"👤 Пользователь: {update.effective_user.username or 'Unknown'}\n\n"
            f"🤖 Теперь бот будет отслеживать ВСЕ платежи на этот кошелек!\n"
            f"💡 Используйте /auto для включения автоматического режима.",
            parse_mode='Markdown'
        )
    
    async def auto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /auto - включить/выключить автоматический режим"""
        user_id = update.effective_user.id
        
        # Получаем текущий статус пользователя
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ Сначала добавьте кошелек командой /wallet"
            )
            return
        
        # Переключаем режим
        current_mode = user_data.get('auto_mode', False)
        new_mode = not current_mode
        
        # Обновляем режим в базе данных
        self.db.update_user_auto_mode(user_id, new_mode)
        
        if new_mode:
            await update.message.reply_text(
                "✅ Автоматический режим ВКЛЮЧЕН!\n\n"
                "🤖 Теперь бот будет автоматически зачислять ЛЮБЫЕ платежи на ваш кошелек!\n"
                "💰 Неважно какая сумма - все будет зачислено!\n\n"
                "📱 Ваш кошелек: `" + user_data['wallet_address'] + "`\n"
                "🔄 Бот проверяет новые платежи каждые " + str(config.CHECK_INTERVAL) + " секунд",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Автоматический режим ВЫКЛЮЧЕН!\n\n"
                "🤖 Бот больше не будет автоматически зачислять платежи.\n"
                "💡 Используйте /auto снова для включения режима."
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status - статус платежей"""
        user_id = update.effective_user.id
        
        user_data = self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ Сначала добавьте кошелек командой /wallet"
            )
            return
        
        # Получаем статистику платежей
        wallet_address = user_data['wallet_address']
        auto_mode = user_data.get('auto_mode', False)
        
        # Получаем подтвержденные платежи
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), SUM(amount) 
            FROM confirmed_payments 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        total_payments = result[0] or 0
        total_amount = result[1] or 0
        
        await update.message.reply_text(
            f"📊 Статус ваших платежей:\n\n"
            f"👤 Пользователь: {user_data['username']}\n"
            f"📱 Кошелек: `{wallet_address}`\n"
            f"🤖 Автоматический режим: {'✅ ВКЛЮЧЕН' if auto_mode else '❌ ВЫКЛЮЧЕН'}\n\n"
            f"💰 Всего платежей: {total_payments}\n"
            f"💵 Общая сумма: {total_amount:.2f} USDT\n\n"
            f"🔄 Бот проверяет новые платежи каждые {config.CHECK_INTERVAL} секунд",
            parse_mode='Markdown'
        )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /balance - баланс кошелька"""
        user_id = update.effective_user.id
        
        user_data = self.db.get_user(user_id)
        if not user_data or not user_data['wallet_address']:
            await update.message.reply_text(
                "❌ Сначала добавьте кошелек командой /wallet"
            )
            return
        
        wallet_address = user_data['wallet_address']
        
        try:
            # Получаем баланс USDT
            balance = self.tron_tracker.get_usdt_balance(wallet_address)
            
            await update.message.reply_text(
                f"💰 Баланс кошелька:\n\n"
                f"📱 Адрес: `{wallet_address}`\n"
                f"💵 USDT: {balance:.2f}\n\n"
                f"🔄 Обновлено: {self.tron_tracker.get_last_update_time()}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            await update.message.reply_text(
                "❌ Ошибка получения баланса. Попробуйте позже."
            )
    
    async def check_payments_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Задача проверки платежей - автоматическое зачисление"""
        try:
            # Получаем всех пользователей с включенным автоматическим режимом
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, wallet_address 
                FROM users 
                WHERE wallet_address IS NOT NULL AND wallet_address != '' AND auto_mode = 1
            ''')
            users = cursor.fetchall()
            conn.close()
            
            for user_id, wallet_address in users:
                try:
                    # Получаем новые транзакции
                    new_transfers = self.tron_tracker.get_new_transfers(wallet_address)
                    
                    for transfer in new_transfers:
                        # Проверяем, не обработан ли уже этот платеж
                        conn = self.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT COUNT(*) FROM confirmed_payments 
                            WHERE transaction_hash = ?
                        ''', (transfer['tx_hash'],))
                        already_processed = cursor.fetchone()[0] > 0
                        conn.close()
                        
                        if not already_processed:
                            # Автоматически зачисляем платеж
                            self.db.confirm_payment(
                                user_id,
                                transfer['amount'],
                                'USDT',
                                transfer['tx_hash'],
                                wallet_address
                            )
                            
                            # Отправляем уведомление пользователю
                            try:
                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text=f"🎉 Получен автоматический платеж!\n\n"
                                         f"💰 Сумма: {transfer['amount']:.2f} USDT\n"
                                         f"🔗 Транзакция: `{transfer['tx_hash']}`\n"
                                         f"📱 Кошелек: `{wallet_address}`\n\n"
                                         f"✅ Платеж автоматически зачислен!",
                                    parse_mode='Markdown'
                                )
                            except Exception as e:
                                logger.error(f"Ошибка отправки уведомления: {e}")
                
                except Exception as e:
                    logger.error(f"Ошибка обработки платежей для пользователя {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка в задаче проверки платежей: {e}")
    
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
        
        # Запускаем задачу проверки платежей
        self.application.job_queue.run_repeating(
            self.check_payments_task,
            interval=config.CHECK_INTERVAL,
            first=10
        )
        
        # Запускаем бота
        print("🚀 Запуск Auto Payment Bot...")
        print(f"⏰ Интервал проверки: {config.CHECK_INTERVAL} секунд")
        print("🤖 Режим: Автоматическое зачисление ЛЮБЫХ платежей")
        
        self.application.run_polling()

if __name__ == "__main__":
    bot = AutoPaymentBot()
    bot.run()





