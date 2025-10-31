#!/usr/bin/env python3
"""
Модуль интеграции платежной системы для Telegram ботов
Позволяет интегрировать TRC20 платежи в любой бот
"""

import asyncio
import logging
from typing import Optional, Dict, List, Callable
from database import Database
from tron_tracker import TronTracker
import config

logger = logging.getLogger(__name__)

class PaymentIntegration:
    """
    Класс для интеграции платежной системы в другие боты
    """
    
    def __init__(self, bot_token: str = None):
        """
        Инициализация платежной системы
        
        Args:
            bot_token: Токен бота для отправки уведомлений (опционально)
        """
        self.db = Database()
        self.tron_tracker = TronTracker()
        self.bot_token = bot_token
        self.payment_callbacks = {}  # Словарь для хранения callback функций
        
    def register_payment_callback(self, user_id: int, callback: Callable):
        """
        Регистрация callback функции для уведомления о платежах
        
        Args:
            user_id: ID пользователя
            callback: Функция для вызова при получении платежа
        """
        self.payment_callbacks[user_id] = callback
        logger.info(f"Зарегистрирован callback для пользователя {user_id}")
    
    def unregister_payment_callback(self, user_id: int):
        """
        Отмена регистрации callback функции
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self.payment_callbacks:
            del self.payment_callbacks[user_id]
            logger.info(f"Отменена регистрация callback для пользователя {user_id}")
    
    async def create_payment_request(self, user_id: int, amount: float, 
                                   currency: str = "USDT", 
                                   description: str = None) -> Dict:
        """
        Создание запроса на платеж
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            currency: Валюта (по умолчанию USDT)
            description: Описание платежа
            
        Returns:
            Словарь с информацией о платеже
        """
        try:
            # Получаем данные пользователя
            user_data = self.db.get_user(user_id)
            if not user_data or not user_data.get('wallet_address'):
                return {
                    'success': False,
                    'error': 'Пользователь не зарегистрирован или не указан кошелек'
                }
            
            wallet_address = user_data['wallet_address']
            
            # Создаем ожидающий платеж
            payment_id = self.db.add_pending_payment(
                user_id, amount, currency, wallet_address
            )
            
            # Регистрируем callback для уведомлений
            if user_id not in self.payment_callbacks:
                self.payment_callbacks[user_id] = None
            
            return {
                'success': True,
                'payment_id': payment_id,
                'wallet_address': wallet_address,
                'amount': amount,
                'currency': currency,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_auto_payment_request(self, user_id: int, 
                                        wallet_address: str,
                                        description: str = None) -> Dict:
        """
        Создание запроса на автоматический платеж (любая сумма)
        
        Args:
            user_id: ID пользователя
            wallet_address: Адрес кошелька
            description: Описание платежа
            
        Returns:
            Словарь с информацией о платеже
        """
        try:
            # Обновляем кошелек пользователя
            self.db.update_user_wallet(user_id, wallet_address)
            
            # Включаем автоматический режим
            self.db.update_user_auto_mode(user_id, True)
            
            # Добавляем кошелек для отслеживания
            self.db.add_tracked_wallet(wallet_address, user_id)
            
            # Регистрируем callback для уведомлений
            if user_id not in self.payment_callbacks:
                self.payment_callbacks[user_id] = None
            
            return {
                'success': True,
                'wallet_address': wallet_address,
                'auto_mode': True,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания автоматического платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_payment_status(self, user_id: int, payment_id: int = None) -> Dict:
        """
        Проверка статуса платежа
        
        Args:
            user_id: ID пользователя
            payment_id: ID платежа (опционально)
            
        Returns:
            Словарь со статусом платежа
        """
        try:
            user_data = self.db.get_user(user_id)
            if not user_data or not user_data.get('wallet_address'):
                return {
                    'success': False,
                    'error': 'Пользователь не зарегистрирован'
                }
            
            wallet_address = user_data['wallet_address']
            
            if payment_id:
                # Проверяем конкретный платеж
                pending_payments = self.db.get_pending_payments(wallet_address)
                payment = next((p for p in pending_payments if p['id'] == payment_id), None)
                
                if payment:
                    return {
                        'success': True,
                        'payment_id': payment_id,
                        'status': payment['status'],
                        'amount': payment['amount'],
                        'currency': payment['currency']
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Платеж не найден'
                    }
            else:
                # Возвращаем все платежи пользователя
                pending_payments = self.db.get_pending_payments(wallet_address)
                
                # Получаем подтвержденные платежи
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, amount, currency, transaction_hash, confirmed_at
                    FROM confirmed_payments 
                    WHERE user_id = ?
                    ORDER BY confirmed_at DESC
                ''', (user_id,))
                confirmed_payments = cursor.fetchall()
                conn.close()
                
                return {
                    'success': True,
                    'pending_payments': pending_payments,
                    'confirmed_payments': [
                        {
                            'id': p[0],
                            'amount': p[1],
                            'currency': p[2],
                            'transaction_hash': p[3],
                            'confirmed_at': p[4]
                        } for p in confirmed_payments
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка проверки статуса платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_wallet_balance(self, user_id: int) -> Dict:
        """
        Получение баланса кошелька пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с балансом кошелька
        """
        try:
            user_data = self.db.get_user(user_id)
            if not user_data or not user_data.get('wallet_address'):
                return {
                    'success': False,
                    'error': 'Пользователь не зарегистрирован или не указан кошелек'
                }
            
            wallet_address = user_data['wallet_address']
            balance = self.tron_tracker.get_usdt_balance(wallet_address)
            
            return {
                'success': True,
                'wallet_address': wallet_address,
                'balance': balance,
                'currency': 'USDT'
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_payments(self):
        """
        Обработка платежей (вызывается периодически)
        """
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
                            
                            # Вызываем callback если зарегистрирован
                            if user_id in self.payment_callbacks and self.payment_callbacks[user_id]:
                                try:
                                    await self.payment_callbacks[user_id](
                                        user_id=user_id,
                                        amount=transfer['amount'],
                                        currency='USDT',
                                        transaction_hash=transfer['tx_hash'],
                                        wallet_address=wallet_address
                                    )
                                except Exception as e:
                                    logger.error(f"Ошибка вызова callback для пользователя {user_id}: {e}")
                
                except Exception as e:
                    logger.error(f"Ошибка обработки платежей для пользователя {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка в задаче обработки платежей: {e}")
    
    def get_integration_info(self) -> Dict:
        """
        Получение информации об интеграции
        
        Returns:
            Словарь с информацией об интеграции
        """
        return {
            'version': '1.1.0',
            'features': [
                'TRC20 платежи',
                'Автоматическое зачисление',
                'Webhook уведомления',
                'Баланс кошелька',
                'История платежей'
            ],
            'supported_currencies': ['USDT'],
            'api_endpoints': [
                'create_payment_request',
                'create_auto_payment_request',
                'check_payment_status',
                'get_wallet_balance',
                'process_payments'
            ]
        }

# Пример использования
class ExampleBot:
    """
    Пример бота с интегрированной платежной системой
    """
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.payment_system = PaymentIntegration(bot_token)
        
        # Регистрируем callback для уведомлений
        self.payment_system.register_payment_callback(
            user_id=0,  # Будет заменен на реальный user_id
            callback=self.on_payment_received
        )
    
    async def on_payment_received(self, user_id: int, amount: float, 
                                currency: str, transaction_hash: str, 
                                wallet_address: str):
        """
        Обработчик получения платежа
        """
        print(f"💰 Получен платеж от пользователя {user_id}:")
        print(f"   Сумма: {amount} {currency}")
        print(f"   Транзакция: {transaction_hash}")
        print(f"   Кошелек: {wallet_address}")
        
        # Здесь можно добавить логику обработки платежа
        # Например, активация подписки, пополнение баланса и т.д.
    
    async def create_payment(self, user_id: int, amount: float):
        """
        Создание платежа
        """
        result = await self.payment_system.create_payment_request(
            user_id=user_id,
            amount=amount,
            currency="USDT",
            description="Платеж за услуги"
        )
        
        if result['success']:
            print(f"✅ Платеж создан: {result}")
            return result
        else:
            print(f"❌ Ошибка создания платежа: {result['error']}")
            return None
    
    async def setup_auto_payment(self, user_id: int, wallet_address: str):
        """
        Настройка автоматического платежа
        """
        result = await self.payment_system.create_auto_payment_request(
            user_id=user_id,
            wallet_address=wallet_address,
            description="Автоматический платеж"
        )
        
        if result['success']:
            print(f"✅ Автоматический платеж настроен: {result}")
            return result
        else:
            print(f"❌ Ошибка настройки автоматического платежа: {result['error']}")
            return None

if __name__ == "__main__":
    # Пример использования
    bot = ExampleBot("YOUR_BOT_TOKEN")
    
    # Создание платежа
    # asyncio.run(bot.create_payment(user_id=12345, amount=100.0))
    
    # Настройка автоматического платежа
    # asyncio.run(bot.setup_auto_payment(user_id=12345, wallet_address="TYourAddress..."))





