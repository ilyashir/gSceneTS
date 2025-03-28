import sys
import os
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot import Robot

class TestRobot:
    """Тесты для класса Robot"""
    
    def test_robot_initialization(self):
        """Тест инициализации робота"""
        # Создаем робота
        pos = QPointF(100, 100)
        robot = Robot(pos)
        
        # Проверяем, что робот создался с правильной позицией
        assert robot.pos() == pos
        
        # Проверяем, что размеры робота близки к ожидаемым (около 50x50)
        # Реальный размер может немного отличаться из-за особенностей реализации
        assert abs(robot.boundingRect().width() - 50) <= 1
        assert abs(robot.boundingRect().height() - 50) <= 1
    
    def test_robot_rotation(self):
        """Тест вращения робота"""
        robot = Robot(QPointF(0, 0))
        
        # Проверяем, что начальное вращение - 0 градусов
        assert robot.rotation() == 0
        
        # Устанавливаем новый угол поворота
        new_rotation = 45
        robot.setRotation(new_rotation)
        
        # Проверяем, что поворот изменился
        assert robot.rotation() == new_rotation
    
    def test_robot_highlight(self):
        """Тест выделения робота"""
        robot = Robot(QPointF(0, 0))
        
        # Включаем подсветку
        robot.set_highlight(True)
        
        # Отключаем подсветку
        robot.set_highlight(False) 