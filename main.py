#!/usr/bin/env python3
"""
Telegram Bot для отслеживания TRC20 платежей
Автоматически подтверждает платежи при поступлении на отслеживаемый кошелек
"""

import os
import sys
import signal
import time
from private_bot import PrivatePaymentBot

def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения"""
    print('\n🛑 Получен сигнал завершения. Останавливаем бота...')
    sys.exit(0)

def check_environment():
    """Проверка переменных окружения"""
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Ошибка: Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Создайте файл .env на основе env_example.txt")
        return False
    
    return True

def main():
    """Главная функция"""
    print("🚀 Запуск Telegram бота для отслеживания TRC20 платежей...")
    
    # Проверяем переменные окружения
    if not check_environment():
        return 1
    
    # Настраиваем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создаем и запускаем приватный бот
        bot = PrivatePaymentBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
        return 0
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
