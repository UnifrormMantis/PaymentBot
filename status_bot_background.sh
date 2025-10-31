#!/bin/bash

echo "📊 СТАТУС БОТА"
echo "=============="

# Проверяем файл PID
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "📝 PID из файла: $BOT_PID"
    
    if ps -p $BOT_PID > /dev/null; then
        echo "✅ Бот запущен и работает"
        echo "🕐 Время запуска: $(ps -o lstart= -p $BOT_PID)"
        echo "💾 Использование памяти: $(ps -o rss= -p $BOT_PID) KB"
    else
        echo "❌ Бот не запущен (PID неактивен)"
    fi
else
    echo "ℹ️  Файл bot.pid не найден"
fi

# Проверяем процессы
echo ""
echo "🔍 Поиск процессов бота:"
BOT_PROCESSES=$(ps aux | grep -E "(private_bot|main\.py)" | grep -v grep)
if [ -n "$BOT_PROCESSES" ]; then
    echo "$BOT_PROCESSES"
else
    echo "❌ Процессы бота не найдены"
fi

# Проверяем логи
echo ""
echo "📋 Последние записи в логах:"
if [ -f "bot.log" ]; then
    echo "--- Последние 10 строк ---"
    tail -10 bot.log
else
    echo "❌ Файл логов не найден"
fi



