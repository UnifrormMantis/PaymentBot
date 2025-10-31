#!/usr/bin/env python3
"""
Клиент для интеграции с Payment Bot API
Позволяет легко интегрировать платежи в любой бот
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class PaymentClient:
    """
    Клиент для работы с Payment Bot API
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Инициализация клиента
        
        Args:
            api_url: URL API сервера
        """
        self.api_url = api_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса
        
        Args:
            method: HTTP метод
            endpoint: Endpoint API
            data: Данные для отправки
            
        Returns:
            Ответ от API
        """
        if not self.session:
            raise RuntimeError("Клиент не инициализирован. Используйте async with")
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    result = await response.json()
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            if response.status >= 400:
                raise Exception(f"HTTP {response.status}: {result.get('detail', 'Unknown error')}")
            
            return result
            
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка HTTP запроса: {e}")
            raise Exception(f"Ошибка соединения с API: {e}")
        except Exception as e:
            logger.error(f"Ошибка запроса к API: {e}")
            raise
    
    async def create_payment(self, user_id: int, amount: float, 
                           currency: str = "USDT", description: Optional[str] = None) -> Dict[str, Any]:
        """
        Создание платежа
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            currency: Валюта
            description: Описание платежа
            
        Returns:
            Результат создания платежа
        """
        data = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "description": description
        }
        
        return await self._make_request("POST", "/payment/create", data)
    
    async def setup_auto_payment(self, user_id: int, wallet_address: str, 
                               description: Optional[str] = None) -> Dict[str, Any]:
        """
        Настройка автоматического платежа
        
        Args:
            user_id: ID пользователя
            wallet_address: Адрес кошелька
            description: Описание платежа
            
        Returns:
            Результат настройки автоматического платежа
        """
        data = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "description": description
        }
        
        return await self._make_request("POST", "/payment/auto", data)
    
    async def get_payment_status(self, user_id: int, payment_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Получение статуса платежей
        
        Args:
            user_id: ID пользователя
            payment_id: ID конкретного платежа (опционально)
            
        Returns:
            Статус платежей
        """
        endpoint = f"/payment/status/{user_id}"
        if payment_id:
            endpoint += f"?payment_id={payment_id}"
        
        return await self._make_request("GET", endpoint)
    
    async def get_wallet_balance(self, user_id: int) -> Dict[str, Any]:
        """
        Получение баланса кошелька
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Баланс кошелька
        """
        return await self._make_request("GET", f"/payment/balance/{user_id}")
    
    async def register_callback(self, user_id: int, callback_url: str) -> Dict[str, Any]:
        """
        Регистрация callback URL для уведомлений
        
        Args:
            user_id: ID пользователя
            callback_url: URL для callback уведомлений
            
        Returns:
            Результат регистрации callback
        """
        data = {"callback_url": callback_url}
        return await self._make_request("POST", f"/payment/callback/{user_id}", data)
    
    async def unregister_callback(self, user_id: int) -> Dict[str, Any]:
        """
        Отмена регистрации callback
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Результат отмены регистрации callback
        """
        return await self._make_request("DELETE", f"/payment/callback/{user_id}")
    
    async def get_callbacks(self) -> Dict[str, Any]:
        """
        Получение списка зарегистрированных callback'ов
        
        Returns:
            Список callback'ов
        """
        return await self._make_request("GET", "/payment/callbacks")
    
    async def get_payment_info(self) -> Dict[str, Any]:
        """
        Получение информации о платежной системе
        
        Returns:
            Информация о платежной системе
        """
        return await self._make_request("GET", "/payment/info")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья API
        
        Returns:
            Статус API
        """
        return await self._make_request("GET", "/health")

# Пример использования
class YourBotWithPaymentAPI:
    """
    Пример бота с интеграцией через API
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.payment_client = None
    
    async def start(self):
        """Запуск бота"""
        self.payment_client = PaymentClient(self.api_url)
        print("🤖 Бот с платежной системой запущен!")
    
    async def stop(self):
        """Остановка бота"""
        if self.payment_client:
            await self.payment_client.__aexit__(None, None, None)
        print("🛑 Бот остановлен!")
    
    async def create_payment_for_user(self, user_id: int, amount: float, description: str = None):
        """Создание платежа для пользователя"""
        async with PaymentClient(self.api_url) as client:
            try:
                result = await client.create_payment(
                    user_id=user_id,
                    amount=amount,
                    currency="USDT",
                    description=description
                )
                
                if result['success']:
                    print(f"✅ Платеж создан для пользователя {user_id}: {amount} USDT")
                    return result['data']
                else:
                    print(f"❌ Ошибка создания платежа: {result['error']}")
                    return None
                    
            except Exception as e:
                print(f"❌ Ошибка API: {e}")
                return None
    
    async def setup_auto_payment_for_user(self, user_id: int, wallet_address: str):
        """Настройка автоматического платежа для пользователя"""
        async with PaymentClient(self.api_url) as client:
            try:
                result = await client.setup_auto_payment(
                    user_id=user_id,
                    wallet_address=wallet_address,
                    description="Автоматический платеж"
                )
                
                if result['success']:
                    print(f"✅ Автоматический платеж настроен для пользователя {user_id}")
                    return result['data']
                else:
                    print(f"❌ Ошибка настройки: {result['error']}")
                    return None
                    
            except Exception as e:
                print(f"❌ Ошибка API: {e}")
                return None
    
    async def check_user_balance(self, user_id: int):
        """Проверка баланса пользователя"""
        async with PaymentClient(self.api_url) as client:
            try:
                result = await client.get_wallet_balance(user_id)
                
                if result['success']:
                    print(f"💰 Баланс пользователя {user_id}: {result['balance']} {result['currency']}")
                    return result
                else:
                    print(f"❌ Ошибка получения баланса: {result['error']}")
                    return None
                    
            except Exception as e:
                print(f"❌ Ошибка API: {e}")
                return None
    
    async def get_user_payments(self, user_id: int):
        """Получение истории платежей пользователя"""
        async with PaymentClient(self.api_url) as client:
            try:
                result = await client.get_payment_status(user_id)
                
                if result['success']:
                    data = result['data']
                    print(f"📊 Платежи пользователя {user_id}:")
                    print(f"   Ожидающих: {len(data['pending_payments'])}")
                    print(f"   Подтвержденных: {len(data['confirmed_payments'])}")
                    return data
                else:
                    print(f"❌ Ошибка получения платежей: {result['error']}")
                    return None
                    
            except Exception as e:
                print(f"❌ Ошибка API: {e}")
                return None

# Пример использования
async def main():
    """Пример использования клиента"""
    print("🧪 ТЕСТИРОВАНИЕ PAYMENT CLIENT")
    print("=" * 40)
    
    # Создаем бота
    bot = YourBotWithPaymentAPI("http://localhost:8000")
    
    try:
        # Запускаем бота
        await bot.start()
        
        # Тестовые данные
        test_user_id = 12345
        test_wallet = "TTestWallet1234567890123456789012345"
        test_amount = 100.0
        
        print("\n🧪 ТЕСТ 1: Создание платежа")
        await bot.create_payment_for_user(test_user_id, test_amount, "Тестовый платеж")
        
        print("\n🧪 ТЕСТ 2: Настройка автоматического платежа")
        await bot.setup_auto_payment_for_user(test_user_id, test_wallet)
        
        print("\n🧪 ТЕСТ 3: Проверка баланса")
        await bot.check_user_balance(test_user_id)
        
        print("\n🧪 ТЕСТ 4: История платежей")
        await bot.get_user_payments(test_user_id)
        
        print("\n✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
    
    finally:
        # Останавливаем бота
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())





