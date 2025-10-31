#!/usr/bin/env python3
"""
Ротация активных кошельков каждые 20 секунд
"""

import sqlite3
import time
from datetime import datetime

# Настройки
DATABASE_PATH = "payments.db"

# Список кошельков для ротации
WALLETS = [
    "TRpxhgJ9izoZ56iHJ6gkWwvuStaMeCTisS",
    "TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx", 
    "TPersistenceTest123456789012345678901234"
]

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
    
    print(f"🔄 {datetime.now().strftime('%H:%M:%S')} - Активирован: {wallet_address}")

def main():
    """Основная функция ротации"""
    print("🔄 РОТАЦИЯ АКТИВНЫХ КОШЕЛЬКОВ")
    print("=" * 50)
    print(f"⏰ Начало: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🔄 Ротация каждые 20 секунд")
    print(f"⏱️  Продолжительность: 300 секунд (15 циклов)")
    print("=" * 50)
    
    wallet_index = 0
    test_duration = 300  # 300 секунд
    rotation_interval = 20  # 20 секунд
    start_time = time.time()
    
    while time.time() - start_time < test_duration:
        current_time = datetime.now().strftime('%H:%M:%S')
        elapsed = int(time.time() - start_time)
        remaining = test_duration - elapsed
        
        # Получаем текущий кошелек для активации
        current_wallet = WALLETS[wallet_index % len(WALLETS)]
        
        print(f"\n⏰ {current_time} | Прошло: {elapsed}s | Осталось: {remaining}s")
        
        # Активируем кошелек
        set_active_wallet(current_wallet)
        
        # Переходим к следующему кошельку
        wallet_index += 1
        
        # Ждем до следующей ротации
        if remaining > rotation_interval:
            print(f"⏳ Ждем {rotation_interval} секунд...")
            time.sleep(rotation_interval)
        else:
            print(f"⏳ Ждем {remaining} секунд до завершения...")
            time.sleep(remaining)
    
    print("\n" + "=" * 50)
    print("🎉 РОТАЦИЯ ЗАВЕРШЕНА!")
    print(f"⏰ Время завершения: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main()





