#!/bin/bash

echo "📊 Статус Telegram бота..."

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Проверяем статус
python -c "
import sys
sys.path.append('.')
from process_manager import ProcessManager

manager = ProcessManager()

print('🔍 Проверка статуса процессов бота...')
print('=' * 60)

processes = manager.find_bot_processes()

if not processes:
    print('ℹ️  Бот не запущен')
    print('💡 Для запуска используйте: ./start_bot.sh')
else:
    print(f'📊 Найдено {len(processes)} процессов бота:')
    print()
    
    for i, proc in enumerate(processes, 1):
        try:
            proc_info = manager.get_process_info(proc['pid'])
            if proc_info:
                print(f'{i}. PID: {proc_info[\"pid\"]}')
                print(f'   Команда: {proc_info[\"cmdline\"]}')
                print(f'   Статус: {proc_info[\"status\"]}')
                print(f'   Время запуска: {proc_info[\"create_time\"]}')
                print(f'   Память: {proc_info[\"memory_info\"].rss / 1024 / 1024:.1f} MB')
                print(f'   CPU: {proc_info[\"cpu_percent\"]:.1f}%')
                print()
        except Exception as e:
            print(f'{i}. PID: {proc[\"pid\"]} (ошибка: {e})')
    
    # Проверяем на конфликты
    if len(processes) > 1:
        print('⚠️  ВНИМАНИЕ: Обнаружено несколько экземпляров бота!')
        print('🛑 Это может вызвать ошибку \"Conflict: terminated by other getUpdates request\"')
        print('💡 Рекомендуется остановить все процессы и запустить заново:')
        print('   ./stop_bot.sh && ./start_bot.sh')
    else:
        print('✅ Запущен один экземпляр бота - конфликтов нет')

print()
print('🛠️  Доступные команды:')
print('   ./start_bot.sh  - запустить бота')
print('   ./stop_bot.sh   - остановить бота')
print('   ./monitor_bot.sh - мониторинг процессов')
print('   ./status_bot.sh - показать этот статус')
"

