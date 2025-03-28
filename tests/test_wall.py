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
    
    def test_wall_id_uniqueness(self):
        """Тест уникальности ID стен"""
        # Создаем несколько стен
        wall1 = Wall(QPointF(0, 0), QPointF(100, 100))
        wall2 = Wall(QPointF(200, 200), QPointF(300, 300))
        wall3 = Wall(QPointF(400, 400), QPointF(500, 500))
        
        # Проверяем, что ID разные
        assert wall1.id != wall2.id
        assert wall1.id != wall3.id
        assert wall2.id != wall3.id
        
        # Проверяем, что ID начинаются с "w"
        assert wall1.id.startswith("w")
        assert wall2.id.startswith("w")
        assert wall3.id.startswith("w")
        
        # Проверяем, что ID находятся в множестве существующих ID
        assert wall1.id in Wall._existing_ids
        assert wall2.id in Wall._existing_ids
        assert wall3.id in Wall._existing_ids
    
    def test_wall_set_id(self):
        """Тест установки ID стены"""
        # Создаем стену
        wall1 = Wall(QPointF(0, 0), QPointF(100, 100))
        wall2 = Wall(QPointF(200, 200), QPointF(300, 300))
        
        old_id1 = wall1.id
        
        # Проверяем успешную установку уникального ID
        new_id = "w_test_unique"
        result = wall1.set_id(new_id)
        
        assert result is True
        assert wall1.id == new_id
        assert old_id1 not in Wall._existing_ids
        assert new_id in Wall._existing_ids
        
        # Проверяем невозможность установки неуникального ID
        old_id2 = wall2.id
        result = wall2.set_id(new_id)
        
        assert result is False
        assert wall2.id == old_id2  # ID не должен измениться
        
        # Проверяем возможность установки того же ID для той же стены
        result = wall1.set_id(new_id)
        assert result is True
        assert wall1.id == new_id 