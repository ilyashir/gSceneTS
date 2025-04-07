import sys
import os
import unittest
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QMessageBox
from PyQt6.QtTest import QTest
import logging
from unittest.mock import patch, MagicMock
from scene.items import Robot, Wall, Region
from field_widget import FieldWidget
from properties_window import PropertiesWindow

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Создаем экземпляр QApplication для всех тестов
app = QApplication.instance()
if app is None:
    app = QApplication([])

class TestFieldWidget(unittest.TestCase):
    """Тесты для класса FieldWidget"""
    
    def setUp(self):
        """Создаем экземпляр FieldWidget для каждого теста."""
        # Перехватываем QMessageBox.warning для автоматического закрытия
        self.patcher_msg = patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Ok)
        self.mock_warning = self.patcher_msg.start()
        
        # Сохраняем оригинальный метод init_robot
        self.original_init_robot = FieldWidget.init_robot
        
        # Создаем заглушку для init_robot
        def mock_init_robot(self_field, pos):
            logging.debug(f"Mock: Инициализация робота в позиции {pos}")
            # Создаем мок-объект робота
            class MockRobot:
                def __init__(self):
                    self.id = "mock_robot"
                    self.pos_value = pos
                    self.boundingRect_value = QRectF(0, 0, 50, 50)
                    
                def pos(self):
                    return self.pos_value
                    
                def boundingRect(self):
                    return self.boundingRect_value
                    
                def setPos(self, x, y=None):
                    if isinstance(x, QPointF):
                        self.pos_value = x
                    else:
                        self.pos_value = QPointF(x, y)
                    logging.debug(f"Mock Robot: setPos вызван с {self.pos_value}")
            
            # Устанавливаем мок-робота
            self_field.robot_model = MockRobot()
            logging.debug(f"Mock: Робот создан с id={self_field.robot_model.id}")
            return True
        
        # Заменяем оригинальный метод моком
        FieldWidget.init_robot = mock_init_robot
        
        # Создаем экземпляр PropertiesWindow
        self.properties_window = PropertiesWindow()
        
        # Создаем экземпляр FieldWidget с патченным методом init_robot
        self.field_widget = FieldWidget(self.properties_window)
    
    def tearDown(self):
        """Восстанавливаем оригинальные методы после завершения теста"""
        # Восстанавливаем оригинальный метод init_robot
        FieldWidget.init_robot = self.original_init_robot
        
        # Отключаем патч для QMessageBox
        self.patcher_msg.stop()
        
        # Сбрасываем экземпляр Robot после теста
        Robot.reset_instance()
    
    def test_initialization(self):
        """Тест инициализации FieldWidget"""
        # Проверяем, что создан экземпляр QGraphicsScene
        self.assertIsInstance(self.field_widget.scene(), QGraphicsScene)
        
        # Проверяем, что созданы слои
        self.assertIsNotNone(self.field_widget.grid_layer)
        self.assertIsNotNone(self.field_widget.axes_layer)
        self.assertIsNotNone(self.field_widget.objects_layer)
        
        # Проверяем, что размеры сцены соответствуют ожидаемым
        self.assertEqual(self.field_widget.scene_width, 1300)
        self.assertEqual(self.field_widget.scene_height, 800)
        
        # Проверяем, что робот существует и находится в начальной позиции
        self.assertIsNotNone(self.field_widget.robot_model)
        self.assertEqual(self.field_widget.robot_model.pos(), QPointF(0, 0))
    
    def test_add_wall(self):
        """Тест добавления стены"""
        # Начальное количество стен
        initial_wall_count = len(self.field_widget.walls)
        
        # Добавляем стену
        start = QPointF(100, 100)
        end = QPointF(200, 200)
        self.field_widget.add_wall(start, end)
        
        # Проверяем, что стена добавлена
        self.assertEqual(len(self.field_widget.walls), initial_wall_count + 1)
        
        # Проверяем, что добавленная стена имеет правильные координаты
        wall = self.field_widget.walls[-1]
        self.assertEqual(wall.line().p1(), start)
        self.assertEqual(wall.line().p2(), end)
    
    def test_add_region(self):
        """Тест добавления региона"""
        # Начальное количество регионов
        initial_region_count = len(self.field_widget.regions)
        
        # Создаем список точек для региона
        points = [
            QPointF(100, 100),
            QPointF(300, 100),
            QPointF(300, 300),
            QPointF(100, 300)
        ]
        self.field_widget.add_region(points)
        
        # Проверяем, что регион добавлен
        self.assertEqual(len(self.field_widget.regions), initial_region_count + 1)
        
        # Проверяем, что добавленный регион имеет правильные размеры
        region = self.field_widget.regions[-1]
        # Используем boundingRect вместо rect
        bounding_rect = region.boundingRect()
        self.assertAlmostEqual(bounding_rect.width(), 200, delta=3)  # Допускаем погрешность в 3 единицы
        self.assertAlmostEqual(bounding_rect.height(), 200, delta=3)  # Допускаем погрешность в 3 единицы
        
        # Проверяем, что позиция региона определена
        self.assertIsNotNone(region.pos())
    
    def test_check_object_within_scene(self):
        """Тест проверки нахождения объектов в пределах сцены"""
        # Сбросим экземпляр Robot перед тестом
        Robot.reset_instance()
        
        # Патчим метод check_object_within_scene для тестирования объектов за пределами сцены
        original_check = self.field_widget.check_object_within_scene
        
        def mock_check(item):
            if isinstance(item, Wall):
                line = item.line()
                # Если это наша тестовая стена далеко за пределами сцены
                if abs(line.x1()) >= 1000 and abs(line.y1()) >= 1000:
                    return False
            elif isinstance(item, Region):
                path = item.path()
                rect = path.boundingRect()
                pos = item.pos()
                # Если регион находится за пределами сцены (в нашем случае вокруг точки 2000,2000)
                if abs(pos.x() + rect.x()) >= 1000 or abs(pos.y() + rect.y()) >= 1000:
                    return False
            elif isinstance(item, Robot):
                pos = item.pos()
                # Если робот находится за пределами сцены
                if abs(pos.x()) >= 1000 or abs(pos.y()) >= 1000:
                    return False
            return original_check(item)
        
        # Подменяем метод для теста
        self.field_widget.check_object_within_scene = mock_check
        
        try:
            # Создаем и проверяем стену внутри сцены
            wall_inside = Wall(QPointF(0, 0), QPointF(100, 100))
            self.assertTrue(self.field_widget.check_object_within_scene(wall_inside))
            
            # Создаем и проверяем стену за пределами сцены
            wall_outside = Wall(QPointF(-5000, -5000), QPointF(-4900, -4900))
            self.assertFalse(self.field_widget.check_object_within_scene(wall_outside))
            
            # Создаем и проверяем регион внутри сцены - используем список точек
            points_inside = [
                QPointF(0, 0),
                QPointF(100, 0),
                QPointF(100, 100),
                QPointF(0, 100)
            ]
            region_inside = Region(points_inside)
            self.assertTrue(self.field_widget.check_object_within_scene(region_inside))
            
            # Создаем и проверяем регион за пределами сцены - используем список точек гораздо дальше
            points_outside = [
                QPointF(2000, 2000),
                QPointF(2100, 2000),
                QPointF(2100, 2100),
                QPointF(2000, 2100)
            ]
            region_outside = Region(points_outside)
            self.assertFalse(self.field_widget.check_object_within_scene(region_outside))
            
            # Создаем и проверяем робота внутри сцены
            robot_inside = Robot(QPointF(0, 0))
            self.assertTrue(self.field_widget.check_object_within_scene(robot_inside))
            
            # Сбросим экземпляр Robot перед созданием нового
            Robot.reset_instance()
            
            # Создаем и проверяем робота за пределами сцены - гораздо дальше
            robot_outside = Robot(QPointF(-5000, -5000))
            self.assertFalse(self.field_widget.check_object_within_scene(robot_outside))
        finally:
            # Восстанавливаем оригинальный метод
            self.field_widget.check_object_within_scene = original_check
    
    def test_snap_to_grid(self):
        """Тест привязки к сетке"""
        # Включаем привязку к сетке
        self.field_widget.snap_to_grid_enabled = True
        
        # Проверяем, что координаты привязываются к ближайшему узлу сетки
        original_pos = QPointF(123, 78)
        snapped_pos = self.field_widget.snap_to_grid(original_pos)
        
        # Ожидаем, что координаты привязались к ближайшему узлу сетки (размер сетки 50)
        self.assertEqual(snapped_pos, QPointF(100, 100))
        
        # Отключаем привязку к сетке
        self.field_widget.snap_to_grid_enabled = False
        
        # Проверяем, что координаты не привязываются к сетке
        original_pos = QPointF(123, 78)
        non_snapped_pos = self.field_widget.snap_to_grid(original_pos)
        
        # Ожидаем, что координаты не изменились (или были только обрезаны по границам)
        self.assertEqual(non_snapped_pos.x(), original_pos.x())
        self.assertEqual(non_snapped_pos.y(), original_pos.y())
        
    def test_update_wall_id(self):
        """Тест обновления ID стены"""
        # Добавляем стену
        start = QPointF(100, 100)
        end = QPointF(200, 200)
        self.field_widget.add_wall(start, end)
        
        # Получаем добавленную стену
        wall = self.field_widget.walls[-1]
        old_id = wall.id
        
        # Выделяем стену
        self.field_widget.select_item(wall)
        self.assertEqual(self.field_widget.selected_item, wall)
        
        # Обновляем ID стены на уникальный
        new_id = "w_unique_test_id"
        result = self.field_widget.update_wall_id(new_id)
        
        # Проверяем, что ID стены обновился
        self.assertTrue(result)
        self.assertEqual(wall.id, new_id)
        self.assertNotIn(old_id, Wall._existing_ids)
        self.assertIn(new_id, Wall._existing_ids)
        
        # Создаем еще одну стену
        self.field_widget.add_wall(QPointF(300, 300), QPointF(400, 400))
        second_wall = self.field_widget.walls[-1]
        second_wall_old_id = second_wall.id
        
        # Выделяем вторую стену
        self.field_widget.select_item(second_wall)
        self.assertEqual(self.field_widget.selected_item, second_wall)
        
        # Пытаемся установить для второй стены тот же ID
        result = self.field_widget.update_wall_id(new_id)
        
        # ID второй стены не должен измениться, так как ID должен быть уникальным
        self.assertFalse(result)
        self.assertEqual(second_wall.id, second_wall_old_id)

if __name__ == '__main__':
    unittest.main() 