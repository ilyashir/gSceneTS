import sys
import os
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from region import Region

class TestRegion:
    """Тесты для класса Region"""
    
    def test_region_initialization(self):
        """Тест инициализации региона"""
        # Создаем регион
        pos = QPointF(100, 100)
        width = 200
        height = 150
        region = Region(pos, width, height)
        
        # Проверяем, что регион создался с правильными размерами
        assert region.rect().width() == width
        assert region.rect().height() == height
        
        # Проверяем, что координаты региона корректны
        # Примечание: в данной реализации Region координаты x, y задаются 
        # в rect, а не в позиции объекта
        assert region.rect().x() == pos.x()
        assert region.rect().y() == pos.y()
    
    def test_region_set_color(self):
        """Тест установки цвета региона"""
        region = Region(QPointF(0, 0), 100, 100)
        
        # Проверяем, что у региона есть атрибут color
        assert hasattr(region, 'color')
        
        # Сохраняем исходный цвет
        original_color = region.color
        
        # Устанавливаем новый цвет
        new_color = QColor(0, 255, 0, 100)
        region.set_color(new_color)
        
        # Проверяем, что цвет изменился
        assert region.color != original_color
    
    def test_region_highlight(self):
        """Тест выделения региона"""
        region = Region(QPointF(0, 0), 100, 100)
        
        # Включаем подсветку
        region.set_highlight(True)
        
        # Отключаем подсветку
        region.set_highlight(False) 