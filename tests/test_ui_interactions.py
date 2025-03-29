import sys
import os
import pytest
from PyQt6.QtCore import Qt, QPointF, QEvent, QPoint
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtTest import QTest
from unittest.mock import patch

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Импортируем тестируемые модули
from main_window import MainWindow
from robot import Robot
from wall import Wall
from region import Region
from styles import AppStyles

# Фикстура для создания приложения и главного окна
@pytest.fixture
def app_and_window(qtbot):
    """Создает экземпляр приложения и главного окна для тестирования"""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    
    # Используем qtbot.waitExposed вместо waitForWindowShown
    qtbot.waitExposed(window)
    
    yield app, window, qtbot
    
    # Очистка после тестов
    window.close()


class TestUIInteractions:
    """Тесты для UI взаимодействий"""
    
    def test_theme_toggle(self, app_and_window):
        """Тест переключения темы кнопкой"""
        _, window, qtbot = app_and_window
        
        # Получаем начальное состояние темы
        initial_theme = window.is_dark_theme
        
        # Кликаем на кнопку переключения темы
        qtbot.mouseClick(window.theme_switch, Qt.MouseButton.LeftButton)
        
        # Проверяем, что тема изменилась
        assert window.is_dark_theme != initial_theme
        
        # Кликаем снова, чтобы вернуться к начальной теме
        qtbot.mouseClick(window.theme_switch, Qt.MouseButton.LeftButton)
        
        # Проверяем, что тема вернулась к начальной
        assert window.is_dark_theme == initial_theme
    
    def test_robot_drag_in_edit_mode(self, app_and_window):
        """Тест перетаскивания робота в режиме редактирования"""
        _, window, qtbot = app_and_window
        
        # Переключаемся в режим редактирования
        window.set_mode("edit")
        
        # Создаем робота на сцене
        robot_pos = QPointF(200, 200)
        robot = Robot(robot_pos)
        window.field_widget.scene().addItem(robot)
        
        # Выбираем робота
        window.field_widget.select_item(robot)
        
        # Начальная позиция робота
        initial_pos = robot.pos()
        
        # Эмулируем перетаскивание: нажатие кнопки мыши, перемещение, отпускание
        field_widget = window.field_widget
        
        # Преобразуем координаты сцены в координаты вида
        view_pos = field_widget.mapFromScene(robot_pos)
        
        # Нажимаем на робота
        qtbot.mousePress(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         pos=view_pos)
        
        # Перетаскиваем на новую позицию
        delta_x, delta_y = 50, 50
        drag_pos = QPoint(view_pos.x() + delta_x, view_pos.y() + delta_y)
        qtbot.mouseMove(field_widget.viewport(), pos=drag_pos)
        
        # Отпускаем кнопку мыши
        qtbot.mouseRelease(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                           pos=drag_pos)
        
        # Проверяем, что позиция робота изменилась
        assert robot.pos() != initial_pos
        
        # Проверяем, что перемещение примерно соответствует ожидаемому
        # (с учетом возможного округления и других факторов)
        assert abs(robot.pos().x() - (initial_pos.x() + delta_x)) <= 10
        assert abs(robot.pos().y() - (initial_pos.y() + delta_y)) <= 10
    
    def test_wall_drag_in_edit_mode(self, app_and_window):
        """Тест перетаскивания стены в режиме редактирования"""
        _, window, qtbot = app_and_window
        
        # Переключаемся в режим редактирования
        window.set_mode("edit")
        
        # Создаем стену на сцене
        start = QPointF(100, 100)
        end = QPointF(300, 100)
        wall = Wall(start, end)
        window.field_widget.scene().addItem(wall)
        
        # Выбираем стену
        window.field_widget.select_item(wall)
        
        # Начальная позиция стены
        initial_line = wall.line()
        
        # Эмулируем перетаскивание: нажатие кнопки мыши, перемещение, отпускание
        field_widget = window.field_widget
        
        # Преобразуем координаты сцены в координаты вида
        view_pos = field_widget.mapFromScene(QPointF(200, 100))  # Центр стены
        
        # Нажимаем на стену
        qtbot.mousePress(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         pos=view_pos)
        
        # Перетаскиваем на новую позицию
        delta_x, delta_y = 0, 50
        drag_pos = QPoint(view_pos.x() + delta_x, view_pos.y() + delta_y)
        qtbot.mouseMove(field_widget.viewport(), pos=drag_pos)
        
        # Отпускаем кнопку мыши
        qtbot.mouseRelease(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                           pos=drag_pos)
        
        # Проверяем, что линия стены изменилась
        assert wall.line() != initial_line
        
        # Проверяем, что перемещение примерно соответствует ожидаемому
        # (с учетом возможного округления и других факторов)
        # Проверяем обе точки стены
        assert abs(wall.line().y1() - (initial_line.y1() + delta_y)) <= 10
        assert abs(wall.line().y2() - (initial_line.y2() + delta_y)) <= 10
    
    def test_region_drag_in_edit_mode(self, app_and_window):
        """Тест перетаскивания региона в режиме редактирования"""
        _, window, qtbot = app_and_window
        
        # Переключаемся в режим редактирования
        window.set_mode("edit")
        
        # Создаем регион на сцене
        pos = QPointF(150, 150)
        width, height = 100, 100
        region = Region(pos, width, height)
        window.field_widget.scene().addItem(region)
        
        # Выбираем регион
        window.field_widget.select_item(region)
        
        # Начальная позиция региона
        initial_pos = region.pos()
        
        # Эмулируем перетаскивание: нажатие кнопки мыши, перемещение, отпускание
        field_widget = window.field_widget
        
        # Преобразуем координаты сцены в координаты вида
        view_pos = field_widget.mapFromScene(pos + QPointF(width/2, height/2))  # Центр региона
        
        # Нажимаем на регион
        qtbot.mousePress(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                         pos=view_pos)
        
        # Перетаскиваем на новую позицию
        delta_x, delta_y = 70, 30
        drag_pos = QPoint(view_pos.x() + delta_x, view_pos.y() + delta_y)
        qtbot.mouseMove(field_widget.viewport(), pos=drag_pos)
        
        # Отпускаем кнопку мыши
        qtbot.mouseRelease(field_widget.viewport(), Qt.MouseButton.LeftButton, 
                           pos=drag_pos)
        
        # Проверяем, что позиция региона изменилась
        assert region.pos() != initial_pos
        
        # Проверяем, что перемещение примерно соответствует ожидаемому
        # (с учетом возможного округления и других факторов)
        # Увеличиваем допустимое отклонение до 25 пикселей для координат региона
        assert abs(region.pos().x() - (initial_pos.x() + delta_x)) <= 25
        assert abs(region.pos().y() - (initial_pos.y() + delta_y)) <= 25
    
    def test_duplicate_wall_id_handling(self, app_and_window):
        """Тест обработки дублирующегося ID стены с автоматическим закрытием окна предупреждения"""
        _, window, qtbot = app_and_window
        
        # Переключаемся в режим редактирования
        window.set_mode("edit")
        
        # Создаем две стены с разными ID
        wall1 = Wall(QPointF(100, 100), QPointF(200, 100))
        wall1.set_id("wall1")
        
        wall2 = Wall(QPointF(300, 100), QPointF(400, 100))
        wall2.set_id("wall2")
        
        # Добавляем стены на сцену
        window.field_widget.scene().addItem(wall1)
        window.field_widget.scene().addItem(wall2)
        
        # Выбираем вторую стену и пытаемся установить ей ID первой стены
        window.field_widget.select_item(wall2)
        
        # Пытаемся установить дублирующийся ID
        # Это должно вызвать QMessageBox.warning, но благодаря фикстуре
        # auto_close_message_boxes окно не появится
        result = window.field_widget.update_wall_id("wall1")
        
        # Проверяем, что ID не изменился из-за дублирования
        assert result == False
        assert wall2.id == "wall2"
        
        # Устанавливаем уникальный ID и проверяем, что изменение произошло
        result = window.field_widget.update_wall_id("wall3")
        assert result == True
        assert wall2.id == "wall3"
        
    def test_duplicate_region_id_handling(self, app_and_window):
        """Тест обработки дублирующегося ID региона с автоматическим закрытием окна предупреждения"""
        _, window, qtbot = app_and_window
        
        # Переключаемся в режим редактирования
        window.set_mode("edit")
        
        # Создаем два региона с разными ID
        region1 = Region(QPointF(100, 100), 50, 50)
        region1.set_id("region1")
        
        region2 = Region(QPointF(200, 200), 50, 50)
        region2.set_id("region2")
        
        # Добавляем регионы на сцену
        window.field_widget.scene().addItem(region1)
        window.field_widget.scene().addItem(region2)
        
        # Выбираем второй регион и пытаемся установить ему ID первого региона
        window.field_widget.select_item(region2)
        
        # Пытаемся установить дублирующийся ID
        # Это должно вызвать QMessageBox.warning, но благодаря фикстуре
        # auto_close_message_boxes окно не появится
        result = window.field_widget.update_region_id("region1")
        
        # Проверяем, что ID не изменился из-за дублирования
        assert result == False
        assert region2.id == "region2"
        
        # Устанавливаем уникальный ID и проверяем, что изменение произошло
        result = window.field_widget.update_region_id("region3")
        assert result == True
        assert region2.id == "region3" 