#!/usr/bin/env python3
"""
Скрипт для восстановления кошелька пользователя
"""

import sys
from database import Database
from tron_tracker import TronTracker

def restore_wallet(user_id: int, wallet_address: str):
    """Восстановить кошелек пользователя"""
    print(f"🔧 ВОССТАНОВЛЕНИЕ КОШЕЛЬКА")
    print("=" * 40)
    
    # Создаем экземпляры
    db = Database()
    tracker = TronTracker()
    
    # Проверяем валидность адреса
    if not tracker.validate_address(wallet_address):
        print(f"❌ Неверный адрес кошелька: {wallet_address}")
        return False
    
    # Обновляем кошелек в базе
    db.update_user_wallet(user_id, wallet_address)
    print(f"✅ Кошелек {wallet_address} восстановлен для пользователя {user_id}")
    
    # Проверяем баланс
    try:
        balance = tracker.get_balance(wallet_address)
        print(f"💰 Баланс USDT: {balance}")
    except Exception as e:
        print(f"⚠️  Ошибка проверки баланса: {e}")
    
    return True

def main():
    """Главная функция"""
    if len(sys.argv) != 3:
        print("Использование: python restore_wallet.py <user_id> <wallet_address>")
        print("Пример: python restore_wallet.py 798427688 TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx")
        return
    
    user_id = int(sys.argv[1])
    wallet_address = sys.argv[2]
    
    restore_wallet(user_id, wallet_address)

if __name__ == "__main__":
    main()





