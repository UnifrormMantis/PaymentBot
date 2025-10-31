#!/usr/bin/env python3
"""
Готовый клиент для интеграции платежного бота
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from tron_tracker import TronTracker

class PaymentBotClient:
    """Клиент для работы с API платежного бота"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8001"):
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
        self.tron_tracker = TronTracker()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнить HTTP запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
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
    
    def create_payment(self, user_id: int, amount: float, currency: str = "USDT", description: str = "") -> Dict[str, Any]:
        """
        Создать новый платеж
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            currency: Валюта (по умолчанию USDT)
            description: Описание платежа
            
        Returns:
            Словарь с результатом создания платежа
        """
        data = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "description": description
        }
        
        return self._make_request("POST", "/create-payment", data=data)
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Получить статус платежа
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Словарь со статусом платежа
        """
        return self._make_request("GET", f"/check-payment/{payment_id}")
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """
        Получить баланс кошелька
        
        Returns:
            Словарь с балансом кошелька
        """
        # Получаем баланс через TronTracker напрямую
        try:
            balance = self.tron_tracker.get_balance("TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx")
            return {
                "success": True,
                "balance": balance,
                "currency": "USDT",
                "wallet_address": "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка получения баланса: {str(e)}"
            }
    
    def get_payment_history(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        Получить историю платежей пользователя
        
        Args:
            user_id: ID пользователя
            limit: Количество записей (по умолчанию 10)
            
        Returns:
            Словарь с историей платежей
        """
        # Пока что возвращаем заглушку, так как endpoint не реализован
        return {
            "success": True,
            "payments": [],
            "total": 0,
            "message": "История платежей пока не реализована"
        }
    
    def wait_for_payment_confirmation(self, payment_id: str, timeout: int = 300, check_interval: int = 10) -> Dict[str, Any]:
        """
        Ожидать подтверждения платежа
        
        Args:
            payment_id: ID платежа
            timeout: Максимальное время ожидания в секундах
            check_interval: Интервал проверки в секундах
            
        Returns:
            Словарь со статусом платежа
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_payment_status(payment_id)
            
            if not status.get("success", False):
                return status
            
            if status.get("status") == "confirmed":
                return status
            
            time.sleep(check_interval)
        
        # Таймаут
        return {
            "success": False,
            "error": "Превышено время ожидания подтверждения платежа",
            "payment_id": payment_id,
            "status": "timeout"
        }
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Получить информацию об API
        
        Returns:
            Словарь с информацией об API
        """
        return self._make_request("GET", "/get-api-key")


# Пример использования
if __name__ == "__main__":
    # Инициализация клиента
    client = PaymentBotClient("7QrV9SXDydqnE_vCraPYonhW-MZy1NAFQ8Wp3_fJSGY")
    
    print("🧪 ТЕСТИРОВАНИЕ ПЛАТЕЖНОГО API")
    print("=" * 40)
    
    # Тест 1: Получение информации об API
    print("\n1. Получение информации об API...")
    api_info = client.get_api_info()
    if api_info.get("success"):
        print(f"✅ API доступен")
        print(f"   Ключ: {api_info.get('api_key', 'N/A')}")
    else:
        print(f"❌ Ошибка: {api_info.get('error', 'Неизвестная ошибка')}")
    
    # Тест 2: Получение баланса
    print("\n2. Получение баланса кошелька...")
    balance = client.get_wallet_balance()
    if balance.get("success"):
        print(f"✅ Баланс: {balance.get('balance', 0)} {balance.get('currency', 'USDT')}")
        print(f"   Кошелек: {balance.get('wallet_address', 'N/A')}")
    else:
        print(f"❌ Ошибка: {balance.get('error', 'Неизвестная ошибка')}")
    
    # Тест 3: Создание тестового платежа
    print("\n3. Создание тестового платежа...")
    test_payment = client.create_payment(
        user_id=123456789,
        amount=1.00,
        currency="USDT",
        description="Тестовый платеж"
    )
    
    if test_payment.get("success"):
        payment_id = test_payment.get("payment_id")
        print(f"✅ Платеж создан: {payment_id}")
        print(f"   Сумма: {test_payment.get('amount')} {test_payment.get('currency')}")
        print(f"   Кошелек: {test_payment.get('wallet_address')}")
        
        # Тест 4: Проверка статуса платежа
        print(f"\n4. Проверка статуса платежа {payment_id}...")
        status = client.get_payment_status(payment_id)
        if status.get("success"):
            print(f"✅ Статус: {status.get('status', 'N/A')}")
        else:
            print(f"❌ Ошибка: {status.get('error', 'Неизвестная ошибка')}")
    else:
        print(f"❌ Ошибка создания платежа: {test_payment.get('error', 'Неизвестная ошибка')}")
    
    print("\n" + "=" * 40)
    print("✅ Тестирование завершено!")
