#!/usr/bin/env python3
"""
Готовые шаблоны кода для интеграции Payment Bot в основной бот
Копируйте и адаптируйте под вашу систему
"""

import sqlite3
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

# Настройки Payment Bot API
PAYMENT_API_URL = "http://localhost:8001"
PAYMENT_API_KEY = "your_api_key_here"  # Получите через GET /get-api-key

# =============================================================================
# КЛИЕНТ ДЛЯ РАБОТЫ С PAYMENT BOT API
# =============================================================================

class PaymentClient:
    """Клиент для работы с Payment Bot API"""
    
    def __init__(self, api_key: str, base_url: str = PAYMENT_API_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_payment_wallet(self, user_wallet: str) -> dict:
        """Получить активный кошелек для приема платежей"""
        try:
            response = requests.post(
                f"{self.base_url}/get-payment-wallet",
                headers=self.headers,
                json={"user_wallet": user_wallet},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Ошибка получения кошелька: {e}")
            return {"success": False, "error": str(e)}
    
    def check_user_payments(self, user_wallet: str) -> dict:
        """Проверить платежи пользователя"""
        try:
            response = requests.post(
                f"{self.base_url}/check-user-payments",
                headers=self.headers,
                json={"user_wallet": user_wallet},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Ошибка проверки платежей: {e}")
            return {"success": False, "error": str(e)}

# =============================================================================
# РАБОТА С БАЗОЙ ДАННЫХ
# =============================================================================

class DatabaseManager:
    """Менеджер базы данных для основного бота"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                wallet_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица депозитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                currency TEXT DEFAULT 'USDT',
                wallet_address TEXT,
                tx_hash TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица балансов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_balances (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'USDT',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_wallet(self, user_id: int, wallet_address: str):
        """Сохранить кошелек пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, wallet_address)
            VALUES (?, ?)
        ''', (user_id, wallet_address))
        
        conn.commit()
        conn.close()
    
    def get_user_wallet(self, user_id: int) -> str:
        """Получить кошелек пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT wallet_address FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def add_deposit(self, user_id: int, amount: float, wallet_address: str, tx_hash: str):
        """Добавить депозит"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deposits (user_id, amount, currency, wallet_address, tx_hash, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, 'USDT', wallet_address, tx_hash, 'confirmed'))
        
        conn.commit()
        conn.close()
    
    def update_balance(self, user_id: int, amount: float):
        """Обновить баланс пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_balances (user_id, balance, currency)
            VALUES (?, COALESCE((SELECT balance FROM user_balances WHERE user_id = ?), 0) + ?, ?)
        ''', (user_id, user_id, amount, 'USDT'))
        
        conn.commit()
        conn.close()
    
    def get_balance(self, user_id: int) -> float:
        """Получить баланс пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance FROM user_balances WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.0

# =============================================================================
# КОМАНДЫ БОТА
# =============================================================================

# Инициализация
db = DatabaseManager()
payment_client = PaymentClient(PAYMENT_API_KEY, PAYMENT_API_URL)

async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для указания кошелька пользователя"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли кошелек в сообщении
    if len(context.args) < 1:
        await update.message.reply_text(
            "💳 **Укажите ваш кошелек**\n\n"
            "Использование: `/wallet TYourWalletAddress123456789`\n\n"
            "Этот кошелек будет использоваться для проверки ваших платежей."
        )
        return
    
    wallet_address = context.args[0]
    
    # Сохраняем кошелек в базу данных
    db.save_user_wallet(user_id, wallet_address)
    
    await update.message.reply_text(
        f"✅ **Кошелек сохранен!**\n\n"
        f"📱 Ваш кошелек: `{wallet_address}`\n\n"
        f"Теперь вы можете использовать команду `/pay` для пополнения баланса."
    )

async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пополнения баланса"""
    user_id = update.effective_user.id
    
    # Получаем кошелек пользователя
    user_wallet = db.get_user_wallet(user_id)
    
    if not user_wallet:
        await update.message.reply_text(
            "❌ **Сначала укажите ваш кошелек**\n\n"
            "Используйте команду: `/wallet TYourWalletAddress123456789`"
        )
        return
    
    # Получаем активный кошелек для приема платежей
    response = payment_client.get_payment_wallet(user_wallet)
    
    if not response.get('success'):
        await update.message.reply_text(f"❌ Ошибка получения кошелька: {response.get('error')}")
        return
    
    active_wallet = response['wallet_address']
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Проверить платеж", callback_data="check_payment")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_payment")]
    ])
    
    await update.message.reply_text(
        f"💳 **Пополнение баланса**\n\n"
        f"📱 Ваш кошелек: `{user_wallet}`\n"
        f"🏦 Кошелек для оплаты: `{active_wallet}`\n\n"
        f"Переведите средства на указанный кошелек, "
        f"затем нажмите кнопку 'Проверить платеж'",
        reply_markup=keyboard
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки баланса"""
    user_id = update.effective_user.id
    
    balance = db.get_balance(user_id)
    
    await update.message.reply_text(
        f"💰 **Ваш баланс**\n\n"
        f"💵 Баланс: {balance} USDT\n"
        f"📱 ID: {user_id}"
    )

async def check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка платежа пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Получаем кошелек пользователя
    user_wallet = db.get_user_wallet(user_id)
    
    if not user_wallet:
        await query.edit_message_text("❌ Кошелек не найден")
        return
    
    # Проверяем платежи
    response = payment_client.check_user_payments(user_wallet)
    
    if not response.get('success'):
        await query.edit_message_text(f"❌ Ошибка: {response.get('error')}")
        return
    
    payments = response.get('payments', [])
    
    if not payments:
        await query.edit_message_text("⏳ Платеж еще не поступил. Попробуйте позже.")
        return
    
    # Обрабатываем платежи
    total_amount = 0
    for payment in payments:
        if payment['confirmed']:
            total_amount += payment['amount']
            
            # Сохраняем депозит
            db.add_deposit(user_id, payment['amount'], user_wallet, payment['tx_hash'])
            
            # Обновляем баланс
            db.update_balance(user_id, payment['amount'])
    
    if total_amount > 0:
        await query.edit_message_text(
            f"✅ **Платеж подтвержден!**\n\n"
            f"💰 Зачислено: {total_amount} USDT\n"
            f"📱 Ваш кошелек: `{user_wallet}`\n\n"
            f"Используйте команду `/balance` для проверки баланса."
        )
    else:
        await query.edit_message_text("⏳ Платеж еще не поступил. Попробуйте позже.")

async def cancel_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена платежа"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ Платеж отменен")

# =============================================================================
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ
# =============================================================================

def register_handlers(application):
    """Регистрация обработчиков команд"""
    
    # Команды
    application.add_handler(CommandHandler("wallet", wallet_command))
    application.add_handler(CommandHandler("pay", pay_command))
    application.add_handler(CommandHandler("balance", balance_command))
    
    # Callback queries
    application.add_handler(CallbackQueryHandler(check_payment_callback, pattern="^check_payment$"))
    application.add_handler(CallbackQueryHandler(cancel_payment_callback, pattern="^cancel_payment$"))

# =============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# =============================================================================

if __name__ == "__main__":
    # Пример использования в основном боте
    from telegram.ext import Application
    
    # Создаем приложение
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    # Регистрируем обработчики
    register_handlers(application)
    
    # Запускаем бота
    application.run_polling()

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def get_payment_statistics():
    """Получить статистику платежей"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    # Общая сумма депозитов
    cursor.execute('SELECT SUM(amount) FROM deposits WHERE status = "confirmed"')
    total_deposits = cursor.fetchone()[0] or 0
    
    # Количество пользователей
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Количество депозитов
    cursor.execute('SELECT COUNT(*) FROM deposits WHERE status = "confirmed"')
    total_transactions = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_deposits": total_deposits,
        "total_users": total_users,
        "total_transactions": total_transactions
    }

