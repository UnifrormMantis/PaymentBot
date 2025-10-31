#!/usr/bin/env python3
"""
Тест совместимости: ротация активных кошельков каждые 20 секунд
"""

import sqlite3
import time
import requests
import json
from datetime import datetime

# Настройки
DATABASE_PATH = "payments.db"
API_URL = "http://localhost:8001"
API_KEY = "rsG7Hzt0EaEY5ZoEH4eE96SiY234qpiSYg5d92xrSm4"

# Список кошельков для ротации
WALLETS = [
    "TRpxhgJ9izoZ56iHJ6gkWwvuStaMeCTisS",
    "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx", 
    "TPersistenceTest123456789012345678901234"
]

def get_active_wallet():
    """Получить текущий активный кошелек из базы данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT wallet_address FROM user_wallets 
        WHERE is_active = 1 
        ORDER BY created_at DESC
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def set_active_wallet(wallet_address):
    """Установить активный кошелек"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Деактивируем все кошельки
    cursor.execute('UPDATE user_wallets SET is_active = 0')
    
    # Активируем нужный кошелек
    cursor.execute('UPDATE user_wallets SET is_active = 1 WHERE wallet_address = ?', (wallet_address,))
    
    conn.commit()
    conn.close()
    
    print(f"🔄 Активирован кошелек: {wallet_address}")

def test_api_response():
    """Тестировать ответ API"""
    try:
        response = requests.post(
            f"{API_URL}/get-payment-wallet",
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json={"user_wallet": "TTestUser123456789"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('wallet_address')
            else:
                return f"❌ API Error: {data.get('error')}"
        else:
            return f"❌ HTTP Error: {response.status_code}"
            
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

def main():
    """Основная функция теста"""
    print("🧪 ТЕСТ СОВМЕСТИМОСТИ PAYMENT BOT API")
    print("=" * 50)
    print(f"⏰ Начало теста: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🔄 Ротация каждые 20 секунд")
    print(f"⏱️  Продолжительность: 200 секунд (10 циклов)")
    print("=" * 50)
    
    wallet_index = 0
    test_duration = 200  # 200 секунд
    rotation_interval = 20  # 20 секунд
    start_time = time.time()
    
    while time.time() - start_time < test_duration:
        current_time = datetime.now().strftime('%H:%M:%S')
        elapsed = int(time.time() - start_time)
        remaining = test_duration - elapsed
        
        # Получаем текущий кошелек для активации
        current_wallet = WALLETS[wallet_index % len(WALLETS)]
        
        print(f"\n⏰ {current_time} | Прошло: {elapsed}s | Осталось: {remaining}s")
        print(f"🔄 Активируем кошелек: {current_wallet}")
        
        # Активируем кошелек
        set_active_wallet(current_wallet)
        
        # Ждем 2 секунды для стабилизации
        time.sleep(2)
        
        # Проверяем базу данных
        db_wallet = get_active_wallet()
        print(f"📊 База данных: {db_wallet}")
        
        # Проверяем API
        api_wallet = test_api_response()
        print(f"🌐 API ответ: {api_wallet}")
        
        # Проверяем совместимость
        if db_wallet == api_wallet:
            print("✅ СОВМЕСТИМОСТЬ: OK")
        else:
            print("❌ СОВМЕСТИМОСТЬ: ОШИБКА!")
        
        # Переходим к следующему кошельку
        wallet_index += 1
        
        # Ждем до следующей ротации
        if remaining > rotation_interval:
            print(f"⏳ Ждем {rotation_interval} секунд до следующей ротации...")
            time.sleep(rotation_interval)
        else:
            print(f"⏳ Ждем {remaining} секунд до завершения теста...")
            time.sleep(remaining)
    
    print("\n" + "=" * 50)
    print("🎉 ТЕСТ ЗАВЕРШЕН!")
    print(f"⏰ Время завершения: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main()





