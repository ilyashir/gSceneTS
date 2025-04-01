#!/usr/bin/env python

import unittest
import sys
import os
import argparse

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Пытаемся импортировать colorama для цветного вывода
try:
    from colorama import init, Fore, Style
    init()  # Инициализация colorama для работы в Windows
    has_colors = True
except ImportError:
    has_colors = False
    print("Для цветного вывода установите colorama: pip install colorama")

# Создаем класс для цветного вывода тестов
if has_colors:
    class ColoredTextTestResult(unittest.TextTestResult):
        """Класс для цветного вывода результатов тестов"""
        
        def addSuccess(self, test):
            """Зеленый цвет для успешных тестов"""
            self.stream.write(f"{Fore.GREEN}[✓] ")
            super().addSuccess(test)
            self.stream.write(Style.RESET_ALL)
            
        def addError(self, test, err):
            """Красный цвет для ошибок"""
            self.stream.write(f"{Fore.RED}[✗] ")
            super().addError(test, err)
            self.stream.write(Style.RESET_ALL)
            
        def addFailure(self, test, err):
            """Желтый цвет для неудачных тестов"""
            self.stream.write(f"{Fore.YELLOW}[✗] ")
            super().addFailure(test, err)
            self.stream.write(Style.RESET_ALL)
            
        def addSkip(self, test, reason):
            """Синий цвет для пропущенных тестов"""
            self.stream.write(f"{Fore.BLUE}[S] ")
            super().addSkip(test, reason)
            self.stream.write(Style.RESET_ALL)
            
    class ColoredTextTestRunner(unittest.TextTestRunner):
        """Цветной запускатель тестов"""
        
        def _makeResult(self):
            return ColoredTextTestResult(self.stream, self.descriptions, self.verbosity)
        
        def run(self, test):
            """Запуск тестов с цветным итоговым отчетом"""
            result = super().run(test)
            
            # Выводим цветной итоговый отчет
            if result.wasSuccessful():
                print(f"\n{Fore.GREEN}Все тесты пройдены успешно!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Тесты не пройдены.{Style.RESET_ALL}")
                
            return result

# Импортируем тесты
from test_shortcuts import TestShortcuts
from test_field_widget import TestFieldWidget
from test_wall import TestWall
from test_robot import TestRobot
from test_region import TestRegion
from test_mouse_events import TestMouseEvents
from test_ui_interactions import TestUIInteractions

def run_specific_tests(test_names):
    """
    Запускает только указанные тесты.
    
    Args:
        test_names: Список имен тестовых классов для запуска
    
    Returns:
        bool: True если все тесты прошли успешно, иначе False
    """
    # Словарь доступных тестовых классов
    test_classes = {
        'shortcuts': TestShortcuts,
        'field': TestFieldWidget,
        'wall': TestWall,
        'robot': TestRobot,
        'region': TestRegion,
        'mouse': TestMouseEvents,
        'ui': TestUIInteractions
    }
    
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()
    
    # Создаем набор тестов
    suite = unittest.TestSuite()
    
    for name in test_names:
        if name in test_classes:
            suite.addTest(loader.loadTestsFromTestCase(test_classes[name]))
        else:
            print(f"{Fore.YELLOW if has_colors else ''}Предупреждение: Тест '{name}' не найден. Доступные тесты: {', '.join(test_classes.keys())}{Style.RESET_ALL if has_colors else ''}")
    
    # Если не выбрано ни одного теста, выводим сообщение и возвращаем True
    if suite.countTestCases() == 0:
        print(f"{Fore.YELLOW if has_colors else ''}Не выбрано ни одного валидного теста.{Style.RESET_ALL if has_colors else ''}")
        return True
    
    # Запускаем тесты с цветным выводом, если доступно
    if has_colors:
        runner = ColoredTextTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner(verbosity=2)
    
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """
    Запускает все доступные тесты.
    
    Returns:
        bool: True если все тесты прошли успешно, иначе False
    """
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()
    
    # Находим все тесты в текущей директории
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Запускаем тесты с цветным выводом, если доступно
    if has_colors:
        runner = ColoredTextTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner(verbosity=2)
    
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Настраиваем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description='Запуск тестов для приложения gSceneTS')
    parser.add_argument('tests', nargs='*', help='Список тестов для запуска (shortcuts, field, wall, robot, region, mouse, ui)')
    parser.add_argument('--all', action='store_true', help='Запустить все тесты')
    parser.add_argument('--no-color', action='store_true', help='Отключить цветной вывод')
    
    args = parser.parse_args()
    
    # Отключаем цветной вывод, если указан флаг --no-color
    if args.no_color:
        has_colors = False
    
    # Определяем режим запуска
    if args.all or not args.tests:
        # Запускаем все тесты
        success = run_all_tests()
    else:
        # Запускаем указанные тесты
        success = run_specific_tests(args.tests)
    
    # Выходим с соответствующим кодом
    sys.exit(not success) 