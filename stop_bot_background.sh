#!/bin/bash

echo "🛑 Остановка бота..."
echo "==================="

# Читаем PID из файла
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    echo "📝 Найден PID: $BOT_PID"
    
    # Проверяем, что процесс существует
    if ps -p $BOT_PID > /dev/null; then
        echo "🛑 Останавливаем процесс $BOT_PID..."
        kill $BOT_PID
        
        # Ждем завершения
        sleep 3
        
        # Проверяем, что процесс остановлен
        if ps -p $BOT_PID > /dev/null; then
            echo "⚠️  Принудительная остановка..."
            kill -9 $BOT_PID
        fi
        
        echo "✅ Бот остановлен"
    else
        echo "ℹ️  Процесс уже не запущен"
    fi
    
    # Удаляем файл PID
    rm -f bot.pid
else
    echo "ℹ️  Файл bot.pid не найден"
fi

# Дополнительная очистка
echo "🧹 Дополнительная очистка..."
pkill -f "private_bot.py" 2>/dev/null
echo "✅ Очистка завершена"



