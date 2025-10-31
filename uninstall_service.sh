#!/bin/bash

echo "🗑️  УДАЛЕНИЕ СИСТЕМНОГО СЕРВИСА"
echo "==============================="

# Останавливаем сервис
echo "🛑 Остановка сервиса..."
launchctl stop com.paymentbot 2>/dev/null

# Выгружаем сервис
echo "📤 Выгрузка сервиса..."
launchctl unload "$HOME/Library/LaunchAgents/com.paymentbot.plist" 2>/dev/null

# Удаляем plist файл
echo "🗑️  Удаление конфигурации..."
rm -f "$HOME/Library/LaunchAgents/com.paymentbot.plist"

# Очищаем логи
echo "🧹 Очистка логов..."
rm -f "$HOME/Library/Logs/com.paymentbot.log"

echo "✅ СЕРВИС УДАЛЕН!"
echo "================="
echo "Бот больше не будет запускаться автоматически"



