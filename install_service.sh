#!/bin/bash

echo "🔧 УСТАНОВКА СИСТЕМНОГО СЕРВИСА"
echo "================================"

# Останавливаем текущий бот
echo "🛑 Остановка текущего бота..."
./stop_bot_background.sh

# Создаем директорию для LaunchAgents
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

# Копируем plist файл
echo "📁 Копирование конфигурации сервиса..."
cp com.paymentbot.plist "$LAUNCH_AGENTS_DIR/"

# Загружаем переменные окружения в plist
echo "🔧 Настройка переменных окружения..."
if [ -f ".env" ]; then
    # Читаем переменные из .env
    while IFS= read -r line; do
        # Пропускаем комментарии и пустые строки
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
            key=$(echo "$line" | cut -d'=' -f1)
            value=$(echo "$line" | cut -d'=' -f2-)
            
            # Добавляем переменную в plist (упрощенная версия)
            echo "   $key = $value"
        fi
    done < .env
fi

# Загружаем сервис
echo "🚀 Загрузка сервиса..."
launchctl load "$LAUNCH_AGENTS_DIR/com.paymentbot.plist"

# Запускаем сервис
echo "▶️  Запуск сервиса..."
launchctl start com.paymentbot

# Проверяем статус
echo "📊 Проверка статуса..."
sleep 2
launchctl list | grep com.paymentbot

echo ""
echo "✅ СЕРВИС УСТАНОВЛЕН!"
echo "====================="
echo "📊 Статус: launchctl list | grep com.paymentbot"
echo "🛑 Остановка: launchctl stop com.paymentbot"
echo "▶️  Запуск: launchctl start com.paymentbot"
echo "🗑️  Удаление: launchctl unload ~/Library/LaunchAgents/com.paymentbot.plist"
echo "📋 Логи: tail -f ~/Library/Logs/com.paymentbot.log"



