#!/bin/bash

# Скрипт запуска Simple Payment API

echo "🚀 Запуск Simple Payment API..."
echo "================================"

# Проверяем, что мы в правильной директории
if [ ! -f "simple_payment_api.py" ]; then
    echo "❌ Ошибка: simple_payment_api.py не найден!"
    echo "Запустите скрипт из директории с файлами бота"
    exit 1
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем, что виртуальное окружение активировано
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Ошибка: Не удалось активировать виртуальное окружение!"
    exit 1
fi

echo "✅ Виртуальное окружение активировано"

# Проверяем зависимости
echo "🔍 Проверка зависимостей..."
python -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Установка зависимостей..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей!"
        exit 1
    fi
fi

echo "✅ Зависимости установлены"

# Останавливаем существующие процессы Simple API
echo "🔍 Проверка запущенных процессов Simple API..."
API_PID=$(pgrep -f "simple_payment_api.py")
if [ ! -z "$API_PID" ]; then
    echo "🛑 Остановка существующего Simple API процесса (PID: $API_PID)..."
    kill $API_PID
    sleep 2
fi

# Запускаем Simple API сервер
echo "🚀 Запуск Simple Payment API..."
echo "================================"
echo "📡 API будет доступен по адресу: http://localhost:8001"
echo "📚 Документация: http://localhost:8001/docs"
echo "🔍 Проверка здоровья: http://localhost:8001/health"
echo "================================"
echo ""
echo "💡 ПРОСТАЯ ИНТЕГРАЦИЯ:"
echo "   1. Получите API ключ: GET http://localhost:8001/get-api-key"
echo "   2. Создайте платеж: POST http://localhost:8001/create-payment"
echo "   3. Проверьте статус: GET http://localhost:8001/check-payment/{id}"
echo ""
echo "🔑 Заголовок для всех запросов: X-API-Key: your_api_key"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Запускаем API
python simple_payment_api.py
