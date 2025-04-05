import sys
import os
import unittest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем тестируемые модули
from region import Region

class TestRegion(unittest.TestCase):
    """Тесты для класса Region"""
    
    def test_region_init(self):
        """Тест инициализации региона с правильными параметрами"""
        # Создаем регион с помощью списка точек
        points = [
            QPointF(100, 150),
            QPointF(300, 150),
            QPointF(300, 450),
            QPointF(100, 450)
        ]
        color = "#FF0000"
        region = Region(points, color=color)
        
        # Проверяем атрибуты
        self.assertEqual(region.color, color)
        # Проверяем, что ограничивающий прямоугольник имеет правильные размеры
        rect = region.boundingRect()
        self.assertEqual(rect.width(), 200)  # 300 - 100
        self.assertEqual(rect.height(), 300)  # 450 - 150
        
        # Проверяем, что ID сгенерирован и начинается с "r"
        self.assertTrue(region.id.startswith("r"))
    
    def test_region_set_id(self):
        """Тест установки ID региона"""
        # Создаем регион с помощью списка точек
        points = [
            QPointF(0, 0),
            QPointF(100, 0),
            QPointF(100, 100),
            QPointF(0, 100)
        ]
        region = Region(points)
        original_id = region.id
        
        # Устанавливаем новый ID
        new_id = "r99"
        result = region.set_id(new_id)
        
        # Проверяем, что ID изменился
        self.assertTrue(result)
        self.assertEqual(region.id, new_id)
        self.assertNotEqual(original_id, new_id)
    
    def test_region_update_size(self):
        """Тест обновления размера региона"""
        # Создаем регион с помощью списка точек
        points = [
            QPointF(0, 0),
            QPointF(100, 0),
            QPointF(100, 100),
            QPointF(0, 100)
        ]
        region = Region(points)
        
        # Обновляем размер через создание нового пути
        new_points = [
            QPointF(0, 0),
            QPointF(150, 0),
            QPointF(150, 200),
            QPointF(0, 200)
        ]
        new_path = QPainterPath()
        new_path.moveTo(new_points[0])
        for i in range(1, len(new_points)):
            new_path.lineTo(new_points[i])
        new_path.closeSubpath()
        region.setPath(new_path)
        
        # Проверяем новый размер
        rect = region.boundingRect()
        self.assertEqual(rect.width(), 150)
        self.assertEqual(rect.height(), 200)
    
    def test_region_update_color(self):
        """Тест обновления цвета региона"""
        # Создаем регион с помощью списка точек
        points = [
            QPointF(0, 0),
            QPointF(100, 0),
            QPointF(100, 100),
            QPointF(0, 100)
        ]
        region = Region(points, color="#000000")
        
        # Обновляем цвет
        new_color = "#FFFFFF"
        region.set_color(new_color)
        
        # Проверяем новый цвет
        self.assertEqual(region.color, new_color)
    
    def test_region_initialization(self):
        """Тест инициализации региона с позицией и размерами"""
        # Создаем регион с заданными точками
        points = [
            QPointF(100, 100),
            QPointF(300, 100),
            QPointF(300, 250),
            QPointF(100, 250)
        ]
        region = Region(points)
        
        # Позиционируем регион явно
        region.setPos(QPointF(100, 100))
        
        # Проверяем, что регион создался с правильными размерами
        rect = region.boundingRect()
        self.assertEqual(rect.width(), 200)
        self.assertEqual(rect.height(), 150)
        
        # Проверяем, что позиция установлена правильно
        self.assertEqual(region.pos().x(), 100)
        self.assertEqual(region.pos().y(), 100)
    
    def test_region_set_color(self):
        """Тест установки цвета региона"""
        points = [
            QPointF(0, 0),
            QPointF(100, 0),
            QPointF(100, 100),
            QPointF(0, 100)
        ]
        region = Region(points)
        
        # Проверяем, что у региона есть атрибут color
        self.assertTrue(hasattr(region, 'color'))
        
        # Сохраняем исходный цвет
        original_color = region.color
        
        # Устанавливаем новый цвет (строка HEX)
        new_color = "#00FF00"
        region.set_color(new_color)
        
        # Проверяем, что цвет изменился
        self.assertEqual(region.color, new_color)
        self.assertNotEqual(region.color, original_color)
    
    def test_region_highlight(self):
        """Тест выделения региона"""
        points = [
            QPointF(0, 0),
            QPointF(100, 0),
            QPointF(100, 100),
            QPointF(0, 100)
        ]
        region = Region(points)
        
        # Включаем подсветку
        region.set_highlight(True)
        
        # Отключаем подсветку
        region.set_highlight(False)

if __name__ == '__main__':
    unittest.main() 