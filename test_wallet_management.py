#!/usr/bin/env python3
"""
Тест новой системы управления кошельками
"""

from database import Database

def test_wallet_management():
    """Тестирование системы управления кошельками"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ УПРАВЛЕНИЯ КОШЕЛЬКАМИ")
    print("=" * 50)
    
    db = Database()
    
    # Тестовый пользователь
    test_user_id = 739935417
    
    print(f"👤 Тестовый пользователь: {test_user_id}")
    
    # Очищаем старые кошельки пользователя
    print("\n🧹 Очистка старых кошельков...")
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_wallets WHERE user_id = ?', (test_user_id,))
    conn.commit()
    conn.close()
    print("✅ Старые кошельки удалены")
    
    # Тест 1: Добавление кошельков
    print("\n1️⃣ ДОБАВЛЕНИЕ КОШЕЛЬКОВ:")
    wallets_to_add = [
        "TTestWallet1234567890123456789012345",
        "TAnotherWallet1234567890123456789012",
        "TThirdWallet123456789012345678901234"
    ]
    
    for i, wallet_address in enumerate(wallets_to_add, 1):
        wallet_name = f"Тестовый кошелек {i}"
        db.add_user_wallet(test_user_id, wallet_address, wallet_name)
        print(f"   ✅ Добавлен: {wallet_name} ({wallet_address})")
    
    # Тест 2: Получение списка кошельков
    print("\n2️⃣ ПОЛУЧЕНИЕ СПИСКА КОШЕЛЬКОВ:")
    wallets = db.get_user_wallets(test_user_id)
    print(f"   📊 Всего кошельков: {len(wallets)}")
    
    for wallet in wallets:
        status = "🟢 АКТИВНЫЙ" if wallet['is_active'] else "⚪ Неактивный"
        print(f"   {status} {wallet['wallet_name']} ({wallet['wallet_address']})")
    
    # Тест 3: Установка активного кошелька
    print("\n3️⃣ УСТАНОВКА АКТИВНОГО КОШЕЛЬКА:")
    if wallets:
        first_wallet_id = wallets[0]['id']
        db.set_active_wallet(test_user_id, first_wallet_id)
        print(f"   ✅ Активирован кошелек: {wallets[0]['wallet_name']}")
        
        # Проверяем активный кошелек
        active_wallet = db.get_active_wallet(test_user_id)
        if active_wallet:
            print(f"   🟢 Активный кошелек: {active_wallet['wallet_name']}")
        else:
            print("   ❌ Активный кошелек не найден")
    
    # Тест 4: Удаление кошелька
    print("\n4️⃣ УДАЛЕНИЕ КОШЕЛЬКА:")
    if len(wallets) > 1:
        wallet_to_delete = wallets[1]
        db.delete_user_wallet(test_user_id, wallet_to_delete['id'])
        print(f"   🗑️ Удален кошелек: {wallet_to_delete['wallet_name']}")
        
        # Проверяем, что кошелек удален
        remaining_wallets = db.get_user_wallets(test_user_id)
        print(f"   📊 Осталось кошельков: {len(remaining_wallets)}")
    
    # Тест 5: Финальное состояние
    print("\n5️⃣ ФИНАЛЬНОЕ СОСТОЯНИЕ:")
    final_wallets = db.get_user_wallets(test_user_id)
    active_wallet = db.get_active_wallet(test_user_id)
    
    print(f"   📊 Всего кошельков: {len(final_wallets)}")
    for wallet in final_wallets:
        status = "🟢 АКТИВНЫЙ" if wallet['is_active'] else "⚪ Неактивный"
        print(f"   {status} {wallet['wallet_name']}")
    
    if active_wallet:
        print(f"   🟢 Активный кошелек: {active_wallet['wallet_name']}")
    else:
        print("   ❌ Нет активного кошелька")
    
    print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 50)

if __name__ == "__main__":
    test_wallet_management()

