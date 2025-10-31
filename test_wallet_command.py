#!/usr/bin/env python3
"""
Тест команды /wallet
"""

from database import Database

def test_wallet_update():
    """Тестирование обновления кошелька"""
    print("🧪 ТЕСТИРОВАНИЕ КОМАНДЫ /WALLET")
    print("=" * 40)
    
    db = Database()
    
    # Тестовый пользователь
    test_user_id = 739935417
    test_wallet = "TTestWallet1234567890123456789012345"
    
    print(f"👤 Тестовый пользователь: {test_user_id}")
    print(f"💳 Тестовый кошелек: {test_wallet}")
    
    # Проверяем текущее состояние
    user_before = db.get_user(test_user_id)
    print(f"\n📊 ДО обновления:")
    if user_before:
        print(f"   Кошелек: {user_before['wallet_address']}")
        print(f"   Авторежим: {user_before['auto_mode']}")
    else:
        print("   Пользователь не найден")
    
    # Обновляем кошелек
    print(f"\n🔄 Обновляем кошелек...")
    try:
        db.update_user_wallet(test_user_id, test_wallet)
        print("✅ Обновление выполнено")
    except Exception as e:
        print(f"❌ Ошибка обновления: {e}")
        return
    
    # Проверяем результат
    user_after = db.get_user(test_user_id)
    print(f"\n📊 ПОСЛЕ обновления:")
    if user_after:
        print(f"   Кошелек: {user_after['wallet_address']}")
        print(f"   Авторежим: {user_after['auto_mode']}")
        
        if user_after['wallet_address'] == test_wallet:
            print("✅ Кошелек успешно обновлен!")
        else:
            print("❌ Кошелек не обновился")
    else:
        print("❌ Пользователь не найден после обновления")

if __name__ == "__main__":
    test_wallet_update()

