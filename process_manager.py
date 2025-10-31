#!/usr/bin/env python3
"""
Модуль для управления процессами Telegram бота
Отслеживает запущенные экземпляры и предотвращает конфликты
"""

import os
import sys
import time
import signal
import psutil
import subprocess
import hashlib
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self, bot_name: str = "telegram_bot"):
        self.bot_name = bot_name
        self.process_patterns = [
            "main.py",
            "minimal_bot.py", 
            "basic_bot.py",
            "simple_bot.py",
            "legacy_bot.py",
            "telegram_bot.py",
            "private_bot.py",
            "auto_payment_bot.py"
        ]
        self.current_bot_file = "private_bot.py"  # Актуальный файл бота
        self.version_file = "bot_version.json"  # Файл с версией
    
    def find_bot_processes(self) -> List[Dict]:
        """Найти все запущенные процессы бота"""
        bot_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # Проверяем, является ли процесс ботом
                    for pattern in self.process_patterns:
                        if pattern in cmdline and 'python' in cmdline.lower():
                            bot_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'create_time': proc.info['create_time'],
                                'pattern': pattern
                            })
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка при поиске процессов: {e}")
            
        return bot_processes
    
    def get_process_info(self, pid: int) -> Optional[Dict]:
        """Получить информацию о процессе по PID"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'cmdline': ' '.join(proc.cmdline()),
                'create_time': proc.create_time(),
                'status': proc.status(),
                'memory_info': proc.memory_info(),
                'cpu_percent': proc.cpu_percent()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def stop_process(self, pid: int, force: bool = False) -> bool:
        """Остановить процесс по PID"""
        try:
            proc = psutil.Process(pid)
            
            if force:
                proc.kill()
                logger.info(f"Процесс {pid} принудительно завершен")
            else:
                proc.terminate()
                logger.info(f"Процесс {pid} получил сигнал завершения")
            
            # Ждем завершения процесса
            try:
                proc.wait(timeout=5)
                logger.info(f"Процесс {pid} успешно завершен")
                return True
            except psutil.TimeoutExpired:
                if not force:
                    logger.warning(f"Процесс {pid} не завершился, принудительное завершение")
                    proc.kill()
                    proc.wait(timeout=2)
                    return True
                return False
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Не удалось завершить процесс {pid}: {e}")
            return False
    
    def stop_all_bot_processes(self, force: bool = False) -> int:
        """Остановить все процессы бота"""
        processes = self.find_bot_processes()
        stopped_count = 0
        
        if not processes:
            print("ℹ️  Процессы бота не найдены")
            return 0
        
        print(f"🛑 Найдено {len(processes)} процессов бота:")
        for proc in processes:
            print(f"   PID: {proc['pid']}, Команда: {proc['cmdline']}")
        
        print(f"\n{'Принудительное' if force else 'Мягкое'} завершение процессов...")
        
        for proc in processes:
            if self.stop_process(proc['pid'], force):
                stopped_count += 1
                time.sleep(0.5)  # Небольшая пауза между завершениями
        
        if stopped_count > 0:
            print(f"✅ Завершено {stopped_count} из {len(processes)} процессов")
            time.sleep(2)  # Ждем полного завершения
        
        return stopped_count
    
    def wait_for_processes_to_stop(self, timeout: int = 10) -> bool:
        """Ждать завершения всех процессов бота"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            processes = self.find_bot_processes()
            if not processes:
                return True
            time.sleep(1)
        
        return False
    
    def check_conflict(self) -> bool:
        """Проверить наличие конфликтующих процессов"""
        processes = self.find_bot_processes()
        return len(processes) > 1
    
    def get_running_count(self) -> int:
        """Получить количество запущенных процессов бота"""
        return len(self.find_bot_processes())
    
    def print_status(self):
        """Вывести статус процессов"""
        processes = self.find_bot_processes()
        
        if not processes:
            print("ℹ️  Процессы бота не запущены")
            return
        
        print(f"📊 Найдено {len(processes)} процессов бота:")
        print("-" * 80)
        
        for i, proc in enumerate(processes, 1):
            try:
                proc_info = self.get_process_info(proc['pid'])
                if proc_info:
                    print(f"{i}. PID: {proc_info['pid']}")
                    print(f"   Команда: {proc_info['cmdline']}")
                    print(f"   Статус: {proc_info['status']}")
                    print(f"   Время запуска: {time.ctime(proc_info['create_time'])}")
                    print(f"   Память: {proc_info['memory_info'].rss / 1024 / 1024:.1f} MB")
                    print()
            except Exception as e:
                print(f"{i}. PID: {proc['pid']} (ошибка получения информации: {e})")
    
    def cleanup_orphaned_processes(self):
        """Очистить зависшие процессы"""
        processes = self.find_bot_processes()
        current_time = time.time()
        orphaned_count = 0
        
        for proc in processes:
            try:
                # Если процесс запущен более 1 часа назад и не отвечает
                if current_time - proc['create_time'] > 3600:
                    proc_info = self.get_process_info(proc['pid'])
                    if proc_info and proc_info['status'] in ['zombie', 'stopped']:
                        print(f"🧹 Очистка зависшего процесса {proc['pid']}")
                        self.stop_process(proc['pid'], force=True)
                        orphaned_count += 1
            except Exception as e:
                logger.error(f"Ошибка при очистке процесса {proc['pid']}: {e}")
        
        if orphaned_count > 0:
            print(f"✅ Очищено {orphaned_count} зависших процессов")
    
    def ensure_single_instance(self) -> bool:
        """Убедиться, что запущен только один экземпляр бота"""
        processes = self.find_bot_processes()
        
        if len(processes) == 0:
            print("ℹ️  Бот не запущен")
            return True
        
        if len(processes) == 1:
            print(f"✅ Запущен один экземпляр бота (PID: {processes[0]['pid']})")
            return True
        
        print(f"⚠️  Обнаружено {len(processes)} экземпляров бота!")
        print("🛑 Останавливаю все экземпляры...")
        
        stopped = self.stop_all_bot_processes()
        
        if stopped > 0:
            print("⏳ Жду завершения процессов...")
            if self.wait_for_processes_to_stop():
                print("✅ Все процессы успешно завершены")
                return True
            else:
                print("⚠️  Некоторые процессы не завершились, принудительное завершение...")
                self.stop_all_bot_processes(force=True)
                return True
        
        return False
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Получить хеш файла для проверки изменений"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"Ошибка получения хеша файла {file_path}: {e}")
            return None
    
    def get_current_version(self) -> Dict:
        """Получить текущую версию бота"""
        version_info = {
            "bot_file": self.current_bot_file,
            "file_hash": self.get_file_hash(self.current_bot_file),
            "timestamp": time.time(),
            "version": "1.1.0"
        }
        
        # Сохраняем версию в файл
        try:
            with open(self.version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения версии: {e}")
        
        return version_info
    
    def check_bot_actuality(self) -> Dict:
        """Проверить актуальность запущенного бота"""
        result = {
            "is_actual": False,
            "current_file": None,
            "expected_file": self.current_bot_file,
            "file_changed": False,
            "processes": [],
            "recommendations": []
        }
        
        processes = self.find_bot_processes()
        result["processes"] = processes
        
        if not processes:
            result["recommendations"].append("Бот не запущен")
            return result
        
        # Проверяем, какой файл запущен
        running_files = set()
        for proc in processes:
            cmdline = proc.get('cmdline', '')
            for pattern in self.process_patterns:
                if pattern in cmdline:
                    running_files.add(pattern)
                    break
        
        result["current_file"] = list(running_files)
        
        # Проверяем, запущен ли актуальный файл
        if self.current_bot_file in running_files:
            result["is_actual"] = True
            
            # Проверяем, изменился ли файл с момента запуска
            current_hash = self.get_file_hash(self.current_bot_file)
            if current_hash:
                # Получаем время запуска самого старого процесса
                oldest_start = min(proc['create_time'] for proc in processes)
                
                # Проверяем, изменился ли файл после запуска
                file_mtime = os.path.getmtime(self.current_bot_file)
                if file_mtime > oldest_start:
                    result["file_changed"] = True
                    result["is_actual"] = False
                    result["recommendations"].append("Файл бота был изменен после запуска")
        else:
            result["recommendations"].append(f"Запущен устаревший файл: {running_files}")
            result["recommendations"].append(f"Ожидается: {self.current_bot_file}")
        
        # Дополнительные проверки
        if len(processes) > 1:
            result["recommendations"].append("Запущено несколько экземпляров бота")
            result["is_actual"] = False
        
        return result
    
    def restart_if_outdated(self, force: bool = False) -> bool:
        """Перезапустить бота если он устарел"""
        actuality = self.check_bot_actuality()
        
        if actuality["is_actual"] and not actuality["file_changed"]:
            print("✅ Бот актуален и работает корректно")
            return True
        
        print("⚠️  Обнаружены проблемы с актуальностью бота:")
        for rec in actuality["recommendations"]:
            print(f"   • {rec}")
        
        if not force:
            print("\n🔄 Для перезапуска запустите: ./start_private_bot.sh")
            return False
        
        print("🛑 Останавливаю устаревшие процессы...")
        stopped = self.stop_all_bot_processes(force=True)
        
        if stopped > 0:
            print("⏳ Жду завершения процессов...")
            if self.wait_for_processes_to_stop():
                print("✅ Процессы остановлены")
                print("🚀 Запустите актуальный бот командой: ./start_private_bot.sh")
                return True
            else:
                print("⚠️  Некоторые процессы не завершились")
                return False
        
        return False
    
    def get_actuality_status(self) -> str:
        """Получить текстовый статус актуальности"""
        actuality = self.check_bot_actuality()
        
        if actuality["is_actual"] and not actuality["file_changed"]:
            return "✅ Актуален"
        elif actuality["file_changed"]:
            return "⚠️  Файл изменен"
        elif actuality["current_file"] and self.current_bot_file not in actuality["current_file"]:
            return "❌ Устарел"
        else:
            return "❓ Неизвестно"
    
    def print_actuality_report(self):
        """Вывести отчет об актуальности"""
        actuality = self.check_bot_actuality()
        
        print("🔍 ПРОВЕРКА АКТУАЛЬНОСТИ БОТА")
        print("=" * 50)
        
        print(f"📁 Ожидаемый файл: {actuality['expected_file']}")
        print(f"🔄 Запущенные файлы: {', '.join(actuality['current_file']) if actuality['current_file'] else 'Нет'}")
        print(f"📊 Количество процессов: {len(actuality['processes'])}")
        print(f"🎯 Статус: {self.get_actuality_status()}")
        
        if actuality["file_changed"]:
            print("⚠️  Файл бота был изменен после запуска!")
        
        if actuality["recommendations"]:
            print("\n💡 Рекомендации:")
            for i, rec in enumerate(actuality["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print("\n📋 Запущенные процессы:")
        if actuality["processes"]:
            for i, proc in enumerate(actuality["processes"], 1):
                print(f"   {i}. PID: {proc['pid']} - {proc['cmdline']}")
        else:
            print("   Процессы не найдены")

def main():
    """Главная функция для тестирования"""
    manager = ProcessManager()
    
    print("🔍 Проверка процессов бота...")
    manager.print_status()
    
    print("\n🛡️  Проверка на конфликты...")
    if manager.check_conflict():
        print("⚠️  Обнаружен конфликт! Останавливаю все процессы...")
        manager.ensure_single_instance()
    else:
        print("✅ Конфликтов не обнаружено")
    
    print("\n" + "="*60)
    manager.print_actuality_report()
    
    print("\n🔄 Проверка необходимости перезапуска...")
    actuality = manager.check_bot_actuality()
    if not actuality["is_actual"] or actuality["file_changed"]:
        print("⚠️  Требуется перезапуск бота!")
        print("💡 Запустите: ./start_private_bot.sh")
    else:
        print("✅ Бот актуален, перезапуск не требуется")

if __name__ == "__main__":
    main()
