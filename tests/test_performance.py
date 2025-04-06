import unittest
import time
import logging
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit
from PyQt6.QtCore import Qt, QTimer
import sys
import os
import gc

# Добавляем корневую директорию в sys.path для импорта модулей проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_window import MainWindow
from config import Config
from custom_widgets import EditableLineEdit, ColorPickerButton
from properties.robot_properties_widget import RobotPropertiesWidget
from properties.wall_properties_widget import WallPropertiesWidget
from properties.region_properties_widget import RegionPropertiesWidget

# Счетчик вызовов set_theme
set_theme_calls = 0

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestPerformance(unittest.TestCase):
    """Тесты производительности для различных операций приложения"""
    
    # Сохраняем оригинальные методы как статические переменные класса
    original_editable_set_theme = None
    original_colorpicker_set_theme = None
    
    @classmethod
    def setUpClass(cls):
        # Сохраняем оригинальные методы set_theme
        TestPerformance.original_editable_set_theme = EditableLineEdit.set_theme
        TestPerformance.original_colorpicker_set_theme = ColorPickerButton.set_theme
        
        # Создаем единственный экземпляр QApplication для всех тестов
        cls.app = QApplication.instance() or QApplication(sys.argv)
    
    def setUp(self):
        # Инициализируем главное окно перед каждым тестом
        self.main_window = MainWindow()
        # Обеспечиваем начальное состояние с темной темой
        if not self.main_window.is_dark_theme:
            self.main_window.toggle_theme()
            QApplication.processEvents()
        
        # Замена стандартного метода set_theme на отслеживающий
        global set_theme_calls
        set_theme_calls = 0
        
        # Переопределяем метод set_theme для отслеживания вызовов
        def count_set_theme_editable(self, is_dark_theme=True):
            global set_theme_calls
            set_theme_calls += 1
            return TestPerformance.original_editable_set_theme(self, is_dark_theme)
        
        def count_set_theme_colorpicker(self, is_dark_theme):
            global set_theme_calls
            set_theme_calls += 1
            return TestPerformance.original_colorpicker_set_theme(self, is_dark_theme)
        
        # Заменяем методы
        EditableLineEdit.set_theme = count_set_theme_editable
        ColorPickerButton.set_theme = count_set_theme_colorpicker
        
    def tearDown(self):
        # Восстанавливаем оригинальные методы
        EditableLineEdit.set_theme = TestPerformance.original_editable_set_theme
        ColorPickerButton.set_theme = TestPerformance.original_colorpicker_set_theme
        
        # Закрываем окно после каждого теста
        if hasattr(self, 'main_window'):
            self.main_window.close()
            self.main_window = None
            
        # Вызываем сборщик мусора для освобождения ресурсов
        gc.collect()
        
        # Обрабатываем все оставшиеся события
        QApplication.processEvents()
        
    @classmethod
    def tearDownClass(cls):
        # Восстанавливаем оригинальные методы, если они были сохранены
        if TestPerformance.original_editable_set_theme:
            EditableLineEdit.set_theme = TestPerformance.original_editable_set_theme
        if TestPerformance.original_colorpicker_set_theme:
            ColorPickerButton.set_theme = TestPerformance.original_colorpicker_set_theme
        
        # Выходим из приложения после всех тестов
        pass
    
    def test_theme_toggle_performance(self):
        """Тест производительности переключения темы"""
        # Прогрев - переключаем тему несколько раз перед измерением
        for _ in range(2):
            self.main_window.toggle_theme()
            QApplication.processEvents()
        
        # Сбрасываем счетчик перед измерением
        global set_theme_calls
        set_theme_calls = 0
        
        # Измеряем время переключения с темной на светлую тему
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем на светлую тему
        QApplication.processEvents()
        dark_to_light_time = time.time() - start_time
        dark_to_light_calls = set_theme_calls
        
        # Сбрасываем счетчик перед следующим измерением
        set_theme_calls = 0
        
        # Измеряем время переключения со светлой на темную тему
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем обратно на темную тему
        QApplication.processEvents()
        light_to_dark_time = time.time() - start_time
        light_to_dark_calls = set_theme_calls
        
        # Логируем результаты
        logger.info(f"Время переключения с темной на светлую тему: {dark_to_light_time:.6f} секунд")
        logger.info(f"Количество вызовов set_theme при переключении с темной на светлую: {dark_to_light_calls}")
        logger.info(f"Время переключения со светлой на темную тему: {light_to_dark_time:.6f} секунд")
        logger.info(f"Количество вызовов set_theme при переключении со светлой на темную: {light_to_dark_calls}")
        logger.info(f"Среднее время переключения темы: {(dark_to_light_time + light_to_dark_time) / 2:.6f} секунд")
        
        # Альтернативный подход для сравнения - измеряем без рекурсивного обхода
        # Временно заменяем метод _apply_theme_recursively на заглушку
        original_recursive_method = self.main_window._apply_theme_recursively
        
        def dummy_recursive_method(widget, is_dark_theme):
            pass  # Ничего не делаем
        
        # Подменяем метод на заглушку
        self.main_window._apply_theme_recursively = dummy_recursive_method
        
        # Измеряем время переключения с темной на светлую тему без рекурсивного обхода
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем на светлую тему
        QApplication.processEvents()
        dark_to_light_no_recursion_time = time.time() - start_time
        
        # Измеряем время переключения со светлой на темную тему без рекурсивного обхода
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем обратно на темную тему
        QApplication.processEvents()
        light_to_dark_no_recursion_time = time.time() - start_time
        
        # Возвращаем оригинальный метод
        self.main_window._apply_theme_recursively = original_recursive_method
        
        # Логируем результаты без рекурсивного обхода
        logger.info(f"Время переключения с темной на светлую тему без рекурсии: {dark_to_light_no_recursion_time:.6f} секунд")
        logger.info(f"Время переключения со светлой на темную тему без рекурсии: {light_to_dark_no_recursion_time:.6f} секунд")
        logger.info(f"Среднее время переключения темы без рекурсии: {(dark_to_light_no_recursion_time + light_to_dark_no_recursion_time) / 2:.6f} секунд")
        
        # Вычисляем, сколько времени занимает рекурсивный обход
        recursion_overhead = ((dark_to_light_time + light_to_dark_time) / 2) - ((dark_to_light_no_recursion_time + light_to_dark_no_recursion_time) / 2)
        logger.info(f"Дополнительное время, затрачиваемое на рекурсивный обход: {recursion_overhead:.6f} секунд")
        
        # Выводим процентное соотношение времени, затрачиваемого на рекурсивный обход
        percentage_overhead = (recursion_overhead / ((dark_to_light_time + light_to_dark_time) / 2)) * 100 if ((dark_to_light_time + light_to_dark_time) / 2) > 0 else 0
        logger.info(f"Процент времени, затрачиваемого на рекурсивный обход: {percentage_overhead:.2f}%")
    
    def test_complex_ui_theme_toggle_performance(self):
        """Тест производительности переключения темы с большим количеством виджетов"""
        # Создаем контейнер с большим количеством виджетов
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Добавляем различные виджеты, включая кастомные
        widget_references = []  # Сохраняем ссылки на созданные виджеты
        for i in range(5):  # Уменьшаем количество виджетов для снижения нагрузки
            # Добавляем обычные виджеты Qt
            label = QLabel(f"Label {i}")
            layout.addWidget(label)
            widget_references.append(label)
            
            button = QPushButton(f"Button {i}")
            layout.addWidget(button)
            widget_references.append(button)
            
            checkbox = QCheckBox(f"Checkbox {i}")
            layout.addWidget(checkbox)
            widget_references.append(checkbox)
            
            line_edit = QLineEdit(f"LineEdit {i}")
            layout.addWidget(line_edit)
            widget_references.append(line_edit)
            
            # Добавляем кастомные виджеты
            editable = EditableLineEdit()
            editable.setText(f"Editable {i}")
            layout.addWidget(editable)
            widget_references.append(editable)
            
            color_picker = ColorPickerButton(Qt.GlobalColor.red)
            layout.addWidget(color_picker)
            widget_references.append(color_picker)
            
            # Добавляем виджеты свойств - только один тип для каждой итерации
            if i % 3 == 0:
                props = RobotPropertiesWidget()
                layout.addWidget(props)
                widget_references.append(props)
            elif i % 3 == 1:
                props = WallPropertiesWidget()
                layout.addWidget(props)
                widget_references.append(props)
            else:
                props = RegionPropertiesWidget()
                layout.addWidget(props)
                widget_references.append(props)
                
        # Добавляем контейнер в главное окно
        self.main_window.setCentralWidget(container)
        
        # Сохраняем ссылку на контейнер
        self.test_container = container
        self.widget_references = widget_references
        
        # Обрабатываем события, чтобы виджеты отобразились
        QApplication.processEvents()
        
        # Прогрев - переключаем тему несколько раз перед измерением
        for _ in range(2):
            self.main_window.toggle_theme()
            QApplication.processEvents()
        
        # Сбрасываем счетчик перед измерением
        global set_theme_calls
        set_theme_calls = 0
        
        # Измеряем время переключения с темной на светлую тему с большим количеством виджетов
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем на светлую тему
        QApplication.processEvents()
        dark_to_light_complex_time = time.time() - start_time
        dark_to_light_complex_calls = set_theme_calls
        
        # Сбрасываем счетчик перед следующим измерением
        set_theme_calls = 0
        
        # Измеряем время переключения со светлой на темную тему с большим количеством виджетов
        start_time = time.time()
        self.main_window.toggle_theme()  # Переключаем обратно на темную тему
        QApplication.processEvents()
        light_to_dark_complex_time = time.time() - start_time
        light_to_dark_complex_calls = set_theme_calls
        
        # Логируем результаты
        logger.info(f"Время переключения с темной на светлую тему (сложный UI): {dark_to_light_complex_time:.6f} секунд")
        logger.info(f"Количество вызовов set_theme при переключении с темной на светлую (сложный UI): {dark_to_light_complex_calls}")
        logger.info(f"Время переключения со светлой на темную тему (сложный UI): {light_to_dark_complex_time:.6f} секунд")
        logger.info(f"Количество вызовов set_theme при переключении со светлой на темную (сложный UI): {light_to_dark_complex_calls}")
        logger.info(f"Среднее время переключения темы (сложный UI): {(dark_to_light_complex_time + light_to_dark_complex_time) / 2:.6f} секунд")

if __name__ == "__main__":
    # Запуск только одного теста для предотвращения ошибок с Qt
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "complex":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_complex_ui_theme_toggle_performance"))
            unittest.TextTestRunner().run(suite)
        elif test_name == "simple":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_theme_toggle_performance"))
            unittest.TextTestRunner().run(suite)
        else:
            print("Укажите тип теста: simple или complex")
    else:
        print("Укажите тип теста: simple или complex")
        print("Например: python tests/test_performance.py simple") 