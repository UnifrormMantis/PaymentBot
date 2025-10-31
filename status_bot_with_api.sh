#!/bin/bash

echo "📊 СТАТУС БОТА И API СЕРВЕРА"
echo "============================"

# Проверяем бота
echo "🤖 БОТ:"
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    if ps -p $BOT_PID > /dev/null; then
        echo "✅ Запущен (PID: $BOT_PID)"
        echo "🕐 Время запуска: $(ps -o lstart= -p $BOT_PID)"
        echo "💾 Память: $(ps -o rss= -p $BOT_PID) KB"
    else
        echo "❌ Не запущен (PID неактивен)"
    fi
else
    echo "❌ Не запущен (файл bot.pid не найден)"
fi

echo ""

# Проверяем API сервер
echo "🌐 API СЕРВЕР:"
if [ -f "api.pid" ]; then
    API_PID=$(cat api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "✅ Запущен (PID: $API_PID)"
        echo "🕐 Время запуска: $(ps -o lstart= -p $API_PID)"
        echo "💾 Память: $(ps -o rss= -p $API_PID) KB"
        
        # Проверяем доступность API
        if curl -s http://localhost:8001/get-api-key > /dev/null; then
            echo "🌐 API доступен: http://localhost:8001"
        else
            echo "⚠️  API недоступен"
        fi
    else
        echo "❌ Не запущен (PID неактивен)"
    fi
else
    echo "❌ Не запущен (файл api.pid не найден)"
fi

echo ""

# Проверяем порты
echo "🔌 ПОРТЫ:"
if lsof -i :8001 > /dev/null 2>&1; then
    echo "✅ Порт 8001 (API) занят"
else
    echo "❌ Порт 8001 (API) свободен"
fi

echo ""

# Показываем последние логи
echo "📋 ПОСЛЕДНИЕ ЛОГИ БОТА:"
if [ -f "bot.log" ]; then
    echo "--- Последние 5 строк ---"
    tail -5 bot.log
else
    echo "❌ Файл bot.log не найден"
fi

echo ""

echo "📋 ПОСЛЕДНИЕ ЛОГИ API:"
if [ -f "api.log" ]; then
    echo "--- Последние 5 строк ---"
    tail -5 api.log
else
    echo "❌ Файл api.log не найден"
fi



