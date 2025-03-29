import sys
import os
import pytest
from PyQt6.QtCore import QPointF, QLineF
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QMessageBox

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем класс стены
from wall import Wall

class TestWall:
    """Класс для тестирования Wall"""
    
    def test_wall_initialization(self, app):
        """Тест инициализации стены с параметрами по умолчанию"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Проверяем атрибуты
        assert wall.stroke_width == 10  # Ширина стены по умолчанию - 10
        assert wall.id.startswith("w")  # ID должен начинаться с 'w'
        
        # Проверяем координаты стены
        assert wall.line().x1() == 0
        assert wall.line().y1() == 0
        assert wall.line().x2() == 100
        assert wall.line().y2() == 100
    
    def test_wall_set_stroke_width(self, app):
        """Тест установки толщины стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Проверяем толщину по умолчанию
        assert wall.stroke_width == 10
        
        # Устанавливаем новую толщину
        wall.set_stroke_width(5)
        
        # Проверяем новую толщину
        assert wall.stroke_width == 5
    
    def test_wall_updating_context_manager(self, app):
        """Тест контекстного менеджера для обновления стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Используем контекстный менеджер
        with wall.updating():
            pass
        
        # Здесь мы просто проверяем, что контекстный менеджер
        # не вызывает ошибок при использовании
    
    def test_wall_highlight(self, app):
        """Тест подсветки стены"""
        # Создаем стену
        wall = Wall(QPointF(0, 0), QPointF(100, 100))
        
        # Включаем подсветку
        wall.set_highlight(True)
        
        # Отключаем подсветку
        wall.set_highlight(False)
    
    def test_wall_id_uniqueness(self, app):
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
    
    def test_wall_set_id(self, app):
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
    
    def test_wall_init(self, app):
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
        assert wall.id == "test_wall"
        assert wall.stroke_width == 5
        assert wall.line().x1() == 100
        assert wall.line().y1() == 150
        assert wall.line().x2() == 300
        assert wall.line().y2() == 350
    
    def test_wall_update_point1(self, app):
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
        assert wall.line().x1() == 50
        assert wall.line().y1() == 75
        assert wall.line().x2() == 100  # Вторая точка должна остаться неизменной
        assert wall.line().y2() == 100
    
    def test_wall_update_point2(self, app):
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
        assert wall.line().x1() == 0    # Первая точка должна остаться неизменной
        assert wall.line().y1() == 0
        assert wall.line().x2() == 150
        assert wall.line().y2() == 200
    
    def test_wall_update_stroke_width(self, app):
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
        assert wall.stroke_width == 10 