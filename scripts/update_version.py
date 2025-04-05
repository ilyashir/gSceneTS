#!/usr/bin/env python3
"""
Скрипт для обновления версии проекта в различных файлах.
Считывает версию из __init__.py и обновляет её в pyproject.toml.
"""

import re
import os
import sys

def get_version_from_init():
    """Получает версию из __init__.py"""
    init_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        return version_match.group(1)
    else:
        raise RuntimeError("Не удалось найти версию в __init__.py")

def update_pyproject_toml(version):
    """Обновляет версию в pyproject.toml"""
    pyproject_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pyproject.toml')
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_content = re.sub(
        r'version = "[^"]*"',
        f'version = "{version}"',
        content
    )
    
    with open(pyproject_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Обновлена версия в pyproject.toml: {version}")

def main():
    """Основная функция скрипта"""
    try:
        version = get_version_from_init()
        update_pyproject_toml(version)
        print("Версия успешно обновлена во всех файлах!")
        return 0
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 