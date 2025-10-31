#!/bin/bash

echo "🛑 Остановка бота и API сервера..."
echo "=================================="

# Останавливаем бота
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "🛑 Останавливаем бот (PID: $BOT_PID)..."
    kill $BOT_PID 2>/dev/null
    sleep 2
    if ps -p $BOT_PID > /dev/null; then
        kill -9 $BOT_PID 2>/dev/null
    fi
    rm -f bot.pid
    echo "✅ Бот остановлен"
else
    echo "ℹ️  Файл bot.pid не найден"
fi

# Останавливаем API сервер
if [ -f "api.pid" ]; then
    API_PID=$(cat api.pid)
    echo "🛑 Останавливаем API сервер (PID: $API_PID)..."
    kill $API_PID 2>/dev/null
    sleep 2
    if ps -p $API_PID > /dev/null; then
        kill -9 $API_PID 2>/dev/null
    fi
    rm -f api.pid
    echo "✅ API сервер остановлен"
else
    echo "ℹ️  Файл api.pid не найден"
fi

# Дополнительная очистка
echo "🧹 Дополнительная очистка..."
pkill -f "private_bot.py" 2>/dev/null
pkill -f "simple_payment_api.py" 2>/dev/null
echo "✅ Очистка завершена"



