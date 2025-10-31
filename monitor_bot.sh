#!/bin/bash

echo "📊 Мониторинг процессов Telegram бота..."

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запускаем мониторинг
python -c "
import sys
import time
sys.path.append('.')
from process_manager import ProcessManager

manager = ProcessManager()

def monitor_loop():
    print('🔍 Запуск мониторинга процессов бота...')
    print('Нажмите Ctrl+C для выхода')
    print('=' * 60)
    
    while True:
        try:
            processes = manager.find_bot_processes()
            actuality = manager.check_bot_actuality()
            
            status = manager.get_actuality_status()
            print(f'\\r📊 {time.strftime(\"%H:%M:%S\")} - Процессов: {len(processes)} | Статус: {status}', end='', flush=True)
            
            # Проверка конфликтов
            if len(processes) > 1:
                print('\\n⚠️  ОБНАРУЖЕН КОНФЛИКТ! Несколько экземпляров бота запущено!')
                print('🛑 Автоматическая остановка всех процессов...')
                
                stopped = manager.stop_all_bot_processes()
                if stopped > 0:
                    print(f'✅ Остановлено {stopped} процессов')
                    if manager.wait_for_processes_to_stop():
                        print('✅ Все процессы успешно завершены')
                    else:
                        print('⚠️  Принудительное завершение...')
                        manager.stop_all_bot_processes(force=True)
                else:
                    print('❌ Не удалось остановить процессы')
            
            # Проверка актуальности
            elif not actuality['is_actual'] or actuality['file_changed']:
                print('\\n⚠️  ОБНАРУЖЕНА ПРОБЛЕМА АКТУАЛЬНОСТИ!')
                for rec in actuality['recommendations']:
                    print(f'   • {rec}')
                print('🛑 Автоматическая остановка устаревших процессов...')
                
                stopped = manager.stop_all_bot_processes(force=True)
                if stopped > 0:
                    print(f'✅ Остановлено {stopped} процессов')
                    print('💡 Запустите актуальный бот: ./start_private_bot.sh')
                else:
                    print('❌ Не удалось остановить процессы')
            
            time.sleep(5)  # Проверяем каждые 5 секунд
            
        except KeyboardInterrupt:
            print('\\n🛑 Мониторинг остановлен пользователем')
            break
        except Exception as e:
            print(f'\\n❌ Ошибка мониторинга: {e}')
            time.sleep(10)

if __name__ == '__main__':
    monitor_loop()
"

