#!/usr/bin/env python3
"""
Мониторинг потребления запросов в реальном времени
Показывает, сколько запросов осталось и когда закончатся
"""

import time
import config
from datetime import datetime, timedelta

def monitor_requests():
    """Мониторинг потребления запросов"""
    
    print("📊 МОНИТОРИНГ ПОТРЕБЛЕНИЯ ЗАПРОСОВ")
    print("=" * 50)
    
    # Настройки
    check_interval = config.CHECK_INTERVAL
    total_requests = 100000
    requests_per_minute = 60 / check_interval
    requests_per_hour = requests_per_minute * 60
    requests_per_day = requests_per_hour * 24
    
    print(f"🔧 Настройки:")
    print(f"   • Интервал проверки: {check_interval} секунд")
    print(f"   • Запросов в минуту: {requests_per_minute:.1f}")
    print(f"   • Запросов в час: {requests_per_hour:.0f}")
    print(f"   • Запросов в день: {requests_per_day:.0f}")
    print()
    
    # Симуляция работы
    print("🎭 СИМУЛЯЦИЯ РАБОТЫ БОТА:")
    print("   (Показываем потребление запросов в реальном времени)")
    print()
    
    # Показываем потребление по часам
    for hour in range(24):
        time_str = f"{hour:02d}:00"
        requests_used = hour * requests_per_hour
        requests_remaining = total_requests - requests_used
        
        if requests_remaining <= 0:
            print(f"   {time_str} - 🔴 ЗАПРОСЫ ЗАКОНЧИЛИСЬ!")
            break
        
        # Показываем прогресс
        progress = (requests_used / total_requests) * 100
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"   {time_str} - {bar} {progress:.1f}% (осталось {requests_remaining:.0f})")
        
        # Небольшая пауза для демонстрации
        time.sleep(0.1)
    
    print()
    
    # Показываем потребление по дням
    print("📅 ПОТРЕБЛЕНИЕ ПО ДНЯМ:")
    days_available = total_requests / requests_per_day
    
    for day in range(1, min(8, int(days_available) + 2)):  # Показываем первые 7 дней
        requests_used = day * requests_per_day
        requests_remaining = total_requests - requests_used
        
        if requests_remaining <= 0:
            print(f"   День {day} - 🔴 ЗАПРОСЫ ЗАКОНЧИЛИСЬ!")
            break
        
        # Показываем прогресс
        progress = (requests_used / total_requests) * 100
        bar_length = 30
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"   День {day} - {bar} {progress:.1f}% (осталось {requests_remaining:.0f})")
    
    print()
    
    # Показываем когда закончатся запросы
    print("⏰ КОГДА ЗАКОНЧАТСЯ ЗАПРОСЫ:")
    start_time = datetime.now()
    end_time = start_time + timedelta(days=days_available)
    
    print(f"   • Начало работы: {start_time.strftime('%d.%m.%Y %H:%M')}")
    print(f"   • Конец работы: {end_time.strftime('%d.%m.%Y %H:%M')}")
    print(f"   • Дней работы: {days_available:.1f}")
    print(f"   • Часов работы: {days_available * 24:.0f}")
    print()
    
    # Показываем что происходит в последний день
    print("🔴 ПОСЛЕДНИЙ ДЕНЬ РАБОТЫ:")
    last_day = int(days_available)
    requests_on_last_day = total_requests - (last_day - 1) * requests_per_day
    
    print(f"   • День {last_day}: {requests_on_last_day:.0f} запросов")
    print(f"   • Время работы: {requests_on_last_day / requests_per_hour:.1f} часов")
    print(f"   • Остановка в: {end_time.strftime('%H:%M')}")
    print()
    
    # Показываем что происходит после остановки
    print("⚠️  ПОСЛЕ ОСТАНОВКИ БОТА:")
    print("   • Новые платежи не отслеживаются")
    print("   • Пользователи не получают подтверждения")
    print("   • Нужно пополнить лимит запросов")
    print("   • Или изменить настройки бота")
    print()
    
    # Рекомендации
    print("💡 РЕКОМЕНДАЦИИ:")
    print("   • Мониторьте потребление запросов")
    print("   • Планируйте пополнение лимитов")
    print("   • Настройте уведомления о низком балансе")
    print("   • Рассмотрите webhook'и для экономии")

if __name__ == "__main__":
    monitor_requests()





