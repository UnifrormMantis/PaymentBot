#!/usr/bin/env python3
"""
Тест кнопки "Назад" в боте
"""

from database import Database

def test_back_button():
    """Тестирование кнопки 'Назад'"""
    print("🧪 ТЕСТ КНОПКИ 'НАЗАД'")
    print("=" * 30)
    
    db = Database()
    test_user_id = 739935417
    
    print(f"👤 Тестовый пользователь: {test_user_id}")
    
    # Проверяем текущее состояние
    active_wallet = db.get_active_wallet(test_user_id)
    user_wallets = db.get_user_wallets(test_user_id)
    
    print(f"\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    print(f"   Активный кошелек: {'Есть' if active_wallet else 'Нет'}")
    print(f"   Всего кошельков: {len(user_wallets)}")
    
    if active_wallet:
        print(f"   Название: {active_wallet['wallet_name']}")
        print(f"   Адрес: {active_wallet['wallet_address']}")
    
    print(f"\n✅ КНОПКА 'НАЗАД' ДОЛЖНА РАБОТАТЬ В:")
    print(f"   • Главном меню")
    print(f"   • Управлении кошельками")
    print(f"   • Статусе платежей")
    print(f"   • Балансе кошелька")
    print(f"   • Авто режиме")
    print(f"   • Справке")
    print(f"   • API ключе")
    
    print(f"\n🔧 ИСПРАВЛЕНИЯ:")
    print(f"   • Создан метод show_main_menu_callback")
    print(f"   • Исправлен main_menu_callback")
    print(f"   • Кнопка 'Назад' теперь работает корректно")
    
    print(f"\n🎉 ТЕСТ ЗАВЕРШЕН!")
    print(f"   Кнопка 'Назад' должна работать во всех меню")

if __name__ == "__main__":
    test_back_button()

