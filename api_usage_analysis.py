#!/usr/bin/env python3
"""
Анализ потребления Tron API запросов
Расчет на сколько платежей хватит 100,000 запросов
"""

import config
from datetime import datetime, timedelta

def analyze_api_usage():
    """Анализ потребления API запросов"""
    
    print("📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПОТРЕБЛЕНИЯ TRON API")
    print("=" * 60)
    
    # Текущие настройки
    check_interval = config.CHECK_INTERVAL
    total_requests = 100000
    
    print(f"🔧 Текущие настройки:")
    print(f"   • Интервал проверки: {check_interval} секунд")
    print(f"   • Доступно запросов: {total_requests:,}")
    print()
    
    # Базовые расчеты
    requests_per_minute = 60 / check_interval
    requests_per_hour = requests_per_minute * 60
    requests_per_day = requests_per_hour * 24
    requests_per_week = requests_per_day * 7
    requests_per_month = requests_per_day * 30
    
    print("📈 ПОТРЕБЛЕНИЕ ЗАПРОСОВ:")
    print(f"   • В минуту: {requests_per_minute:.1f}")
    print(f"   • В час: {requests_per_hour:.0f}")
    print(f"   • В день: {requests_per_day:.0f}")
    print(f"   • В неделю: {requests_per_week:.0f}")
    print(f"   • В месяц: {requests_per_month:.0f}")
    print()
    
    # Время работы при разных сценариях
    print("⏰ ВРЕМЯ РАБОТЫ ПРИ 100,000 ЗАПРОСОВ:")
    
    # 1 кошелек
    days_1_wallet = total_requests / requests_per_day
    print(f"   • 1 кошелек: {days_1_wallet:.1f} дней ({days_1_wallet/30:.1f} месяцев)")
    
    # 10 кошельков
    days_10_wallets = total_requests / (requests_per_day * 10)
    print(f"   • 10 кошельков: {days_10_wallets:.1f} дней ({days_10_wallets/30:.1f} месяцев)")
    
    # 50 кошельков
    days_50_wallets = total_requests / (requests_per_day * 50)
    print(f"   • 50 кошельков: {days_50_wallets:.1f} дней ({days_50_wallets/30:.1f} месяцев)")
    
    # 100 кошельков
    days_100_wallets = total_requests / (requests_per_day * 100)
    print(f"   • 100 кошельков: {days_100_wallets:.1f} дней ({days_100_wallets/30:.1f} месяцев)")
    print()
    
    # Расчет количества платежей
    print("💳 КОЛИЧЕСТВО ПЛАТЕЖЕЙ:")
    
    # Предполагаем, что каждый платеж требует:
    # - 1 запрос для проверки транзакций при создании
    # - N запросов для мониторинга до подтверждения
    # - 1 запрос для подтверждения
    
    # Среднее время ожидания платежа: 1 час (120 запросов при интервале 30с)
    avg_requests_per_payment = 120 + 2  # мониторинг + создание + подтверждение
    
    payments_1_wallet = total_requests / avg_requests_per_payment
    payments_10_wallets = total_requests / (avg_requests_per_payment * 10)
    payments_50_wallets = total_requests / (avg_requests_per_payment * 50)
    payments_100_wallets = total_requests / (avg_requests_per_payment * 100)
    
    print(f"   • 1 кошелек: {payments_1_wallet:.0f} платежей")
    print(f"   • 10 кошельков: {payments_10_wallets:.0f} платежей")
    print(f"   • 50 кошельков: {payments_50_wallets:.0f} платежей")
    print(f"   • 100 кошельков: {payments_100_wallets:.0f} платежей")
    print()
    
    # Оптимизация интервалов
    print("💡 ОПТИМИЗАЦИЯ ИНТЕРВАЛОВ:")
    
    intervals = [30, 60, 120, 300, 600]  # секунды
    
    for interval in intervals:
        req_per_day = (60 / interval) * 60 * 24
        days_available = total_requests / req_per_day
        payments_available = total_requests / ((60 / interval) * 60 + 2)  # 1 час мониторинга + 2 запроса
        
        print(f"   • Интервал {interval}с: {days_available:.0f} дней, {payments_available:.0f} платежей")
    print()
    
    # Рекомендации
    print("🎯 РЕКОМЕНДАЦИИ:")
    print("   1. Для 1-10 кошельков: интервал 30-60 секунд")
    print("   2. Для 10-50 кошельков: интервал 60-120 секунд")
    print("   3. Для 50+ кошельков: интервал 120-300 секунд")
    print("   4. Используйте webhook'и для уменьшения запросов")
    print("   5. Кэшируйте результаты запросов")
    print()
    
    # Стоимость
    print("💰 СТОИМОСТЬ:")
    print("   • TronGrid Free: 1,000 запросов/день")
    print("   • TronGrid Pro: $99/месяц за 1M запросов")
    print("   • 100,000 запросов ≈ $10 при Pro плане")
    print()
    
    # Практические примеры
    print("📋 ПРАКТИЧЕСКИЕ ПРИМЕРЫ:")
    print("   • Магазин с 10 платежами/день: 35 дней работы")
    print("   • Сервис с 100 платежами/день: 3.5 дня работы")
    print("   • Платформа с 1000 платежей/день: 0.35 дня работы")
    print()
    
    # Альтернативы
    print("🔄 АЛЬТЕРНАТИВЫ:")
    print("   1. Webhook'и Tron (бесплатно)")
    print("   2. Собственный Tron node")
    print("   3. Увеличение интервала проверки")
    print("   4. Пакетная обработка запросов")
    print("   5. Использование нескольких API ключей")

if __name__ == "__main__":
    analyze_api_usage()






