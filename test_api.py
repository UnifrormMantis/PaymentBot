#!/usr/bin/env python3
"""
Тест API TronGrid для проверки доступности
"""

import requests
import config

def test_api():
    """Тестирование API TronGrid"""
    print("🧪 ТЕСТИРОВАНИЕ API TRONGRID")
    print("=" * 40)
    
    # Проверяем конфигурацию
    print(f"🔧 API URL: {config.TRON_API_URL}")
    print(f"🔑 API Key: {'✅ Установлен' if config.TRON_API_KEY else '❌ Не установлен'}")
    print(f"💎 USDT Contract: {config.USDT_CONTRACT_ADDRESS}")
    print()
    
    if not config.TRON_API_KEY:
        print("❌ Ошибка: API ключ не установлен!")
        return
    
    headers = {
        'TRON-PRO-API-KEY': config.TRON_API_KEY
    }
    
    # Тестируем простой endpoint
    test_url = f"{config.TRON_API_URL}/v1/blocks/latest"
    print(f"🔍 Тестируем endpoint: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API доступен!")
            data = response.json()
            print(f"📦 Последний блок: {data.get('block_header', {}).get('raw_data', {}).get('number', 'N/A')}")
        else:
            print(f"❌ Ошибка API: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    
    print()
    
    # Тестируем endpoint для токенов
    test_address = "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"  # Ваш кошелек
    tokens_url = f"{config.TRON_API_URL}/v1/accounts/{test_address}/tokens"
    print(f"🔍 Тестируем токены для: {test_address}")
    print(f"📡 URL: {tokens_url}")
    
    try:
        response = requests.get(tokens_url, headers=headers, timeout=10)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint токенов работает!")
            data = response.json()
            tokens = data.get('data', [])
            print(f"📦 Найдено токенов: {len(tokens)}")
            
            for token in tokens:
                if token.get('contract_address') == config.USDT_CONTRACT_ADDRESS:
                    balance = float(token.get('balance', 0)) / 1000000
                    print(f"💰 USDT баланс: {balance}")
                    break
            else:
                print("💡 USDT токен не найден в списке")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_api()





