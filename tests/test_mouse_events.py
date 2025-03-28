import sys
import os
import pytest
from PyQt6.QtCore import Qt, QPointF, QEvent
from PyQt6.QtWidgets import QApplication, QGraphicsSceneMouseEvent
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QMouseEvent

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from field_widget import FieldWidget
from properties_window import PropertiesWindow
from robot import Robot
from wall import Wall
from region import Region

@pytest.fixture
def field_widget(qapp):
    """Фикстура для создания экземпляра FieldWidget для каждого теста."""
    properties_window = PropertiesWindow()
    field = FieldWidget(properties_window)
    return field

class TestMouseEvents:
    """Тесты для обработки событий мыши в FieldWidget"""
    
    def test_create_wall_with_mouse(self, field_widget):
        """Тест создания стены с помощью мыши"""
        # Устанавливаем режим рисования стен
        field_widget.set_drawing_mode("wall")
        
        # Эмулируем первый клик мыши (начало стены)
        start_position = field_widget.mapFromScene(QPointF(100, 100))
        QTest.mouseClick(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, start_position)
        
        # Проверяем, что начальная точка стены установлена
        assert field_widget.wall_start is not None
        
        # Эмулируем второй клик мыши (конец стены)
        end_position = field_widget.mapFromScene(QPointF(200, 200))
        QTest.mouseClick(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, end_position)
        
        # Проверяем, что начальная точка стены сброшена после создания стены
        assert field_widget.wall_start is None
        
        # Проверяем, что стена создана
        assert len(field_widget.walls) > 0
        
        # Проверяем координаты созданной стены
        wall = field_widget.walls[-1]
        # Учитываем, что координаты могут быть привязаны к сетке
        assert abs(wall.line().p1().x() - 100) <= field_widget.grid_size
        assert abs(wall.line().p1().y() - 100) <= field_widget.grid_size
        assert abs(wall.line().p2().x() - 200) <= field_widget.grid_size
        assert abs(wall.line().p2().y() - 200) <= field_widget.grid_size
    
    def test_create_region_with_mouse(self, field_widget):
        """Тест создания региона с помощью мыши"""
        # Устанавливаем режим рисования регионов
        field_widget.set_drawing_mode("region")
        
        # Эмулируем первый клик мыши (начало региона)
        start_position = field_widget.mapFromScene(QPointF(100, 100))
        QTest.mouseClick(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, start_position)
        
        # Проверяем, что начальная точка региона установлена
        assert field_widget.region_start is not None
        
        # Эмулируем второй клик мыши (конец региона)
        end_position = field_widget.mapFromScene(QPointF(300, 300))
        QTest.mouseClick(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         Qt.KeyboardModifier.NoModifier, end_position)
        
        # Проверяем, что начальная точка региона сброшена после создания региона
        assert field_widget.region_start is None
        
        # Проверяем, что регион создан
        assert len(field_widget.regions) > 0
        
        # Проверяем размеры созданного региона
        region = field_widget.regions[-1]
        # Учитываем, что координаты могут быть привязаны к сетке
        assert 150 <= region.rect().width() <= 250  # между 150 и 250
        assert 150 <= region.rect().height() <= 250  # между 150 и 250
    
    def test_select_and_deselect_item(self, field_widget):
        """Тест выделения и снятия выделения с объекта"""
        # Создаем стену
        wall = Wall(QPointF(100, 100), QPointF(200, 200))
        field_widget.objects_layer.addToGroup(wall)
        field_widget.walls.append(wall)
        
        # Выделяем стену
        field_widget.select_item(wall)
        
        # Проверяем, что стена выделена
        assert field_widget.selected_item == wall
        
        # Снимаем выделение
        field_widget.deselect_item()
        
        # Проверяем, что выделение снято
        assert field_widget.selected_item is None 