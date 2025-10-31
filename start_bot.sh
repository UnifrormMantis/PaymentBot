#!/bin/bash

echo "🤖 Запуск Telegram бота для отслеживания TRC20 платежей..."

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    echo "🔧 Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "❌ Виртуальное окружение не найдено. Запустите install.sh сначала."
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден. Создайте его на основе env_example.txt"
    exit 1
fi

# Проверяем наличие Bot Token
if ! grep -q "TELEGRAM_BOT_TOKEN=your_bot_token_here" .env; then
    if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "TELEGRAM_BOT_TOKEN=$" .env; then
        echo "❌ TELEGRAM_BOT_TOKEN не настроен в файле .env"
        exit 1
    fi
else
    echo "❌ Не забудьте настроить TELEGRAM_BOT_TOKEN в файле .env"
    exit 1
fi

# Проверяем и управляем процессами бота
echo "🔍 Проверка запущенных процессов бота..."
python -c "
import sys
sys.path.append('.')
from process_manager import ProcessManager

manager = ProcessManager()
processes = manager.find_bot_processes()

if len(processes) > 0:
    print(f'⚠️  Найдено {len(processes)} запущенных процессов бота:')
    for proc in processes:
        print(f'   PID: {proc[\"pid\"]}, Команда: {proc[\"cmdline\"]}')
    
    print('🛑 Останавливаю все процессы...')
    stopped = manager.stop_all_bot_processes()
    
    if stopped > 0:
        print('⏳ Жду завершения процессов...')
        if manager.wait_for_processes_to_stop():
            print('✅ Все процессы успешно завершены')
        else:
            print('⚠️  Принудительное завершение оставшихся процессов...')
            manager.stop_all_bot_processes(force=True)
    else:
        print('❌ Не удалось остановить процессы')
        exit(1)
else:
    print('✅ Процессы бота не найдены')
"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при управлении процессами"
    exit 1
fi

echo "🚀 Запуск бота..."
python main.py
