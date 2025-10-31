#!/bin/bash

# Скрипт запуска Payment Bot API

echo "🚀 Запуск Payment Bot API..."
echo "================================"

# Проверяем, что мы в правильной директории
if [ ! -f "payment_api.py" ]; then
    echo "❌ Ошибка: payment_api.py не найден!"
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

# Проверяем конфигурацию
echo "🔧 Проверка конфигурации..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  Предупреждение: TELEGRAM_BOT_TOKEN не установлен"
    echo "   API будет работать, но некоторые функции могут быть недоступны"
fi

if [ -z "$TRON_API_KEY" ]; then
    echo "⚠️  Предупреждение: TRON_API_KEY не установлен"
    echo "   API будет работать, но проверка платежей будет недоступна"
fi

# Останавливаем существующие процессы API
echo "🔍 Проверка запущенных процессов API..."
API_PID=$(pgrep -f "payment_api.py")
if [ ! -z "$API_PID" ]; then
    echo "🛑 Остановка существующего API процесса (PID: $API_PID)..."
    kill $API_PID
    sleep 2
fi

# Запускаем API сервер
echo "🚀 Запуск Payment Bot API..."
echo "================================"
echo "📡 API будет доступен по адресу: http://localhost:8000"
echo "📚 Документация: http://localhost:8000/docs"
echo "🔍 Проверка здоровья: http://localhost:8000/health"
echo "================================"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Запускаем API
python payment_api.py





