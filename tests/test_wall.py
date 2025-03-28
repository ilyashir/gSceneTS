import sys
import os
import pytest
from PyQt6.QtCore import QPointF, QLineF
from PyQt6.QtGui import QPen, QColor

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wall import Wall

class TestWall:
    """Тесты для класса Wall"""
    
    def test_wall_initialization(self):
        """Тест инициализации стены"""
        # Создаем стену
        start = QPointF(100, 100)
        end = QPointF(300, 100)
        wall = Wall(start, end)
        
        # Проверяем, что стена создалась с правильными координатами
        assert wall.line().p1() == start
        assert wall.line().p2() == end
    
    def test_wall_set_stroke_width(self):
        """Тест установки толщины стены"""
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Проверяем, что начальная толщина - 10
        assert wall.stroke_width == 10
        
        # Устанавливаем новую толщину
        new_width = 20
        wall.set_stroke_width(new_width)
        
        # Проверяем, что толщина изменилась
        assert wall.stroke_width == new_width
    
    def test_wall_updating_context_manager(self):
        """Тест контекстного менеджера для обновления стены"""
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Используем контекстный менеджер для обновления стены
        with wall.updating():
            wall.setLine(10, 10, 200, 200)
        
        # Проверяем, что координаты стены обновились
        assert wall.line().x1() == 10
        assert wall.line().y1() == 10
        assert wall.line().x2() == 200
        assert wall.line().y2() == 200
    
    def test_wall_highlight(self):
        """Тест выделения стены"""
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Включаем подсветку
        wall.set_highlight(True)
        
        # Отключаем подсветку
        wall.set_highlight(False) 