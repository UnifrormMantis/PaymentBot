#!/bin/bash

echo "🛑 Остановка Telegram бота..."

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Используем Python для управления процессами
python -c "
import sys
sys.path.append('.')
from process_manager import ProcessManager

manager = ProcessManager()
processes = manager.find_bot_processes()

if not processes:
    print('ℹ️  Бот не запущен')
    exit(0)

print(f'📋 Найдено {len(processes)} процессов бота:')
manager.print_status()

print('🛑 Останавливаю все процессы...')
stopped = manager.stop_all_bot_processes()

if stopped > 0:
    print('⏳ Жду завершения процессов...')
    if manager.wait_for_processes_to_stop():
        print('✅ Бот успешно остановлен')
    else:
        print('⚠️  Принудительное завершение оставшихся процессов...')
        manager.stop_all_bot_processes(force=True)
        print('✅ Бот принудительно остановлен')
else:
    print('❌ Не удалось остановить процессы бота')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при остановке бота"
    exit 1
fi
