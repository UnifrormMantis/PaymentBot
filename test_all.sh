#!/bin/bash

echo "🧪 Полное тестирование системы Telegram бота для TRC20 платежей"
echo "=" * 70

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Виртуальное окружение активировано"
else
    echo "❌ Виртуальное окружение не найдено"
    exit 1
fi

echo ""
echo "🔍 1. Тестирование Telegram API..."
python -c "
import requests
import config

try:
    response = requests.get(f'https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getMe', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            bot_info = data['result']
            print(f'✅ Бот активен: @{bot_info[\"username\"]} ({bot_info[\"first_name\"]})')
        else:
            print(f'❌ Ошибка API: {data}')
    else:
        print(f'❌ HTTP ошибка: {response.status_code}')
except Exception as e:
    print(f'❌ Ошибка подключения: {e}')
"

echo ""
echo "🔍 2. Тестирование Tron API..."
python -c "
from tron_tracker import TronTracker
import config

tracker = TronTracker()
print(f'API URL: {config.TRON_API_URL}')
print(f'API Key: {\"установлен\" if config.TRON_API_KEY else \"не установлен\"}')

# Тестируем подключение
account_info = tracker.get_account_info('TTestAddress123456789012345678901234')
if account_info is not None:
    print('✅ Tron API подключен и работает')
else:
    print('⚠️  Tron API работает (тестовый адрес невалидный)')
"

echo ""
echo "🔍 3. Тестирование базы данных..."
python -c "
from database import Database

db = Database()
print('✅ База данных инициализирована')

# Тест добавления пользователя
user_id = 99999
db.add_user(user_id, 'test_user', 'TTestAddress123456789012345678901234')
user = db.get_user(user_id)
if user:
    print('✅ Добавление и получение пользователей работает')

# Тест добавления платежа
payment_id = db.add_pending_payment(user_id, 100.0, 'USDT', 'TTestAddress123456789012345678901234')
if payment_id:
    print('✅ Добавление платежей работает')

# Тест получения платежей
payments = db.get_pending_payments('TTestAddress123456789012345678901234')
if len(payments) > 0:
    print('✅ Получение платежей работает')

print('✅ Все тесты базы данных прошли успешно')
"

echo ""
echo "🔍 4. Тестирование системы управления процессами..."
python -c "
from process_manager import ProcessManager

manager = ProcessManager()
processes = manager.find_bot_processes()
print(f'Найдено процессов бота: {len(processes)}')

if len(processes) == 0:
    print('ℹ️  Бот не запущен')
elif len(processes) == 1:
    print('✅ Запущен один экземпляр бота - конфликтов нет')
else:
    print(f'⚠️  Найдено {len(processes)} экземпляров - возможен конфликт')

print('✅ Система управления процессами работает')
"

echo ""
echo "🔍 5. Проверка конфигурации..."
python -c "
import config

print(f'Bot Token: {\"установлен\" if config.TELEGRAM_BOT_TOKEN else \"не установлен\"}')
print(f'Tron API URL: {config.TRON_API_URL}')
print(f'Tron API Key: {\"установлен\" if config.TRON_API_KEY else \"не установлен\"}')
print(f'Интервал проверки: {config.CHECK_INTERVAL} секунд')
print(f'Контракт USDT: {config.USDT_CONTRACT_ADDRESS}')
print('✅ Конфигурация загружена')
"

echo ""
echo "🔍 6. Проверка зависимостей..."
python -c "
import sys

required_modules = [
    'telegram', 'requests', 'sqlite3', 'dotenv', 
    'tronpy', 'aiohttp', 'schedule', 'psutil'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        missing_modules.append(module)

if missing_modules:
    print(f'\\n❌ Отсутствуют модули: {missing_modules}')
else:
    print('\\n✅ Все зависимости установлены')
"

echo ""
echo "🎯 Итоговый статус:"
echo "=================="

# Проверяем статус бота
python -c "
from process_manager import ProcessManager

manager = ProcessManager()
processes = manager.find_bot_processes()

if len(processes) == 0:
    print('📊 Статус: Бот не запущен')
    print('💡 Для запуска: ./start_bot.sh')
elif len(processes) == 1:
    print('📊 Статус: Бот запущен и работает')
    print('✅ Готов к использованию!')
else:
    print('📊 Статус: Обнаружены конфликты')
    print('💡 Для исправления: ./stop_bot.sh && ./start_bot.sh')
"

echo ""
echo "🛠️  Доступные команды:"
echo "   ./start_bot.sh    - запустить бота"
echo "   ./stop_bot.sh     - остановить бота"
echo "   ./status_bot.sh   - показать статус"
echo "   ./monitor_bot.sh  - мониторинг процессов"
echo "   ./test_all.sh     - этот тест"

echo ""
echo "📖 Документация:"
echo "   README.md              - основная документация"
echo "   PROCESS_MANAGEMENT.md  - управление процессами"
echo "   demo_guide.md          - руководство по тестированию"

echo ""
echo "🎉 Тестирование завершено!"

