#!/bin/bash

echo "📊 СТАТУС ВСЕХ СЕРВИСОВ ПЛАТЕЖНОЙ СИСТЕМЫ"
echo "=========================================="

echo "🤖 TELEGRAM БОТ:"
echo "----------------"
./status_bot_background.sh

echo ""
echo "🌐 PAYMENT VERIFICATION API:"
echo "----------------------------"
./status_payment_api.sh

echo ""
echo "🔗 ИНТЕГРАЦИЯ:"
echo "-------------"
echo "   • API URL: http://localhost:8002"
echo "   • Документация: http://localhost:8002/docs"
echo "   • Кошелек для приема: TWJ5wQPnJTk2keYXjEgf19i17ZzACBY4Mx"
echo ""
echo "💡 Управление:"
echo "   • Запуск всех: ./start_all_services.sh"
echo "   • Остановка всех: ./stop_all_services.sh"
