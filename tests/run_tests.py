#!/usr/bin/env python

import unittest
import sys
import os
import argparse
import time
import signal
import threading

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Класс для добавления таймаута к тестам
class TestMethodTimeout(unittest.TestCase):
    def setUp(self):
        # Сохраняем флаги для отслеживания состояния теста
        self._timer = None
        self._timeout_handler_called = False
        self._test_finished = False
        # Вызываем setUp родительского класса для корректной инициализации
        super().setUp()

    def tearDown(self):
        # Убеждаемся, что ресурсы нормально очищаются даже при таймауте
        try:
            # Вызываем tearDown родительского класса для корректной очистки ресурсов
            super().tearDown()
        except Exception as e:
            # Логируем исключение, но продолжаем выполнение 
            if hasattr(self, '_testMethodName'):
                print(f"Ошибка при очистке ресурсов в тесте {self._testMethodName}: {e}")
            else:
                print(f"Ошибка при очистке ресурсов: {e}")

    def _timeout_handler(self):
        if self._test_finished:
            return
            
        self._timeout_handler_called = True
        # Сигнализируем о завершении таймаута
        print("\nТаймаут выполнения теста превышен!")
        if hasattr(self, '_current_test_method'):
            print(f"Тест {self._current_test_method} не завершился за отведенное время (10 секунд)")
        
        # Пытаемся корректно выполнить tearDown перед завершением
        try:
            if hasattr(self, 'tearDown'):
                self.tearDown()
        except Exception as e:
            print(f"Ошибка при принудительном вызове tearDown: {e}")
            
        # Принудительное завершение теста
        sys.stderr.write("ТАЙМАУТ: Тест принудительно завершен\n")
        # Используем _exit для принудительного завершения процесса
        os._exit(1)

    def run(self, result=None):
        # Запоминаем метод теста для вывода информации о таймауте
        if hasattr(self, '_testMethodName'):
            self._current_test_method = self._testMethodName
            
        # Создаем таймер для отслеживания превышения времени выполнения (10 секунд)
        self._timer = threading.Timer(10.0, self._timeout_handler)
        self._timer.daemon = True
        self._timer.start()
        
        try:
            # Вызываем оригинальный метод run
            super().run(result)
            # Отмечаем, что тест завершился нормально
            self._test_finished = True
        finally:
            # Отключаем таймер, если он активен
            if self._timer:
                self._timer.cancel()
                del self._timer
                self._timer = None

# Модифицируем класс TestShortcuts для добавления таймаута
def add_timeout_to_test_classes():
    # Импортируем классы тестов
    from test_shortcuts import TestShortcuts
    from test_field_widget import TestFieldWidget
    from test_wall import TestWall
    from test_robot import TestRobot
    from test_region import TestRegion
    from test_mouse_events import TestMouseEvents
    from test_ui_interactions import TestUIInteractions
    from test_theme_switching import TestThemeSwitching
    from test_performance import TestPerformance
    from test_xml_start_position import TestXMLStartPosition
    
    # Список тестовых классов для модификации
    test_classes = [
        TestShortcuts,
        TestFieldWidget,
        TestWall,
        TestRobot,
        TestRegion,
        TestMouseEvents,
        TestUIInteractions,
        TestThemeSwitching,
        TestPerformance,
        TestXMLStartPosition
    ]
    
    # Для каждого класса добавляем миксин TestMethodTimeout
    for test_class in test_classes:
        # Запоминаем оригинальное имя класса и модуль
        original_module = test_class.__module__
        original_name = test_class.__name__
        
        # Создаем новый класс на основе оригинального и TestMethodTimeout
        new_class = type(
            original_name,
            (TestMethodTimeout, test_class),
            {}
        )
        
        # Сохраняем оригинальные атрибуты
        new_class.__module__ = original_module
        
        # Обновляем класс в его оригинальном модуле
        import sys
        module = sys.modules[original_module]
        setattr(module, original_name, new_class)
        
        # Также обновляем в globals() для использования в этом модуле
        globals()[original_name] = new_class
        
        print(f"Добавлен таймаут к тестовому классу {original_name}")

# Пытаемся импортировать colorama для цветного вывода
try:
    from colorama import init, Fore, Style
    init()  # Инициализация colorama для работы в Windows
    has_colors = True
except ImportError:
    has_colors = False
    print("Для цветного вывода установите colorama: pip install colorama")

# Список известных проблемных тестов, которые следует пропустить
SKIP_TESTS = [
    # Тест test_manual_wall_creation_and_deselection исправлен с использованием моков
]

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

# Импортируем тесты (делаем это после определения TestMethodTimeout)
add_timeout_to_test_classes()

# Функция для пропуска известных проблемных тестов
def skip_problematic_tests():
    """Помечает известные проблемные тесты как пропущенные."""
    for test_name in SKIP_TESTS:
        parts = test_name.split('.')
        if len(parts) == 3:
            module_name, class_name, method_name = parts
            
            # Получаем класс
            try:
                test_class = globals()[class_name]
                
                # Получаем оригинальный метод
                original_method = getattr(test_class, method_name)
                
                # Создаем декорированный метод, пропускающий тест
                def skipping_method(self, original=original_method):
                    raise unittest.SkipTest(f"Тест пропущен: известная проблема")
                
                # Заменяем оригинальный метод на декорированный
                setattr(test_class, method_name, skipping_method)
                
                print(f"{Fore.BLUE if has_colors else ''}Тест {test_name} будет пропущен.{Style.RESET_ALL if has_colors else ''}")
            except (KeyError, AttributeError) as e:
                print(f"{Fore.YELLOW if has_colors else ''}Не удалось пропустить тест {test_name}: {e}{Style.RESET_ALL if has_colors else ''}")

