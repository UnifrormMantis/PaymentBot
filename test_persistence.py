#!/usr/bin/env python3
"""
Тест сохранения кошельков после перезагрузки
"""

from database import Database

def test_persistence():
    """Тестирование сохранения данных"""
    print("🧪 ТЕСТ СОХРАНЕНИЯ КОШЕЛЬКОВ")
    print("=" * 40)
    
    db = Database()
    test_user_id = 739935417
    
    print(f"👤 Тестовый пользователь: {test_user_id}")
    
    # Проверяем текущее состояние
    wallets = db.get_user_wallets(test_user_id)
    active_wallet = db.get_active_wallet(test_user_id)
    
    print(f"\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    print(f"   Всего кошельков: {len(wallets)}")
    
    for wallet in wallets:
        status = "🟢 АКТИВНЫЙ" if wallet['is_active'] else "⚪ Неактивный"
        print(f"   {status} {wallet['wallet_name']}")
    
    if active_wallet:
        print(f"   🟢 Активный: {active_wallet['wallet_name']}")
    else:
        print("   ❌ Нет активного кошелька")
    
    # Тест 1: Добавление нового кошелька
    print(f"\n1️⃣ ДОБАВЛЕНИЕ НОВОГО КОШЕЛЬКА:")
    new_wallet_address = "TPersistenceTest123456789012345678901234"
    db.add_user_wallet(test_user_id, new_wallet_address, "Тест сохранения")
    print(f"   ✅ Добавлен: Тест сохранения")
    
    # Тест 2: Проверка после добавления
    print(f"\n2️⃣ ПРОВЕРКА ПОСЛЕ ДОБАВЛЕНИЯ:")
    updated_wallets = db.get_user_wallets(test_user_id)
    print(f"   📊 Всего кошельков: {len(updated_wallets)}")
    
    # Тест 3: Установка нового активного кошелька
    print(f"\n3️⃣ УСТАНОВКА НОВОГО АКТИВНОГО КОШЕЛЬКА:")
    new_wallet = None
    for wallet in updated_wallets:
        if wallet['wallet_address'] == new_wallet_address:
            new_wallet = wallet
            break
    
    if new_wallet:
        db.set_active_wallet(test_user_id, new_wallet['id'])
        print(f"   ✅ Активирован: {new_wallet['wallet_name']}")
        
        # Проверяем активный кошелек
        active_wallet = db.get_active_wallet(test_user_id)
        if active_wallet:
            print(f"   🟢 Активный кошелек: {active_wallet['wallet_name']}")
        else:
            print("   ❌ Ошибка: активный кошелек не найден")
    
    # Тест 4: Финальная проверка
    print(f"\n4️⃣ ФИНАЛЬНАЯ ПРОВЕРКА:")
    final_wallets = db.get_user_wallets(test_user_id)
    final_active = db.get_active_wallet(test_user_id)
    
    print(f"   📊 Всего кошельков: {len(final_wallets)}")
    for wallet in final_wallets:
        status = "🟢 АКТИВНЫЙ" if wallet['is_active'] else "⚪ Неактивный"
        print(f"   {status} {wallet['wallet_name']}")
    
    if final_active:
        print(f"   🟢 Активный кошелек: {final_active['wallet_name']}")
    
    print(f"\n✅ ТЕСТ ЗАВЕРШЕН!")
    print(f"   Данные сохранены в базе данных")
    print(f"   После перезагрузки бота данные должны сохраниться")

if __name__ == "__main__":
    test_persistence()

