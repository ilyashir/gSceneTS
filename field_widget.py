from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsEllipseItem, QInputDialog, QGraphicsPixmapItem, QGraphicsTextItem,
    QGraphicsItemGroup, QGraphicsItem, QMessageBox
)
from PyQt6.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QImage, QTransform
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal
from PyQt6.QtSvg import QSvgRenderer
from robot import Robot
from wall import Wall
from region import Region

import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FieldWidget(QGraphicsView):
    # Сигнал для передачи координат мыши
    mouse_coords_updated = pyqtSignal(float, float)
     # Сигнал для обновления полей ввода
    update_size_fields = pyqtSignal(int, int)

    def __init__(self, properties_window):
        super().__init__()
        self.properties_window = properties_window

        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        
        self.grid_size = 50 # размер графической сетки
        self.snap_to_grid_enabled = True  # Привязка к сетке включена по умолчанию

        self.drawing_mode = None
        self.edit_mode = False
        self.selected_item = None
        self.selected_marker = None
        
        self.temp_wall = None
        self.wall_start = None  # Добавляем инициализацию wall_start

        self.region_start = None  # Начальная точка региона
        self.temp_region = None  # Временный прямоугольник для отрисовки региона
        
        # Состояния объектов
        self.walls = []
        self.regions = []
        self.robot_position = None
        self.dragging_robot = False
        self.robot_offset = QPointF()
        self.scene_width = 800
        self.scene_height = 600

        # Создаем группы для слоев
        self.grid_layer = QGraphicsItemGroup()
        self.axes_layer = QGraphicsItemGroup()
        self.objects_layer = QGraphicsItemGroup()

        self.scene().addItem(self.grid_layer)
        self.scene().addItem(self.axes_layer)
        self.scene().addItem(self.objects_layer)

        self.draw_grid()
        self.draw_axes()
        self.set_robot(QPointF(0, 0))  # Робот по умолчанию в (0, 0)

    # отрисовка сетки
    def draw_grid(self):
        for x in range(-self.scene_width // 2, self.scene_width // 2, self.grid_size):
            line = QGraphicsLineItem(x, -self.scene_height // 2, x, self.scene_height // 2)
            line.setPen(QPen(Qt.GlobalColor.lightGray, 1, Qt.PenStyle.DotLine))
            line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.grid_layer.addToGroup(line)
            logger.debug(f"Added grid line at x={x}")

        for y in range(-self.scene_height // 2, self.scene_height // 2, self.grid_size):
            line = QGraphicsLineItem(-self.scene_width // 2, y, self.scene_width // 2, y)
            line.setPen(QPen(Qt.GlobalColor.lightGray, 1, Qt.PenStyle.DotLine))
            line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.grid_layer.addToGroup(line)
            logger.debug(f"Added grid line at y={y}")
    # отрисовка осей
    def draw_axes(self):
        logger.debug("Drawing axes...")
        # Ось X
        x_axis = QGraphicsLineItem(-self.scene_width // 2, 0, self.scene_width // 2, 0)
        x_axis.setPen(QPen(Qt.GlobalColor.black, 2))
        x_axis.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        x_axis.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(x_axis)
        logger.debug("Added X axis")

        # Ось Y (направлена вниз)
        y_axis = QGraphicsLineItem(0, -self.scene_height // 2, 0, self.scene_height // 2)
        y_axis.setPen(QPen(Qt.GlobalColor.black, 2))
        y_axis.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        y_axis.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(y_axis)
        logger.debug("Added Y axis")

        # Стрелки на осях
        arrow_size = 10
        x_arrow = QGraphicsLineItem(self.scene_width // 2 - arrow_size, -arrow_size, self.scene_width // 2, 0)
        x_arrow.setPen(QPen(Qt.GlobalColor.black, 2))
        x_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        x_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(x_arrow)

        x_arrow = QGraphicsLineItem(self.scene_width // 2 - arrow_size, arrow_size, self.scene_width // 2, 0)
        x_arrow.setPen(QPen(Qt.GlobalColor.black, 2))
        x_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        x_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(x_arrow)

        y_arrow = QGraphicsLineItem(-arrow_size, self.scene_height // 2 - arrow_size, 0, self.scene_height // 2)
        y_arrow.setPen(QPen(Qt.GlobalColor.black, 2))
        y_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        y_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(y_arrow)

        y_arrow = QGraphicsLineItem(arrow_size, self.scene_height // 2 - arrow_size, 0, self.scene_height // 2)
        y_arrow.setPen(QPen(Qt.GlobalColor.black, 2))
        y_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        y_arrow.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(y_arrow)

        # Обозначения осей
        x_label = QGraphicsTextItem("X")
        x_label.setPos(self.scene_width // 2 - 20, 10)
        x_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        x_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(x_label)

        y_label = QGraphicsTextItem("Y")
        y_label.setPos(-20, self.scene_height // 2 - 20)
        y_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        y_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(y_label)
        logger.debug("Drawing axes success")

    def cut_coords(self, x, y):
        if x > self.scene_width / 2:
            x = self.scene_width / 2
        if x < -self.scene_width / 2:
            x = -self.scene_width / 2    
        if y > self.scene_height / 2:
            y = self.scene_height / 2
        if y < -self.scene_height / 2:
            y = -self.scene_height / 2  
        return x, y    

    def snap_to_grid(self, pos):
        if self.snap_to_grid_enabled:
            x = round(pos.x() / self.grid_size) * self.grid_size
            y = round(pos.y() / self.grid_size) * self.grid_size
            x, y = self.cut_coords(x, y)       
            return QPointF(x, y)
        x, y = self.cut_coords(pos.x(), pos.y())       
        return QPointF(x, y)
    
    def select_item(self, item):
        """Выделяет объект жёлтым контуром."""
        print(type(self.selected_item))
        if self.selected_item:
            print("Снимаем выделение с объекта", type(self.selected_item))
            self.deselect_item()  # Снимаем выделение с предыдущего объекта

        if isinstance(item, (Wall, Robot, Region)):
            print("Выделение объекта", type(item))
            self.selected_item = item
            self.selected_item.set_highlight(True)  # Включаем подсветку
            self.properties_window.update_properties(item)  # Обновляем свойства

    def deselect_item(self):
        """Снимает выделение с объекта."""
        if self.selected_item:
            if isinstance(self.selected_item, (Wall, Robot, Region)):
                self.selected_item.set_highlight(False)  # Возвращаем стандартный контур
            self.selected_item = None
            self.properties_window.clear_properties()  # Очищаем свойства
    
    def wall_intersects_robot(self, start, end):
        """
        Проверяет, пересекает ли стена робота.
        """
        if not self.robot_position:
            return False
        # Линия стены
        wall_line = QLineF(start, end)
        # Прямоугольник робота
        robot_rect = self.robot_position.boundingRect()
        robot_rect.translate(self.robot_position.pos())
        # Проверяем пересечение линии стены с прямоугольником робота
        return self.line_intersects_rect(wall_line, robot_rect)
    
    def line_intersects_rect(self, line, rect):
        """
        Проверяет, пересекает ли линия прямоугольник.
        :param line: Линия (QLineF).
        :param rect: Прямоугольник (QRectF).
        :return: True, если линия пересекает прямоугольник, иначе False.
        """
        # Получаем стороны прямоугольника
        top = QLineF(rect.topLeft(), rect.topRight())
        right = QLineF(rect.topRight(), rect.bottomRight())
        bottom = QLineF(rect.bottomLeft(), rect.bottomRight())
        left = QLineF(rect.topLeft(), rect.bottomLeft())

        # Проверяем пересечение линии с каждой стороной прямоугольника
        for side in [top, right, bottom, left]:
            intersection_type, intersection_point = line.intersects(side)
            if intersection_type == QLineF.IntersectionType.BoundedIntersection:
                return True  # Линия пересекает прямоугольник

        # Проверяем, находится ли один из концов линии внутри прямоугольника
        if rect.contains(line.p1()) or rect.contains(line.p2()):
            return True

        return False  # Линия не пересекает прямоугольник

    def add_wall(self, start, end):
        logger.debug(f"Adding wall from {start} to {end}")
        if self.wall_intersects_robot(start,end):
            logger.debug(f"ERR robot intersects")
            return False
        wall = Wall(start, end)
        self.objects_layer.addToGroup(wall)
        self.walls.append(wall)
        self.select_item(wall)         

    def add_region(self, start, end):
        """
        Добавляет регион на сцену.
        :param start: Начальная точка (QPointF).
        :param end: Конечная точка (QPointF).
        """
        rect = QRectF(start, end).normalized()
        width = rect.width()
        height = rect.height()
        logger.debug(f"Adding region at {rect.topLeft()} with width={width}, height={height}")

        region = Region(rect.topLeft(), width, height)
        self.objects_layer.addToGroup(region)
        self.regions.append(region)
        self.select_item(region) 
        logger.debug(f"Region added: {region}")


    def set_robot(self, pos):
        logger.debug(f"Setting robot position to {pos}")
        if self.robot_position is not None:
            logger.debug("Removing existing robot from scene")
            self.scene().removeItem(self.robot_position)
        self.robot_position = Robot(pos)
        self.objects_layer.addToGroup(self.robot_position)

    def set_drawing_mode(self, mode):
        self.drawing_mode = mode

    def set_edit_mode(self, enabled):
        self.edit_mode = enabled

    def set_scene_size(self, width, height):
        logger.debug(f"Setting scene size to width={width}, height={height}")

        # Проверка, влезают ли объекты
        if not self.check_objects_within_bounds(width, height):
            logger.warning("Objects do not fit in the new scene size.")
            # Выводим уведомление, если объекты не влезают
            QMessageBox.warning(
                None,
                "Ошибка",
                f"При новом размере объекты вылезут за границу сцены. Пожалуйста, выберите другой размер.",
                QMessageBox.StandardButton.Ok
            )
            self.update_size_fields.emit(self.scene_width, self.scene_height)
            return

        # Убираем старую сетку со сцены
        for item in self.grid_layer.childItems():
            self.grid_layer.removeFromGroup(item)
            self.scene().removeItem(item)  # Удаляем элементы из сцены

        # Убираем старые оси координат со сцены
        for item in self.axes_layer.childItems():
            self.axes_layer.removeFromGroup(item)
            self.scene().removeItem(item)  # Удаляем элементы из сцены    

        # Обновляем размеры сцены
        self.scene_width = width
        self.scene_height = height
        logger.debug(f"Updated scene dimensions: width={self.scene_width}, height={self.scene_height}")

        logger.debug("Drawing grid and axes...")
        self.draw_grid()
        self.draw_axes()

        logger.debug("Scene size updated successfully.") 

    def check_objects_within_bounds(self, width, height):
        for wall in self.walls:
            if (wall.line().x1() < -width // 2 or wall.line().x2() > width // 2 or
                wall.line().y1() < -height // 2 or wall.line().y2() > height // 2):
                return False

        for region in self.regions:
            if (region.rect().x() < -width // 2 or region.rect().x() + region.rect().width() > width // 2 or
                region.rect().y() < -height // 2 or region.rect().y() + region.rect().height() > height // 2):
                return False

        return True
    
    def is_point_within_scene(self, point):
        """
        Проверяет, находится ли точка в пределах сцены.
        :param point: Точка (QPointF).
        :return: True, если точка находится в пределах сцены, иначе False.
        """
        return (
            -self.scene_width / 2 <= point.x() <= self.scene_width / 2 and
            -self.scene_height / 2 <= point.y() <= self.scene_height / 2
        )
    
    def mousePressEvent(self, event):
        posOriginal = self.mapToScene(event.pos()) # оригинальные координаты
        pos = self.snap_to_grid(posOriginal) # координаты с привязкой к сетке

        item = self.scene().itemAt(posOriginal, self.transform())
        print("click", type(item))
        if event.button() == Qt.MouseButton.LeftButton:
            logger.debug("click left button")
            
            if item and isinstance(item, (Robot, Region)) :
                # print("Время выделять, а сейчас активный", type(self.selected_item))
                self.select_item(item)  # Выделяем объект
            elif item and item.data(0) == "its_wall":
                self.select_item(item.parentItem())  # Выделяем объект
            else:
                self.deselect_item()

            if self.edit_mode:
                if item == self.robot_position:  # Перетаскивание робота
                    self.dragging_robot = True
                    self.robot_offset = pos - self.robot_position.pos()
                    return
                elif item and item.data(0) == "wall_marker":  # Проверяем свойство
                    self.selected_marker = item
                return

            if self.drawing_mode == "wall":
                # if not self.is_point_within_scene(pos):
                #     if self.wall_start:
                #        self.wall_start = None
                #     if self.temp_wall:
                #         self.scene().removeItem(self.temp_wall)
                #         self.temp_wall = None

                #     return    
                if self.wall_start is None:
                    self.wall_start = pos  # Устанавливаем начальную точку стены
                else:
                    self.add_wall(self.wall_start, pos)  # Добавляем стену
                    self.wall_start = None  # Сбрасываем начальную точку
                    if self.temp_wall:
                        self.scene().removeItem(self.temp_wall)
                        self.temp_wall = None

            elif self.drawing_mode == "region":
                if self.region_start is None:
                    # Первый клик: устанавливаем начальную точку
                    self.region_start = pos
                    logger.debug(f"Region start: {self.region_start}")
                else:
                    # Второй клик: создаем регион
                    self.add_region(self.region_start, pos)
                    self.region_start = None  # Сбрасываем начальную точку
                    if self.temp_region:
                        self.scene().removeItem(self.temp_region)
                        self.temp_region = None
    
    def mouseMoveEvent(self, event):
        posOriginal = self.mapToScene(event.pos()) # оригинальные координаты
        pos = self.snap_to_grid(posOriginal) # координаты с привязкой к сетке
        
        # Отправляем сигнал с координатами        
        self.mouse_coords_updated.emit(posOriginal.x(), posOriginal. y())
        
        if self.dragging_robot:
            logger.debug(f"Dragging robot to {pos}")
            # pos = self.snap_to_grid(self.mapToScene(event.pos()))
            self.robot_position.setPos(pos - self.robot_offset)  # Перемещение робота
            return
        
        if self.edit_mode and self.selected_marker:            
            
            wall = self.selected_marker.parentItem()
            if self.selected_marker == wall.start_marker:
                if self.wall_intersects_robot(pos, QPointF(wall.line().x2(), wall.line().y2())):
                    logger.debug(f"ERR robot intersects")
                    return 
                else:
                    wall.setLine(pos.x(), pos.y(), wall.line().x2(), wall.line().y2())                
            else:
                if self.wall_intersects_robot(QPointF(wall.line().x1(), wall.line().y1()), pos):
                    logger.debug(f"ERR robot intersects")
                    return 
                else:                    
                    wall.setLine(wall.line().x1(), wall.line().y1(), pos.x(), pos.y())
            self.selected_marker.setRect(QRectF(pos.x() - 5, pos.y() - 5, 10, 10))        
            wall.update_brick_rect()    
            return
        elif self.edit_mode and self.selected_item == self.robot_position:
            self.robot_position.setPos(pos)  # Перемещаем робота
            self.properties_window.update_properties(self.robot_position)  # Обновляем свойства
            return

        if self.drawing_mode == "wall" and self.wall_start:
            if self.temp_wall:
                self.scene().removeItem(self.temp_wall)
            self.temp_wall = QGraphicsLineItem(self.wall_start.x(), self.wall_start.y(), pos.x(), pos.y())
            self.temp_wall.setPen(QPen(Qt.GlobalColor.gray, 10))
            self.scene().addItem(self.temp_wall)
        elif self.drawing_mode == "region" and self.region_start:
            # Логика для отрисовки временного региона
            if self.temp_region:
                self.scene().removeItem(self.temp_region)
            # Создаем временный прямоугольник
            rect = QRectF(self.region_start, pos).normalized()
            self.temp_region = QGraphicsRectItem(rect)
            self.temp_region.setPen(QPen(Qt.GlobalColor.gray, 2, Qt.PenStyle.DashLine))
            self.temp_region.setBrush(QBrush(Qt.GlobalColor.transparent))
            self.scene().addItem(self.temp_region)   

        super().mouseMoveEvent(event)    

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging_robot:
                self.dragging_robot = False
            elif self.edit_mode:
                self.selected_marker = None
            elif self.drawing_mode == "region" and self.temp_region:
                self.scene().removeItem(self.temp_region)
                self.temp_region = None
