#!/bin/bash

echo "🚀 ЗАПУСК ВСЕХ СЕРВИСОВ ПЛАТЕЖНОЙ СИСТЕМЫ"
echo "=========================================="

# Запускаем бота
echo "🤖 Запуск Telegram бота..."
./start_bot_background.sh

echo ""

# Запускаем API
echo "🌐 Запуск Payment Verification API..."
./start_payment_api.sh

echo ""
echo "✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================="
echo ""
echo "📊 Управление:"
echo "   • Статус всех сервисов: ./status_all_services.sh"
echo "   • Остановка всех сервисов: ./stop_all_services.sh"
echo "   • Логи бота: tail -f bot.log"
echo "   • Логи API: tail -f payment_api.log"
echo ""
echo "🔑 API данные:"
echo "   • URL: http://localhost:8002"
echo "   • Документация: http://localhost:8002/docs"
echo "   • Получить ключ: curl http://localhost:8002/get-api-key"
echo ""
echo "💳 Кошелек для приема: TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
