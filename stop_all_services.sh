#!/bin/bash

echo "🛑 ОСТАНОВКА ВСЕХ СЕРВИСОВ ПЛАТЕЖНОЙ СИСТЕМЫ"
echo "============================================="

# Останавливаем бота
echo "🤖 Остановка Telegram бота..."
./stop_bot_background.sh

echo ""

# Останавливаем API
echo "🌐 Остановка Payment Verification API..."
./stop_payment_api.sh

echo ""
echo "✅ ВСЕ СЕРВИСЫ ОСТАНОВЛЕНЫ!"
echo "============================"
