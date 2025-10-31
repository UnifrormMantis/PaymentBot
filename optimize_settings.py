#!/usr/bin/env python3
"""
Скрипт для оптимизации настроек бота в зависимости от количества кошельков
"""

import config
import os

def optimize_settings():
    """Оптимизация настроек для максимального количества платежей"""
    
    print("🔧 ОПТИМИЗАЦИЯ НАСТРОЕК БОТА")
    print("=" * 50)
    
    # Получаем количество кошельков
    try:
        from database import Database
        db = Database()
        tracked_wallets = db.get_tracked_wallets()
        wallet_count = len(tracked_wallets)
    except:
        wallet_count = 1  # По умолчанию
    
    print(f"📊 Количество отслеживаемых кошельков: {wallet_count}")
    print()
    
    # Рекомендации по интервалу
    if wallet_count <= 5:
        recommended_interval = 30
        scenario = "Небольшой проект (1-5 кошельков)"
    elif wallet_count <= 20:
        recommended_interval = 60
        scenario = "Средний проект (6-20 кошельков)"
    elif wallet_count <= 50:
        recommended_interval = 120
        scenario = "Большой проект (21-50 кошельков)"
    else:
        recommended_interval = 300
        scenario = "Крупная платформа (50+ кошельков)"
    
    print(f"🎯 Рекомендация: {scenario}")
    print(f"⏰ Оптимальный интервал: {recommended_interval} секунд")
    print()
    
    # Расчеты для рекомендуемого интервала
    total_requests = 100000
    requests_per_day = (60 / recommended_interval) * 60 * 24 * max(wallet_count, 1)  # Минимум 1 кошелек
    days_available = total_requests / requests_per_day
    avg_requests_per_payment = (60 / recommended_interval) * 60 + 2  # 1 час мониторинга + 2 запроса
    payments_available = total_requests / (avg_requests_per_payment * max(wallet_count, 1))
    
    print(f"📈 ПРОГНОЗ ПРИ ОПТИМАЛЬНЫХ НАСТРОЙКАХ:")
    print(f"   • Запросов в день: {requests_per_day:.0f}")
    print(f"   • Дней работы: {days_available:.1f}")
    print(f"   • Платежей обработано: {payments_available:.0f}")
    print()
    
    # Сравнение с текущими настройками
    current_interval = config.CHECK_INTERVAL
    current_requests_per_day = (60 / current_interval) * 60 * 24 * max(wallet_count, 1)
    current_days_available = total_requests / current_requests_per_day
    current_avg_requests_per_payment = (60 / current_interval) * 60 + 2
    current_payments_available = total_requests / (current_avg_requests_per_payment * max(wallet_count, 1))
    
    print(f"📊 СРАВНЕНИЕ С ТЕКУЩИМИ НАСТРОЙКАМИ:")
    print(f"   Текущий интервал: {current_interval}с")
    print(f"   Рекомендуемый: {recommended_interval}с")
    print()
    print(f"   Текущие настройки:")
    print(f"   • Дней работы: {current_days_available:.1f}")
    print(f"   • Платежей: {current_payments_available:.0f}")
    print()
    print(f"   Оптимальные настройки:")
    print(f"   • Дней работы: {days_available:.1f}")
    print(f"   • Платежей: {payments_available:.0f}")
    print()
    
    # Улучшение
    days_improvement = days_available - current_days_available
    payments_improvement = payments_available - current_payments_available
    
    if days_improvement > 0:
        print(f"✅ УЛУЧШЕНИЕ:")
        print(f"   • +{days_improvement:.1f} дней работы")
        print(f"   • +{payments_improvement:.0f} платежей")
    else:
        print(f"ℹ️  Текущие настройки уже оптимальны")
    print()
    
    # Предложение изменения настроек
    if recommended_interval != current_interval:
        print(f"🔧 ПРЕДЛОЖЕНИЕ ИЗМЕНЕНИЯ НАСТРОЕК:")
        print(f"   Изменить CHECK_INTERVAL с {current_interval} на {recommended_interval}")
        print()
        print(f"   В файле .env измените:")
        print(f"   CHECK_INTERVAL={recommended_interval}")
        print()
        
        # Создаем резервную копию и предлагаем изменение
        response = input("Хотите применить оптимальные настройки? (y/n): ")
        if response.lower() == 'y':
            apply_optimal_settings(recommended_interval)
    else:
        print("✅ Текущие настройки уже оптимальны!")

def apply_optimal_settings(new_interval):
    """Применить оптимальные настройки"""
    
    env_file = '.env'
    
    if os.path.exists(env_file):
        # Читаем текущий файл
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Обновляем CHECK_INTERVAL
        updated_lines = []
        for line in lines:
            if line.startswith('CHECK_INTERVAL='):
                updated_lines.append(f'CHECK_INTERVAL={new_interval}\n')
            else:
                updated_lines.append(line)
        
        # Записываем обновленный файл
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Настройки обновлены!")
        print(f"   CHECK_INTERVAL изменен на {new_interval}")
        print(f"   Перезапустите бота для применения изменений:")
        print(f"   ./stop_bot.sh && ./start_bot.sh")
    else:
        print("❌ Файл .env не найден")

if __name__ == "__main__":
    optimize_settings()
