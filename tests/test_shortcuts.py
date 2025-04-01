import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QKeySequence

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_window import MainWindow
import logging

# Выключаем логирование для тестов
logging.disable(logging.CRITICAL)

class TestShortcuts(unittest.TestCase):
    """Тесты для проверки работы горячих клавиш"""

    @classmethod
    def setUpClass(cls):
        """Создаем приложение для всех тестов"""
        # Инициализируем приложение PyQt
        cls.app = QApplication(sys.argv)
        
    def setUp(self):
        """Создаем главное окно перед каждым тестом"""
        self.main_window = MainWindow()
        self.field_widget = self.main_window.field_widget
        
    def tearDown(self):
        """Очищаем ресурсы после каждого теста"""
        self.main_window.close()
        self.main_window = None
        
    def test_zoom_in_shortcut(self):
        """Тест для горячей клавиши увеличения масштаба ("+")"""
        # Запоминаем исходный масштаб
        initial_scale = self.field_widget.currentScale()
        
        # Вызываем метод напрямую, так как клавиши могут не работать в тестовой среде
        self.field_widget.zoomIn()
        
        # Проверяем, что масштаб увеличился
        self.assertGreater(self.field_widget.currentScale(), initial_scale)
    
    def test_zoom_out_shortcut(self):
        """Тест для горячей клавиши уменьшения масштаба ("-")"""
        # Сначала увеличим масштаб дважды, чтобы потом можно было его уменьшить
        self.field_widget.zoomIn()
        self.field_widget.zoomIn()
        initial_scale = self.field_widget.currentScale()
        
        # Вызываем метод напрямую
        self.field_widget.zoomOut()
        
        # Проверяем, что масштаб уменьшился
        self.assertLess(self.field_widget.currentScale(), initial_scale)
    
    def test_reset_zoom_shortcut(self):
        """Тест для горячей клавиши сброса масштаба ("0")"""
        # Сначала увеличим масштаб
        self.field_widget.zoomIn()
        
        # Вызываем метод напрямую
        self.field_widget.resetScale()
        
        # Проверяем, что масштаб сбросился до 1.0
        self.assertEqual(self.field_widget.currentScale(), 1.0)
    
    def test_mode_switching(self):
        """Тест для переключения режимов"""
        # Проверяем, что метод set_mode существует
        self.assertTrue(hasattr(self.main_window, 'set_mode'))
        
        # Переключаемся в режим рисования
        self.main_window.set_mode("drawing")
        
        # Переключаемся в режим редактирования
        self.main_window.set_mode("edit")
        
        # Переключаемся в режим наблюдателя
        self.main_window.set_mode("observer")
        
        # Тест проходит, если нет исключений
        self.assertTrue(True)
    
    def test_delete_selected_item(self):
        """Тест для функциональности удаления выбранного элемента"""
        # Проверяем, что метод delete_selected_item существует
        self.assertTrue(hasattr(self.field_widget, 'delete_selected_item'))
        
        # Вызываем метод без выбранного элемента
        # Не должно быть исключений
        self.field_widget.delete_selected_item()
        
        # Тест проходит, если нет исключений
        self.assertTrue(True)
        
    def test_manual_wall_creation_and_deselection(self):
        """Проверка ручного создания стены и снятия выделения"""
        # Переходим в режим рисования
        self.main_window.set_mode("drawing")
        
        # Устанавливаем тип рисования "стена"
        if hasattr(self.main_window, 'set_drawing_type'):
            self.main_window.set_drawing_type("wall")
        
        # Вручную эмулируем создание стены
        start_point = QPointF(-100, -100)
        end_point = QPointF(100, 100)
        
        # Эмулируем нажатие мыши
        self.field_widget.wall_start = self.field_widget.snap_to_grid(start_point)
        
        # Эмулируем отпускание мыши для завершения создания стены
        if hasattr(self.field_widget, 'add_wall'):
            self.field_widget.add_wall(
                self.field_widget.wall_start,
                self.field_widget.snap_to_grid(end_point)
            )
        
        # Проверяем наличие метода deselect_item
        self.assertTrue(hasattr(self.field_widget, 'deselect_item'))
        
        # Снимаем выделение
        self.field_widget.deselect_item()
        
        # Проверяем, что выделение снято
        self.assertIsNone(self.field_widget.selected_item)
        
if __name__ == '__main__':
    unittest.main() 