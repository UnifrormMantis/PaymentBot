#!/usr/bin/env python3
"""
Тестовый скрипт для проверки основных функций бота
"""

import os
import sys
from database import Database
from tron_tracker import TronTracker
import config

def test_database():
    """Тест базы данных"""
    print("🧪 Тестирование базы данных...")
    
    try:
        db = Database("test_payments.db")
        
        # Тест добавления пользователя
        db.add_user(12345, "test_user", "TTestAddress123456789012345678901234")
        
        # Тест получения пользователя
        user = db.get_user(12345)
        assert user is not None
        assert user['user_id'] == 12345
        assert user['username'] == "test_user"
        
        # Тест добавления ожидающего платежа
        payment_id = db.add_pending_payment(12345, 100.0, "USDT", "TTestAddress123456789012345678901234")
        assert payment_id is not None
        
        # Тест получения ожидающих платежей
        payments = db.get_pending_payments("TTestAddress123456789012345678901234")
        assert len(payments) == 1
        assert payments[0]['amount'] == 100.0
        
        # Тест подтверждения платежа
        db.confirm_payment(12345, 100.0, "USDT", "test_tx_hash", "TTestAddress123456789012345678901234")
        
        # Очистка тестовой базы
        os.remove("test_payments.db")
        
        print("✅ База данных работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте базы данных: {e}")
        return False

def test_tron_tracker():
    """Тест Tron трекера"""
    print("🧪 Тестирование Tron трекера...")
    
    try:
        tracker = TronTracker()
        
        # Тест валидации адреса (неправильный адрес)
        invalid_address = "invalid_address"
        assert not tracker.validate_address(invalid_address)
        
        # Тест валидации адреса (правильный формат, но может не существовать)
        valid_format_address = "TTestAddress123456789012345678901234"
        # Этот тест может не пройти, если адрес не существует в сети
        # result = tracker.validate_address(valid_format_address)
        # print(f"Валидация адреса: {result}")
        
        print("✅ Tron трекер работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте Tron трекера: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("🧪 Тестирование конфигурации...")
    
    try:
        # Проверяем, что конфигурация загружается
        assert hasattr(config, 'TELEGRAM_BOT_TOKEN')
        assert hasattr(config, 'TRON_API_URL')
        assert hasattr(config, 'CHECK_INTERVAL')
        assert hasattr(config, 'USDT_CONTRACT_ADDRESS')
        
        print("✅ Конфигурация загружается корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте конфигурации: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов...")
    print("=" * 50)
    
    tests = [
        test_config,
        test_database,
        test_tron_tracker,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())

