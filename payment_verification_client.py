#!/usr/bin/env python3
"""
Клиент для проверки поступления USDT платежей
Используется в основном боте для проверки платежей от пользователей
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

class PaymentVerificationClient:
    """Клиент для проверки поступления платежей"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8002"):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ для аутентификации
            base_url: Базовый URL API сервера
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнить HTTP запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ошибка запроса: {str(e)}"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Ошибка парсинга JSON: {str(e)}"
            }
    
    def verify_payment(self, user_wallet: str, expected_amount: float, currency: str = "USDT", description: str = "") -> Dict[str, Any]:
        """
        Проверить поступление платежа от пользователя
        
        Args:
            user_wallet: Кошелек пользователя
            expected_amount: Ожидаемая сумма
            currency: Валюта (по умолчанию USDT)
            description: Описание платежа
            
        Returns:
            Словарь с результатом проверки
        """
        data = {
            "user_wallet": user_wallet,
            "expected_amount": expected_amount,
            "currency": currency,
            "description": description
        }
        
        return self._make_request("POST", "/verify-payment", data=data)
    
    def get_wallet_info(self) -> Dict[str, Any]:
        """
        Получить информацию о кошельке для приема платежей
        
        Returns:
            Словарь с информацией о кошельке
        """
        return self._make_request("GET", "/wallet-info")
    
    def wait_for_payment(self, user_wallet: str, expected_amount: float, timeout: int = 300, check_interval: int = 10) -> Dict[str, Any]:
        """
        Ожидать поступления платежа от пользователя
        
        Args:
            user_wallet: Кошелек пользователя
            expected_amount: Ожидаемая сумма
            timeout: Максимальное время ожидания в секундах
            check_interval: Интервал проверки в секундах
            
        Returns:
            Словарь с результатом проверки
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.verify_payment(user_wallet, expected_amount)
            
            if not result.get("success", False):
                return result
            
            if result.get("payment_found", False):
                return result
            
            time.sleep(check_interval)
        
        # Таймаут
        return {
            "success": True,
            "payment_found": False,
            "received_amount": 0.0,
            "currency": "USDT",
            "user_wallet": user_wallet,
            "message": "Превышено время ожидания платежа"
        }


# Пример использования в основном боте
class MainBotPaymentHandler:
    """Обработчик платежей для основного бота"""
    
    def __init__(self, api_key: str):
        self.payment_client = PaymentVerificationClient(api_key)
    
    def handle_user_payment(self, user_id: int, user_wallet: str, amount: float, product_name: str = ""):
        """
        Обработать платеж от пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            user_wallet: Кошелек пользователя
            amount: Сумма платежа
            product_name: Название товара/услуги
            
        Returns:
            Результат обработки платежа
        """
        print(f"🔍 Проверка платежа от пользователя {user_id}")
        print(f"   Кошелек: {user_wallet}")
        print(f"   Сумма: {amount} USDT")
        print(f"   Товар: {product_name}")
        
        # Проверяем поступление платежа
        result = self.payment_client.verify_payment(
            user_wallet=user_wallet,
            expected_amount=amount,
            currency="USDT",
            description=f"Покупка {product_name} пользователем {user_id}"
        )
        
        if result.get("success") and result.get("payment_found"):
            print(f"✅ Платеж подтвержден!")
            print(f"   Получено: {result['received_amount']} USDT")
            print(f"   Транзакция: {result.get('transaction_hash', 'N/A')}")
            
            # Здесь можно добавить логику для вашего основного бота:
            # - Зачислить товар/услугу пользователю
            # - Обновить баланс
            # - Отправить уведомление
            # - Записать в базу данных
            
            return {
                "success": True,
                "payment_confirmed": True,
                "amount_received": result['received_amount'],
                "transaction_hash": result.get('transaction_hash'),
                "message": "Платеж успешно подтвержден"
            }
        else:
            print(f"❌ Платеж не найден")
            print(f"   Причина: {result.get('message', 'Неизвестная ошибка')}")
            
            return {
                "success": False,
                "payment_confirmed": False,
                "amount_received": 0.0,
                "message": result.get('message', 'Платеж не найден')
            }


# Пример использования
if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ ПЛАТЕЖНОГО API")
    print("=" * 40)
    
    # Получаем API ключ
    try:
        response = requests.get("http://localhost:8002/get-api-key")
        if response.status_code == 200:
            api_data = response.json()
            api_key = api_data['api_key']
            print(f"✅ API ключ получен: {api_key}")
        else:
            print("❌ Ошибка получения API ключа")
            exit(1)
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        exit(1)
    
    # Инициализация клиента
    client = PaymentVerificationClient(api_key)
    
    # Тест 1: Получение информации о кошельке
    print("\n1. Получение информации о кошельке...")
    wallet_info = client.get_wallet_info()
    if wallet_info.get("success"):
        print(f"✅ Кошелек: {wallet_info['wallet_address']}")
        print(f"   Баланс: {wallet_info['balance']} {wallet_info['currency']}")
    else:
        print(f"❌ Ошибка: {wallet_info.get('error', 'Неизвестная ошибка')}")
    
    # Тест 2: Проверка платежа (тестовый)
    print("\n2. Проверка тестового платежа...")
    test_result = client.verify_payment(
        user_wallet="TTestWallet1234567890123456789012345",
        expected_amount=1.00,
        currency="USDT",
        description="Тестовый платеж"
    )
    
    if test_result.get("success"):
        if test_result.get("payment_found"):
            print(f"✅ Платеж найден: {test_result['received_amount']} USDT")
        else:
            print(f"ℹ️  Платеж не найден (это нормально для тестового кошелька)")
    else:
        print(f"❌ Ошибка: {test_result.get('error', 'Неизвестная ошибка')}")
    
    # Тест 3: Пример использования в основном боте
    print("\n3. Пример использования в основном боте...")
    main_bot = MainBotPaymentHandler(api_key)
    
    # Симулируем обработку платежа
    result = main_bot.handle_user_payment(
        user_id=123456789,
        user_wallet="TTestWallet1234567890123456789012345",
        amount=5.00,
        product_name="Премиум подписка"
    )
    
    if result["success"] and result["payment_confirmed"]:
        print(f"✅ Платеж обработан успешно!")
        print(f"   Получено: {result['amount_received']} USDT")
    else:
        print(f"ℹ️  Платеж не подтвержден: {result['message']}")
    
    print("\n" + "=" * 40)
    print("✅ Тестирование завершено!")
    print("\n💡 Для использования в вашем боте:")
    print("   1. Получите API ключ: GET /get-api-key")
    print("   2. Используйте PaymentVerificationClient")
    print("   3. Вызывайте verify_payment() для проверки")
