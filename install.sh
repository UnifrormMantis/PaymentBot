#!/bin/bash

echo "🚀 Установка Telegram бота для отслеживания TRC20 платежей..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

# Проверяем версию Python
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Требуется Python 3.8 или выше. Текущая версия: $python_version"
    exit 1
fi

echo "✅ Python $python_version найден"

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создание файла .env..."
    cp env_example.txt .env
    echo "⚠️  Не забудьте отредактировать файл .env и добавить ваш Telegram Bot Token!"
fi

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env и добавьте ваш Telegram Bot Token"
echo "2. (Опционально) Получите Tron API ключ на https://www.trongrid.io/"
echo "3. Запустите бота: python main.py"
echo ""
echo "📖 Подробная документация в файле README.md"

