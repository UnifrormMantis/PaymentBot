#!/usr/bin/env python3
"""
Простой клиент для интеграции платежей
Как у популярных платежных ботов - один API ключ и все работает
"""

import requests
import time
import json
from typing import Optional, Dict, Any

class SimplePaymentClient:
    """
    Простой клиент для работы с Payment API
    Как у популярных платежных ботов
    """
    
    def __init__(self, api_key: str, api_url: str = "http://localhost:8001"):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ для авторизации
            api_url: URL API сервера
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, amount: float, currency: str = "USDT", 
                      description: str = None, callback_url: str = None) -> Dict[str, Any]:
        """
        Создать платеж
        
        Args:
            amount: Сумма платежа
            currency: Валюта (по умолчанию USDT)
            description: Описание платежа
            callback_url: URL для callback уведомлений
            
        Returns:
            Результат создания платежа
        """
        data = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "callback_url": callback_url
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/create-payment",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Проверить статус платежа
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Статус платежа
        """
        try:
            response = requests.get(
                f"{self.api_url}/check-payment/{payment_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def wait_for_payment(self, payment_id: str, timeout: int = 300, 
                        check_interval: int = 10) -> Dict[str, Any]:
        """
        Ждать завершения платежа
        
        Args:
            payment_id: ID платежа
            timeout: Максимальное время ожидания в секундах
            check_interval: Интервал проверки в секундах
            
        Returns:
            Результат платежа
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.check_payment(payment_id)
            
            if result.get('success') and result.get('status') == 'completed':
                return result
            elif result.get('success') and result.get('status') == 'failed':
                return result
            
            time.sleep(check_interval)
        
        return {
            "success": False,
            "error": "Timeout: платеж не завершен в указанное время"
        }

# Пример использования
def main():
    """Пример использования простого клиента"""
    print("🚀 Пример использования Simple Payment Client")
    print("=" * 50)
    
    # Получаем API ключ
    print("1️⃣ Получение API ключа...")
    try:
        response = requests.get("http://localhost:8001/get-api-key")
        if response.status_code == 200:
            api_data = response.json()
            api_key = api_data['api_key']
            print(f"✅ API ключ получен: {api_key[:20]}...")
        else:
            print("❌ Ошибка получения API ключа")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # Создаем клиент
    client = SimplePaymentClient(api_key)
    
    # Создаем платеж
    print("\n2️⃣ Создание платежа...")
    payment_result = client.create_payment(
        amount=100.0,
        currency="USDT",
        description="Тестовый платеж",
        callback_url="https://yourbot.com/webhook/payment"
    )
    
    if payment_result['success']:
        payment_id = payment_result['payment_id']
        wallet_address = payment_result['wallet_address']
        amount = payment_result['amount']
        
        print(f"✅ Платеж создан:")
        print(f"   ID: {payment_id}")
        print(f"   Сумма: {amount} USDT")
        print(f"   Кошелек: {wallet_address}")
        
        # Проверяем статус
        print(f"\n3️⃣ Проверка статуса платежа...")
        status_result = client.check_payment(payment_id)
        
        if status_result['success']:
            print(f"✅ Статус: {status_result['status']}")
        else:
            print(f"❌ Ошибка: {status_result['error']}")
        
        # Ждем завершения (в реальном проекте это делается в фоне)
        print(f"\n4️⃣ Ожидание завершения платежа...")
        print("   (В реальном проекте это делается в фоне)")
        
    else:
        print(f"❌ Ошибка создания платежа: {payment_result['error']}")

if __name__ == "__main__":
    main()





