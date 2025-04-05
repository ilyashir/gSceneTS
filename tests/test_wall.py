import sys
import os
import unittest
from PyQt6.QtCore import QPointF, QLineF
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QApplication, QMessageBox
from unittest.mock import patch

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем класс стены
from wall import Wall

# Создаем экземпляр QApplication для тестов
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestWall(unittest.TestCase):
    """Класс для тестирования Wall"""
    
    def setUp(self):
        """Настройка тестового окружения перед каждым тестом"""
        # Перехватываем QMessageBox.warning для автоматического закрытия
        self.patcher_msg = patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Ok)
        self.mock_warning = self.patcher_msg.start()
        
        # Перехватываем другие диалоги
        self.patcher_critical = patch('PyQt6.QtWidgets.QMessageBox.critical', return_value=QMessageBox.StandardButton.Ok)
        self.mock_critical = self.patcher_critical.start()
        
        self.patcher_info = patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok)
        self.mock_info = self.patcher_info.start()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.patcher_msg.stop()
        self.patcher_critical.stop()
        self.patcher_info.stop()
    
    def test_wall_initialization(self):
        """Тест инициализации стены с параметрами по умолчанию"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Проверяем атрибуты
        self.assertEqual(wall.stroke_width, 10)  # Ширина стены по умолчанию - 10
        self.assertTrue(wall.id.startswith("w"))  # ID должен начинаться с 'w'
        
        # Проверяем координаты стены
        self.assertEqual(wall.line().x1(), 0)
        self.assertEqual(wall.line().y1(), 0)
        self.assertEqual(wall.line().x2(), 100)
        self.assertEqual(wall.line().y2(), 100)
    
    def test_wall_set_stroke_width(self):
        """Тест установки толщины стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Проверяем толщину по умолчанию
        self.assertEqual(wall.stroke_width, 10)
        
        # Устанавливаем новую толщину
        wall.set_stroke_width(5)
        
        # Проверяем новую толщину
        self.assertEqual(wall.stroke_width, 5)
    
    def test_wall_updating_context_manager(self):
        """Тест контекстного менеджера для обновления стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Используем контекстный менеджер
        with wall.updating():
            pass
        
        # Здесь мы просто проверяем, что контекстный менеджер
        # не вызывает ошибок при использовании
    
    def test_wall_highlight(self):
        """Тест подсветки стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Включаем подсветку
        wall.set_highlight(True)
        
        # Отключаем подсветку
        wall.set_highlight(False)
    
    def test_wall_id_uniqueness(self):
        """Тест уникальности ID стен"""
        # Создаем несколько стен
        wall1 = Wall(QPointF(0, 0), QPointF(100, 100))
        wall2 = Wall(QPointF(200, 200), QPointF(300, 300))
        wall3 = Wall(QPointF(400, 400), QPointF(500, 500))
        
        # Проверяем, что ID разные
        self.assertNotEqual(wall1.id, wall2.id)
        self.assertNotEqual(wall1.id, wall3.id)
        self.assertNotEqual(wall2.id, wall3.id)
        
        # Проверяем, что ID начинаются с "w"
        self.assertTrue(wall1.id.startswith("w"))
        self.assertTrue(wall2.id.startswith("w"))
        self.assertTrue(wall3.id.startswith("w"))
        
        # Проверяем, что ID находятся в множестве существующих ID
        self.assertIn(wall1.id, Wall._existing_ids)
        self.assertIn(wall2.id, Wall._existing_ids)
        self.assertIn(wall3.id, Wall._existing_ids)
    
    def test_wall_set_id(self):
        """Тест установки ID стены"""
        # Создаем стену
        wall1 = Wall(QPointF(0, 0), QPointF(100, 100))
        wall2 = Wall(QPointF(200, 200), QPointF(300, 300))
        
        old_id1 = wall1.id
        
        # Проверяем успешную установку уникального ID
        new_id = "w_test_unique"
        result = wall1.set_id(new_id)
        
        self.assertTrue(result)
        self.assertEqual(wall1.id, new_id)
        self.assertNotIn(old_id1, Wall._existing_ids)
        self.assertIn(new_id, Wall._existing_ids)
        
        # Проверяем невозможность установки неуникального ID
        old_id2 = wall2.id
        result = wall2.set_id(new_id)
        
        self.assertFalse(result)
        self.assertEqual(wall2.id, old_id2)  # ID не должен измениться
        
        # Проверяем возможность установки того же ID для той же стены
        result = wall1.set_id(new_id)
        self.assertTrue(result)
        self.assertEqual(wall1.id, new_id)
    
    def test_wall_init(self):
        """Тест инициализации стены с правильными параметрами"""
        # Создаем стену
        start = QPointF(100, 150)
        end = QPointF(300, 350)
        wall = Wall(start, end)
        
        # Задаем ширину стены
        wall.set_stroke_width(5)
        
        # Задаем ID стены
        wall.set_id("test_wall")
        
        # Проверяем атрибуты
        self.assertEqual(wall.id, "test_wall")
        self.assertEqual(wall.stroke_width, 5)
        self.assertEqual(wall.line().x1(), 100)
        self.assertEqual(wall.line().y1(), 150)
        self.assertEqual(wall.line().x2(), 300)
        self.assertEqual(wall.line().y2(), 350)
    
    def test_wall_update_point1(self):
        """Тест обновления первой точки стены"""
        # Создаем стену
        start = QPointF(0, 0)
        end = QPointF(100, 100)
        wall = Wall(start, end)
        wall.set_stroke_width(1)
        wall.set_id("wall_point1")
        
        # Обновляем первую точку с помощью setLine
        new_start = QPointF(50, 75)
        wall.setLine(new_start.x(), new_start.y(), end.x(), end.y())
        
        # Проверяем новую позицию первой точки
        self.assertEqual(wall.line().x1(), 50)
        self.assertEqual(wall.line().y1(), 75)
        self.assertEqual(wall.line().x2(), 100)  # Вторая точка должна остаться неизменной
        self.assertEqual(wall.line().y2(), 100)
    
    def test_wall_update_point2(self):
        """Тест обновления второй точки стены"""
        # Создаем стену
        start = QPointF(0, 0)
        end = QPointF(100, 100)
        wall = Wall(start, end)
        wall.set_stroke_width(1)
        wall.set_id("wall_point2")
        
        # Обновляем вторую точку с помощью setLine
        new_end = QPointF(150, 200)
        wall.setLine(start.x(), start.y(), new_end.x(), new_end.y())
        
        # Проверяем новую позицию второй точки
        self.assertEqual(wall.line().x1(), 0)    # Первая точка должна остаться неизменной
        self.assertEqual(wall.line().y1(), 0)
        self.assertEqual(wall.line().x2(), 150)
        self.assertEqual(wall.line().y2(), 200)
    
    def test_wall_update_stroke_width(self):
        """Тест обновления толщины стены"""
        # Создаем стену
        start = QPointF(0, 0)
        end = QPointF(100, 100)
        wall = Wall(start, end)
        wall.set_stroke_width(1)
        wall.set_id("wall_width")
        
        # Обновляем толщину
        wall.set_stroke_width(10)
        
        # Проверяем новую толщину
        self.assertEqual(wall.stroke_width, 10)

if __name__ == '__main__':
    unittest.main() 