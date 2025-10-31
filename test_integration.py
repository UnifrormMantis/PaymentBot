#!/usr/bin/env python3
"""
Тест интеграции платежной системы
Показывает, как использовать модуль интеграции
"""

import asyncio
import logging
from payment_integration import PaymentIntegration

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBot:
    """Тестовый бот для демонстрации интеграции"""
    
    def __init__(self):
        self.payment_system = PaymentIntegration()
        
        # Регистрируем callback для уведомлений
        self.payment_system.register_payment_callback(
            user_id=0,  # Будет заменен на реальный user_id
            callback=self.on_payment_received
        )
    
    async def on_payment_received(self, user_id: int, amount: float, 
                                currency: str, transaction_hash: str, 
                                wallet_address: str):
        """Обработчик получения платежа"""
        print(f"🎉 ПОЛУЧЕН ПЛАТЕЖ!")
        print(f"   👤 Пользователь: {user_id}")
        print(f"   💰 Сумма: {amount} {currency}")
        print(f"   🔗 Транзакция: {transaction_hash}")
        print(f"   📱 Кошелек: {wallet_address}")
        print()
        
        # Здесь можно добавить вашу логику обработки платежа
        await self.process_payment_logic(user_id, amount, currency)
    
    async def process_payment_logic(self, user_id: int, amount: float, currency: str):
        """Логика обработки платежа"""
        print(f"🔄 Обработка платежа для пользователя {user_id}...")
        
        # Пример логики: активация подписки на основе суммы
        if amount >= 100:
            print(f"   ✅ Активирована премиум подписка")
        elif amount >= 50:
            print(f"   ✅ Активирована стандартная подписка")
        else:
            print(f"   ✅ Добавлено {amount} кредитов")
        
        print()
    
    async def test_create_payment(self, user_id: int, amount: float):
        """Тест создания платежа"""
        print(f"🧪 ТЕСТ: Создание платежа")
        print(f"   👤 Пользователь: {user_id}")
        print(f"   💰 Сумма: {amount} USDT")
        print()
        
        result = await self.payment_system.create_payment_request(
            user_id=user_id,
            amount=amount,
            currency="USDT",
            description="Тестовый платеж"
        )
        
        if result['success']:
            print(f"✅ Платеж создан успешно:")
            print(f"   🆔 ID: {result['payment_id']}")
            print(f"   📱 Кошелек: {result['wallet_address']}")
            print(f"   💰 Сумма: {result['amount']} {result['currency']}")
        else:
            print(f"❌ Ошибка создания платежа: {result['error']}")
        
        print()
        return result
    
    async def test_auto_payment(self, user_id: int, wallet_address: str):
        """Тест автоматического платежа"""
        print(f"🧪 ТЕСТ: Настройка автоматического платежа")
        print(f"   👤 Пользователь: {user_id}")
        print(f"   📱 Кошелек: {wallet_address}")
        print()
        
        result = await self.payment_system.create_auto_payment_request(
            user_id=user_id,
            wallet_address=wallet_address,
            description="Автоматический платеж"
        )
        
        if result['success']:
            print(f"✅ Автоматический платеж настроен:")
            print(f"   📱 Кошелек: {result['wallet_address']}")
            print(f"   🤖 Режим: {result['auto_mode']}")
        else:
            print(f"❌ Ошибка настройки: {result['error']}")
        
        print()
        return result
    
    async def test_check_status(self, user_id: int):
        """Тест проверки статуса"""
        print(f"🧪 ТЕСТ: Проверка статуса платежей")
        print(f"   👤 Пользователь: {user_id}")
        print()
        
        result = await self.payment_system.check_payment_status(user_id)
        
        if result['success']:
            print(f"✅ Статус получен:")
            print(f"   📊 Ожидающих платежей: {len(result['pending_payments'])}")
            print(f"   ✅ Подтвержденных платежей: {len(result['confirmed_payments'])}")
        else:
            print(f"❌ Ошибка проверки статуса: {result['error']}")
        
        print()
        return result
    
    async def test_balance(self, user_id: int):
        """Тест проверки баланса"""
        print(f"🧪 ТЕСТ: Проверка баланса")
        print(f"   👤 Пользователь: {user_id}")
        print()
        
        result = await self.payment_system.get_wallet_balance(user_id)
        
        if result['success']:
            print(f"✅ Баланс получен:")
            print(f"   📱 Кошелек: {result['wallet_address']}")
            print(f"   💰 Баланс: {result['balance']} {result['currency']}")
        else:
            print(f"❌ Ошибка получения баланса: {result['error']}")
        
        print()
        return result
    
    async def test_integration_info(self):
        """Тест информации об интеграции"""
        print(f"🧪 ТЕСТ: Информация об интеграции")
        print()
        
        info = self.payment_system.get_integration_info()
        
        print(f"✅ Информация получена:")
        print(f"   📦 Версия: {info['version']}")
        print(f"   🚀 Функции: {', '.join(info['features'])}")
        print(f"   💱 Валюты: {', '.join(info['supported_currencies'])}")
        print(f"   🔌 API: {len(info['api_endpoints'])} методов")
        print()
        
        return info
    
    async def run_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК ТЕСТОВ ИНТЕГРАЦИИ")
        print("=" * 50)
        print()
        
        # Тестовые данные
        test_user_id = 12345
        test_wallet = "TTestWallet1234567890123456789012345"
        test_amount = 100.0
        
        try:
            # Тест 1: Информация об интеграции
            await self.test_integration_info()
            
            # Тест 2: Создание обычного платежа
            await self.test_create_payment(test_user_id, test_amount)
            
            # Тест 3: Настройка автоматического платежа
            await self.test_auto_payment(test_user_id, test_wallet)
            
            # Тест 4: Проверка статуса
            await self.test_check_status(test_user_id)
            
            # Тест 5: Проверка баланса
            await self.test_balance(test_user_id)
            
            print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
            print()
            print("💡 СЛЕДУЮЩИЕ ШАГИ:")
            print("   1. Интегрируйте PaymentIntegration в ваш бот")
            print("   2. Настройте callback для обработки платежей")
            print("   3. Добавьте команды для управления платежами")
            print("   4. Протестируйте с реальными пользователями")
            
        except Exception as e:
            print(f"❌ Ошибка в тестах: {e}")
            logger.error(f"Ошибка в тестах: {e}")

async def main():
    """Главная функция"""
    print("🔧 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ПЛАТЕЖНОЙ СИСТЕМЫ")
    print("=" * 60)
    print()
    
    # Создаем тестовый бот
    test_bot = TestBot()
    
    # Запускаем тесты
    await test_bot.run_tests()

if __name__ == "__main__":
    asyncio.run(main())





