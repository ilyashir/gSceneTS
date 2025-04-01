#!/usr/bin/env python
"""
Точка входа в приложение gSceneTS.
Можно запустить как python -m gscene
"""

import os
import sys

# Добавляем текущую директорию в PYTHONPATH для корректного импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main() 