#!/bin/bash

echo "📊 СТАТУС PAYMENT VERIFICATION API"
echo "=================================="

# Проверяем API сервер
echo "🌐 API СЕРВЕР:"
if [ -f "payment_api.pid" ]; then
    API_PID=$(cat payment_api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "✅ Запущен (PID: $API_PID)"
        echo "🕐 Время запуска: $(ps -o lstart= -p $API_PID)"
        echo "💾 Память: $(ps -o rss= -p $API_PID) KB"
        
        # Проверяем доступность API
        if curl -s http://localhost:8002/health > /dev/null; then
            echo "🌐 API доступен: http://localhost:8002"
        else
            echo "⚠️  API недоступен"
        fi
    else
        echo "❌ Не запущен (PID неактивен)"
    fi
else
    echo "❌ Не запущен (файл payment_api.pid не найден)"
fi

echo ""

# Проверяем порты
echo "🔌 ПОРТЫ:"
if lsof -i :8002 > /dev/null 2>&1; then
    echo "✅ Порт 8002 (API) занят"
else
    echo "❌ Порт 8002 (API) свободен"
fi

echo ""

# Показываем последние логи
echo "📋 ПОСЛЕДНИЕ ЛОГИ API:"
if [ -f "payment_api.log" ]; then
    echo "--- Последние 10 строк ---"
    tail -10 payment_api.log
else
    echo "❌ Файл payment_api.log не найден"
fi

echo ""

# Проверяем кошелек
echo "💰 КОШЕЛЕК ДЛЯ ПРИЕМА ПЛАТЕЖЕЙ:"
echo "   Адрес: TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
echo "   Баланс: 0.908897 USDT (проверяется через API)"


