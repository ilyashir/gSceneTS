import sys
import os
import unittest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor
import math

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from robot import Robot

class TestRobot(unittest.TestCase):
    """Тесты для класса Robot"""
    
    def setUp(self):
        """Сбросить экземпляр робота перед каждым тестом"""
        Robot.reset_instance()
    
    def test_robot_initialization(self):
        """Тест инициализации робота"""
        # Создаем робота
        pos = QPointF(100, 100)
        robot = Robot(pos)
        
        # Проверяем, что робот создался с правильной позицией
        self.assertEqual(robot.pos(), pos)
        
        # Проверяем, что размеры робота близки к ожидаемым (около 50x50)
        # Реальный размер может немного отличаться из-за особенностей реализации
        self.assertLessEqual(abs(robot.boundingRect().width() - 50), 1)
        self.assertLessEqual(abs(robot.boundingRect().height() - 50), 1)
    
    def test_robot_rotation(self):
        """Тест вращения робота"""
        robot = Robot(QPointF(0, 0))
        
        # Запоминаем исходное значение направления
        old_direction = robot.direction
        
        # Устанавливаем новый угол поворота, отличающийся от исходного
        new_rotation = old_direction + 45
        robot.set_direction(new_rotation)
        
        # Проверяем, что поворот изменился
        self.assertEqual(robot.direction, new_rotation)
    
    def test_robot_highlight(self):
        """Тест выделения робота"""
        robot = Robot(QPointF(0, 0))
        
        # Включаем подсветку
        robot.set_highlight(True)
        
        # Отключаем подсветку
        robot.set_highlight(False)
    
    def test_robot_init(self):
        """Тест инициализации робота с правильными параметрами"""
        # Создаем робота
        pos = QPointF(150, 200)
        robot = Robot(pos)
        robot.set_direction(45)
        
        # Проверяем атрибуты
        self.assertEqual(robot.id, "trikKitRobot")  # Фиксированный ID
        self.assertEqual(robot.pos().x(), 150)
        self.assertEqual(robot.pos().y(), 200)
        self.assertEqual(robot.direction, 45)
    
    def test_robot_update_position(self):
        """Тест обновления позиции робота"""
        # Создаем робота
        robot = Robot(QPointF(0, 0))
        
        # Обновляем позицию
        new_pos = QPointF(75, 125)
        robot.setPos(new_pos)
        
        # Проверяем новую позицию
        self.assertEqual(robot.pos().x(), 75)
        self.assertEqual(robot.pos().y(), 125)
    
    def test_robot_update_direction(self):
        """Тест обновления направления робота"""
        # Создаем робота
        robot = Robot(QPointF(0, 0))
        
        # Обновляем направление
        robot.set_direction(90)
        
        # Проверяем новое направление
        self.assertEqual(robot.direction, 90)
        
    def test_robot_negative_direction(self):
        """Тест отрицательного направления робота"""
        # Создаем робота с отрицательным направлением
        robot = Robot(QPointF(0, 0))
        robot.set_direction(-45)
        
        # Проверяем, что направление правильно обрабатывается
        self.assertEqual(robot.direction, -45)

if __name__ == '__main__':
    unittest.main() 