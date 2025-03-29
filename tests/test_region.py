import sys
import os
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем тестируемые модули
from region import Region

class TestRegion:
    """Тесты для класса Region"""
    
    def test_region_init(self):
        """Тест инициализации региона с правильными параметрами"""
        # Создаем регион
        pos = QPointF(100, 150)
        width = 200
        height = 300
        color = "#FF0000"
        region = Region(pos, width, height, color)
        
        # Проверяем атрибуты
        assert region.color == color
        assert region.rect().width() == width
        assert region.rect().height() == height
        
        # Проверяем, что прямоугольник имеет правильные координаты
        # В конструкторе QGraphicsRectItem координаты устанавливаются по значениям pos
        assert region.rect().x() == pos.x()
        assert region.rect().y() == pos.y()
        
        # По умолчанию позиция самого объекта (0,0) до явного вызова setPos
        assert region.pos().x() == 0
        assert region.pos().y() == 0
        
        # Проверяем, что ID сгенерирован и начинается с "r"
        assert region.id.startswith("r")
    
    def test_region_set_id(self):
        """Тест установки ID региона"""
        # Создаем регион
        pos = QPointF(0, 0)
        region = Region(pos, 100, 100)
        original_id = region.id
        
        # Устанавливаем новый ID
        new_id = "test_region"
        result = region.set_id(new_id)
        
        # Проверяем, что ID изменился
        assert result is True
        assert region.id == new_id
        assert original_id != new_id
    
    def test_region_update_size(self):
        """Тест обновления размера региона"""
        # Создаем регион
        pos = QPointF(0, 0)
        width = 100
        height = 100
        region = Region(pos, width, height)
        
        # Обновляем размер через setRect
        new_width = 150
        new_height = 200
        region.setRect(0, 0, new_width, new_height)
        
        # Проверяем новый размер
        assert region.rect().width() == new_width
        assert region.rect().height() == new_height
    
    def test_region_update_color(self):
        """Тест обновления цвета региона"""
        # Создаем регион
        pos = QPointF(0, 0)
        region = Region(pos, 100, 100, "#000000")
        
        # Обновляем цвет
        new_color = "#FFFFFF"
        region.set_color(new_color)
        
        # Проверяем новый цвет
        assert region.color == new_color
    
    def test_region_initialization(self):
        """Тест инициализации региона с позицией и размерами"""
        # Создаем регион с заданной позицией
        pos = QPointF(100, 100)
        width = 200
        height = 150
        region = Region(pos, width, height)
        
        # Позиционируем регион явно
        region.setPos(pos)
        
        # Проверяем, что регион создался с правильными размерами
        assert region.rect().width() == width
        assert region.rect().height() == height
        
        # Проверяем, что позиция установлена правильно
        assert region.pos().x() == pos.x()
        assert region.pos().y() == pos.y()
    
    def test_region_set_color(self):
        """Тест установки цвета региона"""
        region = Region(QPointF(0, 0), 100, 100)
        
        # Проверяем, что у региона есть атрибут color
        assert hasattr(region, 'color')
        
        # Сохраняем исходный цвет
        original_color = region.color
        
        # Устанавливаем новый цвет (строка HEX)
        new_color = "#00FF00"
        region.set_color(new_color)
        
        # Проверяем, что цвет изменился
        assert region.color == new_color
        assert region.color != original_color
    
    def test_region_highlight(self):
        """Тест выделения региона"""
        region = Region(QPointF(0, 0), 100, 100)
        
        # Включаем подсветку
        region.set_highlight(True)
        
        # Отключаем подсветку
        region.set_highlight(False) 