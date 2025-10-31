#!/usr/bin/env python3
"""
Скрипт для тестирования получения баланса USDT
"""

import sys
from tron_tracker import TronTracker
from database import Database

def test_balance():
    """Тестирование получения баланса"""
    print("🧪 ТЕСТИРОВАНИЕ БАЛАНСА USDT")
    print("=" * 40)
    
    # Создаем экземпляры
    tracker = TronTracker()
    db = Database()
    
    # Получаем пользователей из базы
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, wallet_address FROM users WHERE wallet_address IS NOT NULL AND wallet_address != ""')
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("❌ Нет пользователей с кошельками в базе данных")
        return
    
    print(f"👥 Найдено {len(users)} пользователей с кошельками:")
    print()
    
    for user_id, username, wallet_address in users:
        print(f"👤 Пользователь: {username} (ID: {user_id})")
        print(f"💳 Кошелек: {wallet_address}")
        
        # Тестируем получение баланса
        try:
            balance = tracker.get_balance(wallet_address)
            print(f"💰 Баланс USDT: {balance}")
            
            # Также тестируем через get_usdt_balance
            balance2 = tracker.get_usdt_balance(wallet_address)
            print(f"💰 Баланс через get_usdt_balance: {balance2}")
            
        except Exception as e:
            print(f"❌ Ошибка получения баланса: {e}")
        
        print("-" * 40)
    
    print()
    print("💡 ВАЖНО:")
    print("   • Если баланс показывает 0, но в кошельке есть USDT,")
    print("     это может быть проблема с API или неправильным адресом")
    print("   • Убедитесь, что кошелек правильный и содержит USDT")
    print("   • Проверьте, что API ключ TronGrid работает")

if __name__ == "__main__":
    test_balance()





