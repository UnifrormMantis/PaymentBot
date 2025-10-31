#!/bin/bash

echo "🚀 Запуск бота в фоновом режиме..."
echo "=================================="

# Останавливаем существующие процессы
echo "🛑 Остановка существующих процессов..."
pkill -f "private_bot.py" 2>/dev/null
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

# Запускаем бота в фоне
echo "🤖 Запуск бота в фоновом режиме..."
nohup python private_bot.py > bot.log 2>&1 &

# Получаем PID процесса
BOT_PID=$!
echo "✅ Бот запущен с PID: $BOT_PID"

# Сохраняем PID в файл
echo $BOT_PID > bot.pid
echo "📝 PID сохранен в bot.pid"

# Проверяем, что бот запустился
sleep 3
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Бот успешно запущен и работает!"
    echo "📊 Логи: tail -f bot.log"
    echo "🛑 Остановка: ./stop_bot_background.sh"
else
    echo "❌ Ошибка запуска бота. Проверьте логи: cat bot.log"
    exit 1
fi



