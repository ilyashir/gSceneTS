import sys
import os
import unittest
from PyQt6.QtCore import Qt, QPointF, QEvent
from PyQt6.QtWidgets import QApplication, QGraphicsSceneMouseEvent, QMessageBox
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QMouseEvent
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from field_widget import FieldWidget
from properties_window import PropertiesWindow
from robot import Robot
from wall import Wall
from region import Region

# Создаем экземпляр QApplication для тестов
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestMouseEvents(unittest.TestCase):
    """Тесты для обработки событий мыши в FieldWidget"""
    
    def setUp(self):
        """Настройка тестового окружения перед каждым тестом"""
        # Перехватываем QMessageBox.warning для автоматического закрытия
        self.patcher_msg = patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Ok)
        self.mock_warning = self.patcher_msg.start()
        
        # Создание FieldWidget для тестов
        self.properties_window = PropertiesWindow()
        self.field_widget = FieldWidget(self.properties_window)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.patcher_msg.stop()
        
        # Удаляем все созданные объекты
        self.field_widget.walls.clear()
        self.field_widget.regions.clear()
        
        # Очищаем сцену
        if self.field_widget.scene():
            self.field_widget.scene().clear()
    
    def test_create_wall_with_mouse(self):
        """Тест создания стены с помощью мыши"""
        # Устанавливаем режим рисования стен
        self.field_widget.set_drawing_mode("wall")
        
        # Эмулируем первый клик мыши (начало стены)
        start_position = self.field_widget.mapFromScene(QPointF(100, 100))
        QTest.mouseClick(self.field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, start_position)
        
        # Проверяем, что начальная точка стены установлена
        self.assertIsNotNone(self.field_widget.wall_start)
        
        # Эмулируем второй клик мыши (конец стены)
        end_position = self.field_widget.mapFromScene(QPointF(200, 200))
        QTest.mouseClick(self.field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, end_position)
        
        # Проверяем, что начальная точка стены сброшена после создания стены
        self.assertIsNone(self.field_widget.wall_start)
        
        # Проверяем, что стена создана
        self.assertGreater(len(self.field_widget.walls), 0)
        
        # Проверяем координаты созданной стены
        wall = self.field_widget.walls[-1]
        # Учитываем, что координаты могут быть привязаны к сетке
        self.assertLessEqual(abs(wall.line().p1().x() - 100), self.field_widget.grid_size)
        self.assertLessEqual(abs(wall.line().p1().y() - 100), self.field_widget.grid_size)
        self.assertLessEqual(abs(wall.line().p2().x() - 200), self.field_widget.grid_size)
        self.assertLessEqual(abs(wall.line().p2().y() - 200), self.field_widget.grid_size)
    
    def test_create_region_with_mouse(self):
        """Тест создания региона с помощью мыши"""
        # Устанавливаем режим рисования регионов
        self.field_widget.set_drawing_mode("region")
        
        # Эмулируем первый клик мыши (начало региона)
        start_position = self.field_widget.mapFromScene(QPointF(100, 100))
        QTest.mouseClick(self.field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, start_position)
        
        # Проверяем, что начальная точка региона установлена
        self.assertIsNotNone(self.field_widget.region_start)
        
        # Эмулируем второй клик мыши (конец региона)
        end_position = self.field_widget.mapFromScene(QPointF(300, 300))
        QTest.mouseClick(self.field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, end_position)
        
        # Проверяем, что начальная точка региона сброшена после создания региона
        self.assertIsNone(self.field_widget.region_start)
        
        # Проверяем, что регион создан
        self.assertGreater(len(self.field_widget.regions), 0)
        
        # Проверяем размеры созданного региона
        region = self.field_widget.regions[-1]
        # Используем boundingRect для получения размеров
        rect = region.boundingRect()
        # Учитываем, что координаты могут быть привязаны к сетке
        self.assertTrue(150 <= rect.width() <= 250, f"Width is {rect.width()}")  # между 150 и 250
        self.assertTrue(150 <= rect.height() <= 250, f"Height is {rect.height()}")  # между 150 и 250
    
    def test_select_and_deselect_item(self):
        """Тест выделения и снятия выделения с объекта"""
        # Создаем стену
        wall = Wall(QPointF(100, 100), QPointF(200, 200))
        self.field_widget.objects_layer.addToGroup(wall)
        self.field_widget.walls.append(wall)
        
        # Выделяем стену
        self.field_widget.select_item(wall)
        
        # Проверяем, что стена выделена
        self.assertEqual(self.field_widget.selected_item, wall)
        
        # Снимаем выделение
        self.field_widget.deselect_item()
        
        # Проверяем, что выделение снято
        self.assertIsNone(self.field_widget.selected_item)

if __name__ == '__main__':
    unittest.main() 