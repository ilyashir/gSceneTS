#!/usr/bin/env python3
"""
Скрипт для обновления версии проекта во всех необходимых файлах.
Использует bump2version для обновления версии в __init__.py, а затем
запускает update_version.py для синхронизации версии в остальных файлах.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, check=True):
    """Запускает команду и возвращает результат"""
    print(f"Выполняется: {' '.join(command)}")
    result = subprocess.run(command, check=check)
    return result.returncode == 0

def update_version(part):
    """
    Обновляет версию проекта
    
    Args:
        part: Часть версии для обновления ('major', 'minor', 'patch')
    """
    # Проверяем, установлен ли bump2version
    try:
        subprocess.run(['bump2version', '--version'], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("bump2version не установлен. Устанавливаем...")
        if not run_command(['pip', 'install', 'bump2version']):
            print("Ошибка установки bump2version", file=sys.stderr)
            return False
    
    # Путь к директории скриптов
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Запускаем bump2version для обновления версии в __init__.py
    if not run_command(['bump2version', '--allow-dirty', part]):
        print(f"Ошибка при выполнении bump2version {part}", file=sys.stderr)
        return False
    
    # Запускаем update_version.py для синхронизации версии в остальных файлах
    update_script = script_dir / 'update_version.py'
    if not run_command(['python', str(update_script)]):
        print("Ошибка при синхронизации версии в других файлах", file=sys.stderr)
        return False
    
    print("Версия успешно обновлена!")
    return True

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Обновляет версию проекта во всех файлах")
    parser.add_argument('part', choices=['major', 'minor', 'patch'], 
                        help='Часть версии для обновления')
    
    args = parser.parse_args()
    
    if update_version(args.part):
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main()) 