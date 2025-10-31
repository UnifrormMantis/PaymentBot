#!/bin/bash

echo "🛑 Остановка Payment Verification API..."
echo "======================================="

# Останавливаем API сервер
if [ -f "payment_api.pid" ]; then
    API_PID=$(cat payment_api.pid)
    echo "🛑 Останавливаем API сервер (PID: $API_PID)..."
    kill $API_PID 2>/dev/null
    sleep 2
    if ps -p $API_PID > /dev/null; then
        kill -9 $API_PID 2>/dev/null
    fi
    rm -f payment_api.pid
    echo "✅ API сервер остановлен"
else
    echo "ℹ️  Файл payment_api.pid не найден"
fi

# Дополнительная очистка
echo "🧹 Дополнительная очистка..."
pkill -f "payment_verification_api.py" 2>/dev/null
echo "✅ Очистка завершена"


