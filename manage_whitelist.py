#!/usr/bin/env python3
"""
Скрипт для управления whitelist приватного бота
Позволяет добавлять/удалять пользователей из списка разрешенных
"""

import sqlite3
import sys
from database import Database

class WhitelistManager:
    def __init__(self):
        self.db = Database()
    
    def add_user(self, user_id: int, username: str = None):
        """Добавление пользователя в whitelist"""
        try:
            # Добавляем пользователя в базу данных
            self.db.add_user(user_id, username, "")
            
            print(f"✅ Пользователь {user_id} добавлен в whitelist")
            if username:
                print(f"   Username: @{username}")
            
            return True
        except Exception as e:
            print(f"❌ Ошибка добавления пользователя {user_id}: {e}")
            return False
    
    def remove_user(self, user_id: int):
        """Удаление пользователя из whitelist"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Удаляем пользователя из базы данных
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM pending_payments WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM confirmed_payments WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Пользователь {user_id} удален из whitelist")
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления пользователя {user_id}: {e}")
            return False
    
    def list_users(self):
        """Список пользователей в whitelist"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, wallet_address, auto_mode, created_at
                FROM users 
                ORDER BY created_at DESC
            ''')
            users = cursor.fetchall()
            conn.close()
            
            if not users:
                print("📭 Whitelist пуст")
                return
            
            print(f"👥 Пользователи в whitelist ({len(users)}):")
            print("=" * 80)
            
            for i, (user_id, username, wallet, auto_mode, created_at) in enumerate(users, 1):
                print(f"{i:2d}. ID: {user_id}")
                print(f"    Username: @{username if username else 'N/A'}")
                print(f"    Wallet: {wallet if wallet else 'N/A'}")
                print(f"    Auto mode: {'✅' if auto_mode else '❌'}")
                print(f"    Added: {created_at}")
                print("-" * 40)
            
        except Exception as e:
            print(f"❌ Ошибка получения списка пользователей: {e}")
    
    def get_user_info(self, user_id: int):
        """Информация о конкретном пользователе"""
        try:
            user_data = self.db.get_user(user_id)
            
            if not user_data:
                print(f"❌ Пользователь {user_id} не найден в whitelist")
                return
            
            print(f"👤 Информация о пользователе {user_id}:")
            print("=" * 50)
            print(f"Username: @{user_data.get('username', 'N/A')}")
            print(f"Wallet: {user_data.get('wallet_address', 'N/A')}")
            print(f"Auto mode: {'✅ Включен' if user_data.get('auto_mode') else '❌ Выключен'}")
            print(f"Created: {user_data.get('created_at', 'N/A')}")
            
            # Статистика платежей
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM pending_payments WHERE user_id = ?', (user_id,))
            pending_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM confirmed_payments WHERE user_id = ?', (user_id,))
            confirmed_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"Pending payments: {pending_count}")
            print(f"Confirmed payments: {confirmed_count}")
            
        except Exception as e:
            print(f"❌ Ошибка получения информации о пользователе: {e}")
    
    def clear_whitelist(self):
        """Очистка всего whitelist"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Удаляем всех пользователей
            cursor.execute('DELETE FROM users')
            cursor.execute('DELETE FROM pending_payments')
            cursor.execute('DELETE FROM confirmed_payments')
            
            conn.commit()
            conn.close()
            
            print("✅ Whitelist очищен")
            return True
        except Exception as e:
            print(f"❌ Ошибка очистки whitelist: {e}")
            return False

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("🔒 Управление whitelist приватного бота")
        print("=" * 50)
        print()
        print("Использование:")
        print("  python manage_whitelist.py add <user_id> [username]  - Добавить пользователя")
        print("  python manage_whitelist.py remove <user_id>          - Удалить пользователя")
        print("  python manage_whitelist.py list                       - Список пользователей")
        print("  python manage_whitelist.py info <user_id>             - Информация о пользователе")
        print("  python manage_whitelist.py clear                      - Очистить whitelist")
        print()
        print("Примеры:")
        print("  python manage_whitelist.py add 123456789 @username")
        print("  python manage_whitelist.py remove 123456789")
        print("  python manage_whitelist.py list")
        return
    
    manager = WhitelistManager()
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя!")
            print("Пример: python manage_whitelist.py add 123456789 @username")
            return
        
        try:
            user_id = int(sys.argv[2])
            username = sys.argv[3] if len(sys.argv) > 3 else None
            manager.add_user(user_id, username)
        except ValueError:
            print("❌ Неверный формат ID пользователя!")
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя!")
            print("Пример: python manage_whitelist.py remove 123456789")
            return
        
        try:
            user_id = int(sys.argv[2])
            manager.remove_user(user_id)
        except ValueError:
            print("❌ Неверный формат ID пользователя!")
    
    elif command == "list":
        manager.list_users()
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя!")
            print("Пример: python manage_whitelist.py info 123456789")
            return
        
        try:
            user_id = int(sys.argv[2])
            manager.get_user_info(user_id)
        except ValueError:
            print("❌ Неверный формат ID пользователя!")
    
    elif command == "clear":
        confirm = input("⚠️  Вы уверены, что хотите очистить весь whitelist? (yes/no): ")
        if confirm.lower() in ['yes', 'y', 'да', 'д']:
            manager.clear_whitelist()
        else:
            print("❌ Операция отменена")
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Доступные команды: add, remove, list, info, clear")

if __name__ == "__main__":
    main()