def run_specific_tests(test_names):
    """
    Запускает только указанные тесты.
    
    Args:
        test_names: Список имен тестовых классов или методов для запуска
    
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
        'ui': TestUIInteractions,
        'theme': TestThemeSwitching,
        'performance': TestPerformance,
        'xml_start_position': TestXMLStartPosition,
    }
    
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()
    
    # Устанавливаем таймаут для методов тестирования (5 секунд)
    if hasattr(loader, 'testMethodTimeout'):
        loader.testMethodTimeout = 5
    
    # Создаем набор тестов
    suite = unittest.TestSuite()
    
    for name in test_names:
        # Проверяем, содержит ли имя теста точку, что указывает на конкретный метод
        if '.' in name:
            parts = name.split('.')
            if len(parts) == 2:
                # Формат: class_name.method_name
                class_name, method_name = parts
                
                if class_name in test_classes:
                    test_class = test_classes[class_name]
                    # Получаем только заданный метод теста
                    test_method = loader.loadTestsFromName(method_name, test_class)
                    suite.addTest(test_method)
                else:
                    print(f"{Fore.YELLOW if has_colors else ''}Предупреждение: Тестовый класс '{class_name}' не найден. Доступные классы: {', '.join(test_classes.keys())}{Style.RESET_ALL if has_colors else ''}")
            else:
                print(f"{Fore.YELLOW if has_colors else ''}Некорректный формат имени теста: '{name}'. Используйте формат 'class.method' или просто 'class'{Style.RESET_ALL if has_colors else ''}")
        elif name in test_classes:
            # Если это имя класса - загружаем все методы класса
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
    """Запускает все доступные тесты."""
    # Применяем пропуски проблемных тестов
    skip_problematic_tests()
    
    # Загружаем все тесты
    loader = unittest.TestLoader()
    
    # Создаем тестовый набор для всех модулей тестирования
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты из каждого модуля тестирования
    test_suite.addTests(loader.loadTestsFromTestCase(TestShortcuts))
    test_suite.addTests(loader.loadTestsFromTestCase(TestFieldWidget))
    test_suite.addTests(loader.loadTestsFromTestCase(TestWall))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRobot))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRegion))
    test_suite.addTests(loader.loadTestsFromTestCase(TestMouseEvents))
    test_suite.addTests(loader.loadTestsFromTestCase(TestUIInteractions))
    test_suite.addTests(loader.loadTestsFromTestCase(TestThemeSwitching))
    test_suite.addTests(loader.loadTestsFromTestCase(TestPerformance))  # Добавляем тесты производительности
    test_suite.addTests(loader.loadTestsFromTestCase(TestXMLStartPosition))  # Добавляем тесты XML стартовой позиции
    
    # Запускаем тесты
    runner = ColoredTextTestRunner() if has_colors else unittest.TextTestRunner()
    test_result = runner.run(test_suite)
    
    return test_result.wasSuccessful()

def _print_help():
    """Выводит справку по использованию скрипта."""
    logger.info("Использование: python run_tests.py [test(s)]")
    logger.info("где [test(s)] может быть одним из следующих имен тестов или их комбинацией:")
    logger.info("  shortcuts - тесты горячих клавиш")
    logger.info("  field - тесты виджета поля")
    logger.info("  wall - тесты стены")
    logger.info("  robot - тесты робота")
    logger.info("  region - тесты региона")
    logger.info("  mouse - тесты событий мыши")
    logger.info("  ui - тесты взаимодействия с пользовательским интерфейсом")
    logger.info("  theme - тесты переключения темы")
    logger.info("  performance - тесты производительности")
    logger.info("  xml_start_position - тесты XML для стартовой позиции")
    logger.info("  all - запустить все тесты")

if __name__ == '__main__':
    # Настраиваем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description='Запуск тестов для приложения gSceneTS')
    parser.add_argument('tests', nargs='*', help='Список тестов для запуска (shortcuts, field, wall, robot, region, mouse, ui, theme)')
    parser.add_argument('--all', action='store_true', help='Запустить все тесты')
    parser.add_argument('--no-color', action='store_true', help='Отключить цветной вывод')
    parser.add_argument('--no-skip', action='store_true', help='Не пропускать проблемные тесты')
    
    args = parser.parse_args()
    
    # Отключаем цветной вывод, если указан флаг --no-color
    if args.no_color:
        has_colors = False
    
    # Пропускаем проблемные тесты, если не указан флаг --no-skip
    if not args.no_skip:
        skip_problematic_tests()
    
    # Определяем режим запуска
    if args.all or not args.tests:
        # Запускаем все тесты
        success = run_all_tests()
    else:
        # Запускаем указанные тесты
        success = run_specific_tests(args.tests)
    
    # Выходим с соответствующим кодом
    sys.exit(not success) 