def get_user_deposits(user_id: int):
    """Получить депозиты пользователя"""
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT amount, currency, tx_hash, created_at, status
        FROM deposits 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 10
    ''', (user_id,))
    
    deposits = cursor.fetchall()
    conn.close()
    
    return deposits

def format_wallet_address(address: str) -> str:
    """Форматировать адрес кошелька"""
    if len(address) <= 8:
        return address
    return f"{address[:4]}...{address[-4:]}"

# =============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('payment_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# =============================================================================

"""
Примеры использования:

1. Сохранение кошелька пользователя:
   db.save_user_wallet(12345, "TUserWallet123456789")

2. Получение кошелька пользователя:
   wallet = db.get_user_wallet(12345)

3. Получение активного кошелька для платежа:
   response = payment_client.get_payment_wallet("TUserWallet123456789")
   active_wallet = response['wallet_address']

4. Проверка платежей пользователя:
   response = payment_client.check_user_payments("TUserWallet123456789")
   payments = response['payments']

5. Обновление баланса:
   db.update_balance(12345, 100.0)

6. Получение баланса:
   balance = db.get_balance(12345)

7. Получение статистики:
   stats = get_payment_statistics()
   print(f"Общая сумма депозитов: {stats['total_deposits']} USDT")

8. Получение депозитов пользователя:
   deposits = get_user_deposits(12345)
   for deposit in deposits:
       print(f"Сумма: {deposit[0]}, Хеш: {deposit[2]}")
"""






