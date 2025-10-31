#!/bin/bash

# Скрипт запуска приватного Payment Bot

echo "🔒 Запуск приватного Telegram бота для отслеживания TRC20 платежей..."
echo "=================================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "private_bot.py" ]; then
    echo "❌ Ошибка: private_bot.py не найден!"
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
python -c "import telegram, requests, tronpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Установка зависимостей..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей!"
        exit 1
    fi
fi

echo "✅ Зависимости установлены"

# Загружаем переменные окружения из .env
echo "🔧 Загрузка конфигурации..."
if [ -f ".env" ]; then
    echo "📁 Загружаем переменные из .env..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
    echo "✅ Переменные окружения загружены"
else
    echo "⚠️  Файл .env не найден"
fi

# Проверяем конфигурацию
echo "🔧 Проверка конфигурации..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен!"
    echo "Установите переменную окружения:"
    echo "export TELEGRAM_BOT_TOKEN=\"your_bot_token\""
    echo "Или создайте файл .env с токеном"
    exit 1
fi

if [ -z "$TRON_API_KEY" ]; then
    echo "⚠️  Предупреждение: TRON_API_KEY не установлен"
    echo "   Бот будет работать, но проверка платежей будет недоступна"
fi

# Проверяем актуальность запущенных процессов
echo "🔍 Проверка актуальности запущенных процессов..."
python -c "
from process_manager import ProcessManager
manager = ProcessManager()
actuality = manager.check_bot_actuality()

if not actuality['is_actual'] or actuality['file_changed']:
    print('⚠️  Обнаружены проблемы с актуальностью:')
    for rec in actuality['recommendations']:
        print(f'   • {rec}')
    
    if actuality['processes']:
        print('🛑 Останавливаю устаревшие процессы...')
        stopped = manager.stop_all_bot_processes(force=True)
        if stopped > 0:
            print(f'✅ Остановлено {stopped} процессов')
        else:
            print('❌ Не удалось остановить процессы')
    else:
        print('ℹ️  Процессы не найдены')
else:
    print('✅ Все процессы актуальны')
"

# Дополнительная проверка через ProcessManager
echo "🔧 Использование ProcessManager для управления процессами..."
python -c "
from process_manager import ProcessManager
manager = ProcessManager()
manager.ensure_single_instance()
"

# Проверяем whitelist
echo "👥 Проверка whitelist..."
python -c "
from manage_whitelist import WhitelistManager
manager = WhitelistManager()
conn = manager.db.get_connection()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
conn.close()
print(f'Пользователей в whitelist: {count}')
if count == 0:
    print('⚠️  Whitelist пуст! Добавьте пользователей командой:')
    print('   python manage_whitelist.py add <user_id> [username]')
"

# Запускаем приватный бот
echo "🚀 Запуск приватного Payment Bot..."
echo "=================================================================="
echo "🔒 Режим: ПРИВАТНЫЙ (только для авторизованных пользователей)"
echo "⏰ Интервал проверки: 30 секунд"
echo "🤖 Автоматическое зачисление: ВКЛЮЧЕНО"
echo "=================================================================="
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Запускаем бот
python private_bot.py
