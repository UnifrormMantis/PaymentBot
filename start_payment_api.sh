#!/bin/bash

echo "🚀 Запуск Payment Verification API..."
echo "====================================="

# Останавливаем существующие процессы
echo "🛑 Остановка существующих процессов..."
pkill -f "payment_verification_api.py" 2>/dev/null
sleep 2

# Активируем виртуальное окружение
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "❌ Ошибка: Виртуальное окружение не найдено"
    exit 1
fi

# Загружаем переменные окружения
if [ -f ".env" ]; then
    echo "📁 Загрузка переменных из .env..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Запускаем API сервер в фоне
echo "🌐 Запуск Payment Verification API..."
nohup python payment_verification_api.py > payment_api.log 2>&1 &
API_PID=$!
echo "✅ API сервер запущен с PID: $API_PID"
echo $API_PID > payment_api.pid

# Ждем запуска API
echo "⏳ Ожидание запуска API сервера..."
sleep 3

# Проверяем API
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ API сервер работает"
    echo ""
    echo "📊 Информация:"
    echo "   API доступен: http://localhost:8002"
    echo "   Документация: http://localhost:8002/docs"
    echo "   Получить ключ: curl http://localhost:8002/get-api-key"
    echo ""
    echo "📊 Управление:"
    echo "   Статус: ./status_payment_api.sh"
    echo "   Остановка: ./stop_payment_api.sh"
    echo "   Логи: tail -f payment_api.log"
    echo ""
    echo "🔑 Получение API ключа:"
    echo "   curl http://localhost:8002/get-api-key"
else
    echo "❌ Ошибка запуска API сервера"
    echo "📋 Проверьте логи: cat payment_api.log"
    exit 1
fi


