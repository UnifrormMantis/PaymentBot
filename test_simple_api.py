#!/usr/bin/env python3
"""
Простой тест API без ключа для проверки баланса
"""

import requests
import json

def test_simple_api():
    """Тестирование простого API"""
    print("🧪 ТЕСТИРОВАНИЕ ПРОСТОГО API")
    print("=" * 40)
    
    # Ваш кошелек
    address = "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
    print(f"💳 Тестируем кошелек: {address}")
    print()
    
    # Пробуем разные API endpoints
    apis = [
        {
            "name": "TronGrid (без ключа)",
            "url": f"https://api.trongrid.io/v1/accounts/{address}",
            "method": "GET"
        },
        {
            "name": "TronGrid Wallet",
            "url": "https://api.trongrid.io/wallet/getaccount",
            "method": "POST",
            "data": {"address": address, "visible": True}
        },
        {
            "name": "TronScan API",
            "url": f"https://apilist.tronscanapi.com/api/account?address={address}",
            "method": "GET"
        }
    ]
    
    for api in apis:
        print(f"🔍 Тестируем: {api['name']}")
        print(f"📡 URL: {api['url']}")
        
        try:
            if api['method'] == 'GET':
                response = requests.get(api['url'], timeout=10)
            else:
                response = requests.post(api['url'], json=api.get('data', {}), timeout=10)
            
            print(f"📊 Статус: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Успешно!")
                
                # Ищем USDT баланс в разных форматах
                usdt_balance = None
                
                # Проверяем разные поля
                if 'data' in data:
                    if isinstance(data['data'], list):
                        for item in data['data']:
                            if item.get('contract_address') == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':
                                usdt_balance = float(item.get('balance', 0)) / 1000000
                                break
                    elif isinstance(data['data'], dict):
                        trc20 = data['data'].get('trc20', [])
                        for token in trc20:
                            if token.get('contract_address') == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':
                                usdt_balance = float(token.get('balance', 0)) / 1000000
                                break
                
                # Проверяем trc20 напрямую
                if not usdt_balance and 'trc20' in data:
                    for token in data['trc20']:
                        if token.get('contract_address') == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':
                            usdt_balance = float(token.get('balance', 0)) / 1000000
                            break
                
                if usdt_balance is not None:
                    print(f"💰 USDT баланс: {usdt_balance}")
                else:
                    print("💡 USDT баланс не найден в ответе")
                    print(f"📦 Структура ответа: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"❌ Ошибка: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_simple_api()





