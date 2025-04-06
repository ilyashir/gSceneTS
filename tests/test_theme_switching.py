import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_window import MainWindow
from custom_widgets import EditableLineEdit, ColorPickerButton
import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Создаем экземпляр QApplication для тестов
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestThemeSwitching(unittest.TestCase):
    """Тестирование переключения тем кастомных виджетов"""
    
    def setUp(self):
        """Настраивает тестовое окружение для каждого теста"""
        self.main_window = MainWindow()  # Создаем новое главное окно
        
    def tearDown(self):
        """Очищает тестовое окружение после каждого теста"""
        self.main_window.close()
        
    @patch('custom_widgets.EditableLineEdit.set_theme')
    def test_apply_theme_recursively_calls_set_theme_on_editable_line_edit(self, mock_set_theme):
        """Проверяет, что метод _apply_theme_recursively вызывает set_theme у EditableLineEdit"""
        # Создаем экземпляр EditableLineEdit и добавляем его в главное окно
        editable = EditableLineEdit(self.main_window)
        self.main_window.layout().addWidget(editable)
        
        # Переключаем тему в главном окне
        initial_theme = self.main_window.is_dark_theme
        self.main_window.toggle_theme()
        
        # Проверяем, что метод set_theme был вызван с правильным аргументом
        mock_set_theme.assert_called_with(not initial_theme)
        
    @patch('custom_widgets.ColorPickerButton.set_theme')
    def test_apply_theme_recursively_calls_set_theme_on_color_picker_button(self, mock_set_theme):
        """Проверяет, что метод _apply_theme_recursively вызывает set_theme у ColorPickerButton"""
        # Создаем экземпляр ColorPickerButton и добавляем его в главное окно
        color_button = ColorPickerButton(parent=self.main_window)
        self.main_window.layout().addWidget(color_button)
        
        # Переключаем тему в главном окне
        initial_theme = self.main_window.is_dark_theme
        self.main_window.toggle_theme()
        
        # Проверяем, что метод set_theme был вызван с правильным аргументом
        mock_set_theme.assert_called_with(not initial_theme)
        
    @patch('main_window.MainWindow._apply_theme_recursively')
    def test_toggle_theme_calls_apply_theme_recursively(self, mock_apply_recursively):
        """Проверяет, что метод toggle_theme вызывает _apply_theme_recursively"""
        # Переключаем тему в главном окне
        self.main_window.toggle_theme()
        
        # Проверяем, что метод _apply_theme_recursively был вызван
        mock_apply_recursively.assert_called()

if __name__ == '__main__':
    unittest.main() 