#!/usr/bin/env python3

import os
import sys
import pytest

if __name__ == '__main__':
    # Добавляем корневую директорию проекта в sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Запускаем все тесты
    print("Starting tests...")
    pytest.main(['-xvs', 'tests']) 