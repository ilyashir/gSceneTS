import unittest
import time
import logging
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit
from PyQt6.QtCore import Qt, QTimer, QPointF
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
from utils.xml_handler import XMLHandler

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

    def test_element_creation_performance(self):
        """Тест производительности создания и удаления элементов сцены"""
        # Обеспечиваем режим редактирования
        if not self.main_window.field_widget.edit_mode:
            self.main_window.field_widget.set_edit_mode(True)
            QApplication.processEvents()
        
        # Измеряем время создания стены
        num_walls = 20  # Количество стен для создания
        wall_creation_times = []
        
        for i in range(num_walls):
            # Создаем точки для стены в разных местах сцены
            start_point = QPointF(i * 20 - 200, i * 20 - 200)
            end_point = QPointF(i * 20 - 100, i * 20 - 100)
            
            # Измеряем время создания стены
            start_time = time.time()
            wall = self.main_window.field_widget.add_wall(start_point, end_point)
            QApplication.processEvents()
            wall_creation_times.append(time.time() - start_time)
        
        # Измеряем время создания региона
        num_regions = 10  # Количество регионов для создания
        region_creation_times = []
        
        for i in range(num_regions):
            # Создаем точки для региона в разных местах сцены
            points = [
                QPointF(i * 30, i * 30),
                QPointF(i * 30 + 100, i * 30),
                QPointF(i * 30 + 100, i * 30 + 100),
                QPointF(i * 30, i * 30 + 100)
            ]
            
            # Измеряем время создания региона
            start_time = time.time()
            region = self.main_window.field_widget.add_region(points)
            QApplication.processEvents()
            region_creation_times.append(time.time() - start_time)
        
        # Измеряем время удаления стен
        wall_deletion_times = []
        walls = self.main_window.field_widget.walls.copy()
        
        for wall in walls:
            # Выбираем стену
            self.main_window.field_widget.select_item(wall)
            QApplication.processEvents()
            
            # Измеряем время удаления стены
            start_time = time.time()
            self.main_window.field_widget.delete_selected_item()
            QApplication.processEvents()
            wall_deletion_times.append(time.time() - start_time)
        
        # Измеряем время удаления регионов
        region_deletion_times = []
        regions = self.main_window.field_widget.regions.copy()
        
        for region in regions:
            # Выбираем регион
            self.main_window.field_widget.select_item(region)
            QApplication.processEvents()
            
            # Измеряем время удаления региона
            start_time = time.time()
            self.main_window.field_widget.delete_selected_item()
            QApplication.processEvents()
            region_deletion_times.append(time.time() - start_time)
        
        # Логируем результаты
        avg_wall_creation_time = sum(wall_creation_times) / len(wall_creation_times) if wall_creation_times else 0
        avg_region_creation_time = sum(region_creation_times) / len(region_creation_times) if region_creation_times else 0
        avg_wall_deletion_time = sum(wall_deletion_times) / len(wall_deletion_times) if wall_deletion_times else 0
        avg_region_deletion_time = sum(region_deletion_times) / len(region_deletion_times) if region_deletion_times else 0
        
        logger.info(f"Среднее время создания стены: {avg_wall_creation_time:.6f} секунд")
        logger.info(f"Среднее время создания региона: {avg_region_creation_time:.6f} секунд")
        logger.info(f"Среднее время удаления стены: {avg_wall_deletion_time:.6f} секунд")
        logger.info(f"Среднее время удаления региона: {avg_region_deletion_time:.6f} секунд")
    
    def test_mode_switching_performance(self):
        """Тест производительности переключения режимов работы"""
        mode_switch_times = {}
        
        # Режимы в нашем приложении
        # 1. Режим редактирования (edit_mode = True, draw_mode = False)
        # 2. Режим рисования (edit_mode = False, draw_mode = True)
        # 3. Режим наблюдения (edit_mode = False, draw_mode = False)
        
        # Измеряем время переключения между всеми комбинациями режимов
        # Начинаем с режима редактирования
        self.main_window.field_widget.set_edit_mode(True)
        self.main_window.field_widget.set_drawing_mode(None)
        QApplication.processEvents()
        
        # Время переключения в режим рисования
        start_time = time.time()
        self.main_window.field_widget.set_edit_mode(False)
        self.main_window.field_widget.set_drawing_mode("wall")
        QApplication.processEvents()
        edit_to_draw_time = time.time() - start_time
        
        # Время переключения в режим наблюдения
        start_time = time.time()
        self.main_window.field_widget.set_edit_mode(False)
        self.main_window.field_widget.set_drawing_mode(None)
        QApplication.processEvents()
        draw_to_observe_time = time.time() - start_time
        
        # Время переключения в режим редактирования
        start_time = time.time()
        self.main_window.field_widget.set_edit_mode(True)
        self.main_window.field_widget.set_drawing_mode(None)
        QApplication.processEvents()
        observe_to_edit_time = time.time() - start_time
        
        # Логируем результаты
        logger.info(f"Время переключения из режима редактирования в режим рисования: {edit_to_draw_time:.6f} секунд")
        logger.info(f"Время переключения из режима рисования в режим наблюдения: {draw_to_observe_time:.6f} секунд")
        logger.info(f"Время переключения из режима наблюдения в режим редактирования: {observe_to_edit_time:.6f} секунд")
    
    def test_zoom_performance(self):
        """Тест производительности операций масштабирования"""
        # Получаем текущий масштаб
        initial_scale = self.main_window.field_widget.transform().m11()
        
        # Измеряем время увеличения масштаба
        zoom_in_times = []
        for _ in range(5):
            start_time = time.time()
            self.main_window.field_widget.zoomIn()
            QApplication.processEvents()
            zoom_in_times.append(time.time() - start_time)
        
        # Измеряем время уменьшения масштаба
        zoom_out_times = []
        for _ in range(5):
            start_time = time.time()
            self.main_window.field_widget.zoomOut()
            QApplication.processEvents()
            zoom_out_times.append(time.time() - start_time)
        
        # Измеряем время сброса масштаба
        start_time = time.time()
        self.main_window.field_widget.resetScale()
        QApplication.processEvents()
        reset_zoom_time = time.time() - start_time
        
        # Логируем результаты
        avg_zoom_in_time = sum(zoom_in_times) / len(zoom_in_times)
        avg_zoom_out_time = sum(zoom_out_times) / len(zoom_out_times)
        
        logger.info(f"Среднее время увеличения масштаба: {avg_zoom_in_time:.6f} секунд")
        logger.info(f"Среднее время уменьшения масштаба: {avg_zoom_out_time:.6f} секунд")
        logger.info(f"Время сброса масштаба: {reset_zoom_time:.6f} секунд")

    def test_xml_generation_performance(self):
        """Тест производительности генерации XML-представления сцены"""
        # Подготовка сцены - создаем несколько стен и регионов
        if not self.main_window.field_widget.edit_mode:
            self.main_window.field_widget.set_edit_mode(True)
            QApplication.processEvents()
        
        # Создаем стены
        for i in range(10):
            start_point = QPointF(i * 20 - 200, i * 20 - 200)
            end_point = QPointF(i * 20 - 100, i * 20 - 100)
            self.main_window.field_widget.add_wall(start_point, end_point)
        
        # Создаем регионы
        for i in range(5):
            points = [
                QPointF(i * 30, i * 30),
                QPointF(i * 30 + 100, i * 30),
                QPointF(i * 30 + 100, i * 30 + 100),
                QPointF(i * 30, i * 30 + 100)
            ]
            self.main_window.field_widget.add_region(points)
        
        QApplication.processEvents()
        
        # Измеряем время генерации XML
        scene_width = self.main_window.scene_width
        scene_height = self.main_window.scene_height
        
        # Используем только стены и регионы для генерации XML, чтобы избежать проблем с direction робота
        start_time = time.time()
        xml_handler = XMLHandler(scene_width=scene_width, scene_height=scene_height)
        formatted_xml = xml_handler.generate_xml(
            walls=self.main_window.field_widget.walls,
            regions=self.main_window.field_widget.regions,
            robot_model=None  # Не используем робота в тесте
        )
        xml_generation_time = time.time() - start_time
        
        # Измеряем повторную генерацию XML для большей точности
        start_time = time.time()
        xml_handler = XMLHandler(scene_width=scene_width, scene_height=scene_height)
        formatted_xml = xml_handler.generate_xml(
            walls=self.main_window.field_widget.walls,
            regions=self.main_window.field_widget.regions,
            robot_model=None  # Не используем робота в тесте
        )
        xml_generation_time_2 = time.time() - start_time
        
        # Измеряем время генерации XML для больших сцен (добавляем еще элементов)
        for i in range(20):
            start_point = QPointF(i * 20 + 100, i * 20 + 100)
            end_point = QPointF(i * 20 + 200, i * 20 + 200)
            self.main_window.field_widget.add_wall(start_point, end_point)
        
        for i in range(10):
            points = [
                QPointF(i * 30 + 200, i * 30 + 200),
                QPointF(i * 30 + 300, i * 30 + 200),
                QPointF(i * 30 + 300, i * 30 + 300),
                QPointF(i * 30 + 200, i * 30 + 300)
            ]
            self.main_window.field_widget.add_region(points)
        
        QApplication.processEvents()
        
        start_time = time.time()
        xml_handler = XMLHandler(scene_width=scene_width, scene_height=scene_height)
        formatted_xml = xml_handler.generate_xml(
            walls=self.main_window.field_widget.walls,
            regions=self.main_window.field_widget.regions,
            robot_model=None  # Не используем робота в тесте
        )
        xml_generation_time_large = time.time() - start_time
        
        # Логируем результаты
        logger.info(f"Время генерации XML (малая сцена): {xml_generation_time:.6f} секунд")
        logger.info(f"Время повторной генерации XML (малая сцена): {xml_generation_time_2:.6f} секунд")
        logger.info(f"Время генерации XML (большая сцена): {xml_generation_time_large:.6f} секунд")
        
        # Выводим размер сгенерированного XML
        logger.info(f"Размер сгенерированного XML: {len(formatted_xml)} байт")

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
        elif test_name == "elements":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_element_creation_performance"))
            unittest.TextTestRunner().run(suite)
        elif test_name == "modes":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_mode_switching_performance"))
            unittest.TextTestRunner().run(suite)
        elif test_name == "zoom":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_zoom_performance"))
            unittest.TextTestRunner().run(suite)
        elif test_name == "xml":
            suite = unittest.TestSuite()
            suite.addTest(TestPerformance("test_xml_generation_performance"))
            unittest.TextTestRunner().run(suite)
        else:
            print("Укажите тип теста: simple, complex, elements, modes, zoom, xml")
    else:
        print("Укажите тип теста: simple, complex, elements, modes, zoom, xml")
        print("Например: python tests/test_performance.py simple") 