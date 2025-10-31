#!/bin/bash

echo "🚀 Запуск бота с API сервером..."
echo "================================="

# Останавливаем существующие процессы
echo "🛑 Остановка существующих процессов..."
pkill -f "private_bot.py" 2>/dev/null
pkill -f "simple_payment_api.py" 2>/dev/null
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
echo "🌐 Запуск API сервера..."
nohup python simple_payment_api.py > api.log 2>&1 &
API_PID=$!
echo "✅ API сервер запущен с PID: $API_PID"
echo $API_PID > api.pid

# Ждем запуска API
echo "⏳ Ожидание запуска API сервера..."
sleep 3

# Проверяем API
if curl -s http://localhost:8001/get-api-key > /dev/null; then
    echo "✅ API сервер работает"
else
    echo "❌ Ошибка запуска API сервера"
    exit 1
fi

# Запускаем бота в фоне
echo "🤖 Запуск бота..."
nohup python private_bot.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Бот запущен с PID: $BOT_PID"
echo $BOT_PID > bot.pid

# Проверяем, что бот запустился
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Бот успешно запущен и работает!"
    echo ""
    echo "📊 Управление:"
    echo "   Статус: ./status_bot_with_api.sh"
    echo "   Остановка: ./stop_bot_with_api.sh"
    echo "   Логи бота: tail -f bot.log"
    echo "   Логи API: tail -f api.log"
    echo ""
    echo "🌐 API доступен по адресу: http://localhost:8001"
else
    echo "❌ Ошибка запуска бота. Проверьте логи: cat bot.log"
    exit 1
fi



