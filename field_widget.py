from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsItemGroup, QGraphicsItem, QMessageBox, QInputDialog,
    QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsPathItem
)
from PyQt6.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QImage, QTransform, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal, pyqtSlot, QThread, QTimer, QDataStream, QIODevice, QByteArray
from PyQt6.QtSvg import QSvgRenderer
from robot import Robot
from wall import Wall
from region import Region
from start_position import StartPosition
from styles import AppStyles
from hover_highlight import HoverHighlightMixin
# Импортируем утилитные функции
from utils.geometry_utils import (distance_to_line, line_intersects_rect, 
                                  line_with_thickness_intersects_rect, snap_to_grid)

import logging
from math import sqrt, sin, cos, atan2, degrees, radians, pi
from collections import defaultdict

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FieldWidget(QGraphicsView):
    # Сигнал для передачи координат мыши
    mouse_coords_updated = pyqtSignal(float, float)
    # Сигнал для обновления полей ввода
    update_size_fields = pyqtSignal(int, int)
    # Сигнал для выбора объекта
    item_selected = pyqtSignal(object)
    # Сигнал для снятия выделения с объекта
    item_deselected = pyqtSignal()
    # Сигнал для обновления свойств объекта
    properties_updated = pyqtSignal(object)
    # Сигнал изменения режима привязки к сетке
    grid_snap_changed = pyqtSignal(bool)

    def __init__(self, properties_window, scene_width=1300, scene_height=800, grid_size=50):
        super().__init__()
        self.properties_window = properties_window

        # Подключаем сигналы к слотам
        self.item_selected.connect(self.properties_window.update_properties)
        self.item_deselected.connect(self.properties_window.clear_properties)
        self.properties_updated.connect(self.properties_window.update_properties)

        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        
        # Применяем стиль из styles.py
        self.setStyleSheet(AppStyles.get_scene_style(True))
        
        # Белый фон для сцены
        self.scene().setBackgroundBrush(QBrush(QColor("white")))
        
        # Создаем слои для элементов сцены
        self.grid_layer = QGraphicsItemGroup()
        self.axes_layer = QGraphicsItemGroup()
        self.objects_layer = QGraphicsItemGroup()
        
        # Отключаем перехват событий для слоя объектов,
        # чтобы события проходили к дочерним элементам (роботу, стенам и т.д.)
        # В PyQt6 используется другой метод:
        self.objects_layer.setFiltersChildEvents(False)
        
        # Устанавливаем z-index для слоев
        self.grid_layer.setZValue(0)
        self.axes_layer.setZValue(1)
        self.objects_layer.setZValue(2)
        
        # Добавляем слои в сцену в правильном порядке
        self.scene().addItem(self.grid_layer)
        self.scene().addItem(self.axes_layer)
        self.scene().addItem(self.objects_layer)
        
        self.grid_size = grid_size  # размер графической сетки из конфигурации
        self.snap_to_grid_enabled = True  # Привязка к сетке включена по умолчанию

        self.drawing_mode = None
        self.edit_mode = False
        self.selected_item = None
        self.selected_marker = None
        
        self.temp_wall = None
        self.wall_start = None  # Начальная точка стены

        self.region_start = None  # Начальная точка региона
        self.temp_region = None  # Временный прямоугольник для отрисовки региона
        
        # Состояния объектов
        self.walls = []
        self.regions = []
        self.robot_model = None
        self.start_position_model = None  
        self.dragging_robot = False
        self.robot_offset = QPointF()
        self.scene_width = scene_width  # размеры сцены из конфигурации
        self.scene_height = scene_height

        # Инициализация масштаба
        self._scale_factor = 1.0
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._scale_step = 0.5

        # Ссылка на менеджер скроллбаров, который будет установлен из main_window.py
        self._scroll_manager = None

        self.draw_grid()
        self.draw_axes()
        self.init_robot(QPointF(0, 0))  # Робот по умолчанию в (0, 0)
        self.init_start_position(QPointF(25, 25))  # Стартовая позиция по умолчанию
        
        # Устанавливаем размер сцены
        self.scene().setSceneRect(-self.scene_width/2, -self.scene_height/2, self.scene_width, self.scene_height)

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
        y_label.setPos(-25, self.scene_height // 2 - 20)
        y_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        y_label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.axes_layer.addToGroup(y_label)
        logger.debug("Drawing axes success")

    def snap_to_grid(self, pos):
        return snap_to_grid(pos, self.grid_size, self.snap_to_grid_enabled, self.scene_width, self.scene_height)
    
    def select_item(self, item):
        """Выделяет объект"""
        # Проверяем, не выделяем ли тот же объект
        logger.debug(f"Selecting item: {item}, а был выделен {self.selected_item}")
        if item == self.selected_item:
            logger.debug(f"Item {item} is already selected, skipping")
            return
        
        if self.selected_item:
            self.deselect_item()

        if isinstance(item, (Wall, Robot, Region, StartPosition)):
            logger.debug(f"Selecting item: {item}")
            self.selected_item = item
            
            # Если это объект с поддержкой HoverHighlightMixin, отключаем hover_highlight
            if isinstance(item, HoverHighlightMixin) and item._is_hovered:
                logger.debug(f"Disabling hover highlight for selected item")
                item.set_hover_highlight(False)
                
            # Активируем выделение объекта
            self.selected_item.set_highlight(True)
            self.item_selected.emit(item)
            
    def deselect_item(self):
        """Снимает выделение с объекта."""
        if self.selected_item:
            logger.debug(f"Deselecting item: {self.selected_item}")
            if isinstance(self.selected_item, (Wall, Robot, Region, StartPosition)):
                self.selected_item.set_highlight(False)
                
                # Восстанавливаем подсветку при наведении, если мышь всё ещё над объектом
                if isinstance(self.selected_item, HoverHighlightMixin) and self.selected_item._is_hovered:
                    logger.debug(f"Restoring hover highlight after deselection")
                    self.selected_item.set_hover_highlight(True)
                
            self.selected_item = None
            self.item_deselected.emit()
    
    def wall_intersects_robot(self, x1, y1, x2, y2, thickness=None):
        """
        Проверяет, пересекается ли стена с роботом.
        
        Args:
            x1, y1: Координаты первой точки стены
            x2, y2: Координаты второй точки стены
            thickness: Толщина стены (если None, будет использовано значение по умолчанию)
            
        Returns:
            bool: True, если стена пересекается с роботом, False в противном случае
        """
        if not self.robot_model: 
            return False
            
        robot_rect = self.robot_model.boundingRect()
        # Учитываем позицию робота при проверке пересечения
        robot_rect.translate(self.robot_model.pos())
        
        # Линия стены
        wall_line = QLineF(QPointF(x1, y1), QPointF(x2, y2))
        
        # Если толщина не указана, получаем её из временной стены
        if thickness is None:
            # Создаем временную стену для определения толщины линии
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2), is_temp=True)
            thickness = temp_wall.stroke_width
        
        # Проверяем пересечение линии стены с прямоугольником робота с учетом толщины
        # Используем утилитарную функцию
        return line_with_thickness_intersects_rect(wall_line, robot_rect, thickness)
    
    def add_wall(self, p1, p2, wall_id=None):
        """
        Добавляет стену на сцену с заданными координатами и идентификатором.
        
        Args:
            p1: Начальная точка стены (QPointF)
            p2: Конечная точка стены (QPointF)
            wall_id: Идентификатор стены (если None, будет сгенерирован)
            
        Returns:
            Wall: Добавленная стена или None, если добавление не удалось
        """
        logger.debug(f"Добавление стены: {p1} - {p2}, id={wall_id}")
        
        # Создаем новую стену сначала для получения толщины
        temp_wall = Wall(p1, p2, wall_id=None, is_temp=True)
        
        # Проверяем пересечение с роботом, передавая толщину стены
        if self.wall_intersects_robot(p1.x(), p1.y(), p2.x(), p2.y(), thickness=temp_wall.stroke_width):
            logger.warning("Стена пересекается с роботом - отмена добавления")
            return None
            
        # Создаем новую стену для добавления на сцену
        wall = Wall(p1, p2, wall_id)
        wall_id = wall.id  # Сохраняем ID для возможной очистки
        
        # Проверяем, находится ли стена в пределах сцены
        if not self.check_object_within_scene(wall):
            logger.warning("Стена выходит за границы сцены - отмена добавления")
            # Очищаем ID, так как стена не будет добавлена
            Wall._existing_ids.remove(wall_id)
            return None
            
        # Добавляем стену на сцену
        self.objects_layer.addToGroup(wall)
        self.walls.append(wall)
        
        # Настраиваем обработку событий для стены
        wall.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        wall.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        logger.debug(f"Стена успешно добавлена с id={wall.id}")
        
        # Автоматически выделяем созданную стену
        self.select_item(wall)         

        return wall
        
    def add_region(self, rect_or_points, region_id=None, color=None):
        """
        Добавляет новый регион на сцену.
        
        Args:
            rect_or_points: Прямоугольник (QRectF) или список точек для создания региона
            region_id: Идентификатор региона (опционально)
            color: Цвет заливки региона (опционально)
            
        Returns:
            Region: Добавленный регион или None, если добавление не удалось
        """
        logger.debug(f"Добавление региона: {rect_or_points}, id={region_id}, color={color}")
        
        # Проверяем, что за тип передан
        if isinstance(rect_or_points, QRectF):
            # Извлекаем позицию и размеры из прямоугольника
            x = rect_or_points.x()
            y = rect_or_points.y()
            width = rect_or_points.width()
            height = rect_or_points.height()
            
            # Создаем точки для региона используя (0,0) как базовую точку
            # Потом мы установим позицию региона, чтобы правильно расположить его
            points = [
                QPointF(0, 0),
                QPointF(width, 0),
                QPointF(width, height),
                QPointF(0, height)
            ]
            
            # Создаем новый регион
            region = Region(points, region_id, color=color if color else "#800000ff")
            
            # Устанавливаем позицию региона
            region.setPos(x, y)
        elif isinstance(rect_or_points, list):
            # Список точек напрямую передается в конструктор Region
            region = Region(rect_or_points, region_id, color=color if color else "#800000ff")
        else:
            logger.error(f"Неподдерживаемый тип для создания региона: {type(rect_or_points)}")
            return None
        
        # Проверяем, находится ли регион в пределах сцены
        if not self.check_object_within_scene(region):
            logger.warning("Регион выходит за границы сцены - отмена добавления")
            
            # Освобождаем ID региона, если он был создан
            try:
                if region.id in Region._existing_ids:
                    Region._existing_ids.remove(region.id)
                    logger.debug(f"Освободили ID {region.id} неудачно созданного региона")
            except Exception as e:
                logger.debug(f"Ошибка при освобождении ID: {e}")
                
            return None
            
        # Добавляем регион на сцену через слой объектов
        self.objects_layer.addToGroup(region)
        
        # Сохраняем ссылку на регион в списке для быстрого доступа
        self.regions.append(region)
        
        # Настраиваем обработку событий для региона
        region.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        region.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        logger.debug(f"Регион успешно добавлен с id={region.id}")
        
        # Автоматически выделяем созданный регион
        self.select_item(region) 

        return region

    def init_robot(self, pos):
        logger.debug(f"Setting robot position to {pos}")
        # Проверяем, находится ли робот в пределах сцены
        temp_robot = Robot(pos)
        if not self.check_object_within_scene(temp_robot):
            logger.warning(f"Robot position {pos} is out of bounds - using default position (0, 0)")
            pos = QPointF(0, 0)
            
        if self.robot_model is not None:
            logger.debug("Removing existing robot from scene")
            self.scene().removeItem(self.robot_model)
        self.robot_model = Robot(pos)
        self.objects_layer.addToGroup(self.robot_model)
    
    def init_start_position(self, pos, direction=0):
        """
        Инициализирует стартовую позицию робота на сцене.
        
        Args:
            pos: Позиция стартовой позиции (QPointF)
            direction: Начальное направление стартовой позиции
        """
        logger.debug(f"Setting start position to {pos}, direction: {direction}")
        if self.start_position_model is not None:
            logger.debug("Removing existing start position from scene")
            self.scene().removeItem(self.start_position_model)
        self.start_position_model = StartPosition(pos, direction)
        self.objects_layer.addToGroup(self.start_position_model)

    def set_drawing_mode(self, mode):
        # Если меняем режим рисования, снимаем выделение с текущего объекта
        if mode != self.drawing_mode:
            if self.selected_item:
                self.deselect_item()
        
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
        
        # Обновляем размер сцены
        self.scene().setSceneRect(-self.scene_width/2, -self.scene_height/2, self.scene_width, self.scene_height)

        # Обновляем видимость скроллбаров после изменения размера сцены
        self.update_scrollbars_visibility()

        logger.debug("Scene size updated successfully.") 
        logger.debug(f"Scene size set to: {width}x{height}")

    def update_scrollbars_visibility(self):
        """Обновляет видимость скроллбаров в зависимости от размера сцены и текущего масштаба"""
        if hasattr(self, '_scroll_manager') and self._scroll_manager:
            # Вызываем метод из менеджера, который сначала проверит необходимость скроллбаров
            # и затем покажет только те, которые нужны
            self._scroll_manager._showScrollbars()

    def redraw_grid(self):
        """Перерисовывает сетку и оси"""
        # Убираем старую сетку со сцены
        for item in self.grid_layer.childItems():
            self.grid_layer.removeFromGroup(item)
            self.scene().removeItem(item)  # Удаляем элементы из сцены

        # Убираем старые оси координат со сцены
        for item in self.axes_layer.childItems():
            self.axes_layer.removeFromGroup(item)
            self.scene().removeItem(item)  # Удаляем элементы из сцены    
            
        # Перерисовываем сетку и оси
        self.draw_grid()
        self.draw_axes()
        
        logger.debug("Grid redrawn")

    def check_objects_within_bounds(self, width, height):
        for wall in self.walls:
            if (wall.line().x1() < -width // 2 or wall.line().x2() > width // 2 or
                wall.line().y1() < -height // 2 or wall.line().y2() > height // 2):
                return False

        for region in self.regions:
            rect = region.path().boundingRect()
            pos = region.pos()
            if (pos.x() + rect.x() < -width // 2 or 
                pos.x() + rect.x() + rect.width() > width // 2 or
                pos.y() + rect.y() < -height // 2 or 
                pos.y() + rect.y() + rect.height() > height // 2):
                return False

        if (self.robot_model.pos().x() < -width // 2 or self.robot_model.pos().x() + self.robot_model.boundingRect().width() > width // 2 or
            self.robot_model.pos().y() < -height // 2 or self.robot_model.pos().y() + self.robot_model.boundingRect().height() > height // 2):
                return False
        
        if (self.start_position_model.pos().x() < -width // 2 or self.start_position_model.pos().x() + self.start_position_model.boundingRect().width() > width // 2 or
            self.start_position_model.pos().y() < -height // 2 or self.start_position_model.pos().y() + self.start_position_model.boundingRect().height() > height // 2):
                return False

        return True
    
    def check_object_within_scene(self, item):
        """
        Проверяет, находится ли объект в пределах сцены.
        
        Args:
            item: Объект для проверки
            
        Returns:
            bool: True, если объект в пределах сцены, False в противном случае
        """
        scene_width = self.scene_width
        scene_height = self.scene_height
        
        # Проверяем, является ли элемент стеной
        if isinstance(item, Wall):
            # Для стены проверяем обе точки линии
            line = item.line()
            return (
                -scene_width / 2 <= line.x1() <= scene_width / 2 and
                -scene_height / 2 <= line.y1() <= scene_height / 2 and
                -scene_width / 2 <= line.x2() <= scene_width / 2 and
                -scene_height / 2 <= line.y2() <= scene_height / 2
            )
        
        # Проверяем, является ли элемент регионом
        elif isinstance(item, Region):
            # Для региона проверяем его ограничивающий прямоугольник
            rect = item.boundingRect()
            pos = item.pos()
            
            # Проверяем, что все углы прямоугольника находятся в пределах сцены
            top_left = QPointF(pos.x() + rect.x(), pos.y() + rect.y())
            top_right = QPointF(pos.x() + rect.x() + rect.width(), pos.y() + rect.y())
            bottom_left = QPointF(pos.x() + rect.x(), pos.y() + rect.y() + rect.height())
            bottom_right = QPointF(pos.x() + rect.x() + rect.width(), pos.y() + rect.y() + rect.height())
            
            # Проверяем, что все углы прямоугольника находятся в пределах сцены
            return (
                -scene_width / 2 <= top_left.x() <= scene_width / 2 and
                -scene_height / 2 <= top_left.y() <= scene_height / 2 and
                -scene_width / 2 <= top_right.x() <= scene_width / 2 and
                -scene_height / 2 <= top_right.y() <= scene_height / 2 and
                -scene_width / 2 <= bottom_left.x() <= scene_width / 2 and
                -scene_height / 2 <= bottom_left.y() <= scene_height / 2 and
                -scene_width / 2 <= bottom_right.x() <= scene_width / 2 and
                -scene_height / 2 <= bottom_right.y() <= scene_height / 2
            )
        
        elif isinstance(item, Robot):
            # Для робота проверяем его позицию и размеры
            # Размер робота фиксирован - 50x50 пикселей
            pos = item.pos()
            logger.debug(f"Checking robot position: pos=({pos.x()}, {pos.y()})")
            logger.debug(f"Scene bounds: x=({-scene_width/2}, {scene_width/2}), y=({-scene_height/2}, {scene_height/2})")
            
            # Проверяем, что робот полностью находится в пределах сцены
            # с учетом его размеров (50x50 пикселей)
            # Используем точные размеры робота, а не размеры boundingRect
            return (
                -scene_width / 2 <= pos.x() and pos.x() + 50 <= scene_width / 2 and
                -scene_height / 2 <= pos.y() and pos.y() + 50 <= scene_height / 2
            )
            
        elif isinstance(item, StartPosition):
            # Для стартовой позиции проверяем центр, т.к. крест довольно компактный
            pos = item.pos()
            logger.debug(f"Checking start position: pos=({pos.x()}, {pos.y()})")
            
            # Проверяем, что стартовая позиция находится в пределах сцены
            # Добавляем отступ 25 пикселей 
            return (
                -scene_width / 2 + 25 <= pos.x() <= scene_width / 2 - 25 and
                -scene_height / 2 + 25 <= pos.y() <= scene_height / 2 - 25
            )
        
        return False
    
    def mousePressEvent(self, event):
        posOriginal = self.mapToScene(event.pos()) # оригинальные координаты
        pos = self.snap_to_grid(posOriginal) # координаты с привязкой к сетке

        item = self.scene().itemAt(posOriginal, self.transform())
        parent_item = item.parentItem() if item else None
        logger.debug(f"CLICK: position={posOriginal}, item={type(item)}, parent={type(parent_item) if parent_item else None}")
        
        if event.button() == Qt.MouseButton.LeftButton:
            
            # Если в режиме редактирования и нажали на объект, меняем курсор на "кулачок"
            if self.edit_mode and item and (isinstance(item, (Robot, Region, StartPosition, Wall)) or 
                      (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker" or item.data(0) == "hover_highlight")) or 
                      (parent_item and isinstance(parent_item, (Robot, Region, StartPosition, Wall)))):
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            # Проверка клика по выделяемому объекту или его дочернему элементу
            if item:
                # Проверяем, не является ли это подсветкой при наведении
                if hasattr(item, 'data') and item.data(0) == "hover_highlight" and parent_item:
                    # Если это hover_highlight, то работаем с родительским элементом
                    item = parent_item
                
                # Добавляем отладочную информацию
                logger.debug(f"Mouse press on item: {item}, parent: {parent_item}")
                
                # Проверяем, является ли объект или его родитель поддерживаемым типом
                if self.is_supported_item(item):
                    target_item = item
                    logger.debug(f"Clicked directly on supported item: {target_item}")
                    self.select_item(target_item)
                elif parent_item and self.is_supported_item(parent_item):
                    # Если кликнули на дочерний элемент поддерживаемого объекта (например, обводку)
                    target_item = parent_item
                    logger.debug(f"Clicked on child of supported item: {target_item}")
                    self.select_item(target_item)
                elif parent_item and parent_item == self.selected_item:
                    # Если кликнули на дочерний элемент выделенного объекта
                    target_item = parent_item
                    logger.debug(f"Clicked on child of selected item: {target_item}")
                else:
                    # Клик по другому объекту, не являющемуся выделяемым
                    # Не будем снимать выделение при клике на объекты вне сцены
                    if item.scene() == self.scene():
                        logger.debug(f"Clicked on non-selectable item: {item}")
                        self.deselect_item()
            else:
                # Клик по пустому месту
                logger.debug("Clicked on empty space")
                self.deselect_item()

            # Обработка перемещения объектов в режиме редактирования
            if self.edit_mode:
                if item and hasattr(item, 'data') and item.data(0) == "wall_marker":  # Проверяем свойство
                    self.selected_marker = item
                    self.dragging_item = None  # Сбрасываем перетаскиваемый объект
                    return
                elif item and hasattr(item, 'data') and item.data(0) == "its_wall":
                    # Получаем родительский объект (Wall)
                    if parent_item and isinstance(parent_item, Wall):
                        self.dragging_item = parent_item
                        # Сохраняем точку захвата
                        self.grab_point = pos
                        # Сохраняем начальные координаты стены
                        line = self.dragging_item.line()
                        self.initial_line = QLineF(line.x1(), line.y1(), line.x2(), line.y2())
                        return
                elif item and hasattr(item, 'data') and item.data(0) == "hover_highlight":
                    # Получаем родительский объект для hover_highlight
                    if parent_item and isinstance(parent_item, Wall):
                        # Для стены сохраняем точку захвата и начальные координаты
                        self.dragging_item = parent_item
                        self.grab_point = pos
                        line = self.dragging_item.line()
                        self.initial_line = QLineF(line.x1(), line.y1(), line.x2(), line.y2())
                        return
                    elif parent_item and isinstance(parent_item, (Robot, Region, StartPosition)):
                        # Для других объектов
                        self.dragging_item = parent_item
                        self.drag_offset = pos - self.dragging_item.pos()
                        return
                elif item and (isinstance(item, (Robot, Region, StartPosition, Wall))):
                    # Если кликнули непосредственно на объект
                    self.dragging_item = item
                    
                    # Разная логика для разных типов объектов
                    if isinstance(item, Wall):
                        # Для стены сохраняем точку захвата и начальные координаты
                        self.grab_point = pos
                        line = self.dragging_item.line()
                        self.initial_line = QLineF(line.x1(), line.y1(), line.x2(), line.y2())
                    else:
                        # Для объектов с позицией (Robot, Region, StartPosition)
                        self.drag_offset = pos - self.dragging_item.pos()
                    return
                elif parent_item and isinstance(parent_item, (Robot, Region, StartPosition)):
                    # Если кликнули на дочерний элемент
                    self.dragging_item = parent_item
                    self.drag_offset = pos - self.dragging_item.pos()
                    return

            # Обработка рисования стен и регионов
            if self.drawing_mode == "wall":  
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
                    self.add_region(QRectF(self.region_start, pos).normalized())
                    self.region_start = None  # Сбрасываем начальную точку
                    if self.temp_region:
                        self.scene().removeItem(self.temp_region)
                        self.temp_region = None
    
    def mouseMoveEvent(self, event):
        posOriginal = self.mapToScene(event.pos()) # оригинальные координаты
        pos = self.snap_to_grid(posOriginal) # координаты с привязкой к сетке
        
        # Отправляем сигнал с координатами        
        self.mouse_coords_updated.emit(posOriginal.x(), posOriginal.y())
        
        # Проверяем, находится ли курсор над выделяемым объектом
        item = self.scene().itemAt(posOriginal, self.transform())
        
        # Обработка наведения для объектов с HoverHighlightMixin
        self.handle_hover_for_item(item, posOriginal)
        
        # Меняем курсор при наведении на объекты
        if self.edit_mode:
            # Проверяем, является ли объект подсветкой при наведении
            hover_highlight = False
            parent_item = None
            
            if hasattr(item, 'data') and item.data(0) == "hover_highlight" and item.parentItem():
                hover_highlight = True
                parent_item = item.parentItem()
                
            if item and (isinstance(item, (Robot, Region, StartPosition, Wall)) or 
                        (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker")) or 
                        hover_highlight or
                        (item.parentItem() and isinstance(item.parentItem(), (Robot, Region, StartPosition, Wall)))):
                # Если перетаскиваем - устанавливаем курсор "кулачок"
                if hasattr(self, 'dragging_item') and self.dragging_item:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                else:
                    # Иначе устанавливаем курсор "ладошка"
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                # Если не над объектом, возвращаем стандартный курсор
                self.setCursor(Qt.CursorShape.ArrowCursor)
        # В режиме наблюдателя устанавливаем указательный палец при наведении на объекты
        elif not self.drawing_mode:  # Режим наблюдателя
            # Проверяем, является ли объект подсветкой при наведении
            hover_highlight = False
            parent_item = None
            
            if hasattr(item, 'data') and item.data(0) == "hover_highlight" and item.parentItem():
                hover_highlight = True
                parent_item = item.parentItem()
                
            if item and (isinstance(item, (Robot, Region, StartPosition, Wall)) or 
                       (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker")) or 
                       hover_highlight or
                       (item.parentItem() and isinstance(item.parentItem(), (Robot, Region, StartPosition, Wall)))):
                # Устанавливаем курсор "указательный палец"
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                # Если не над объектом, возвращаем стандартный курсор
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        if self.edit_mode and hasattr(self, 'dragging_item') and self.dragging_item:
            logger.debug(f"Dragging {self.dragging_item}")            
            if isinstance(self.dragging_item, (Robot, Region)):
                # Вычисляем новую позицию
                new_pos = pos - self.drag_offset
                
                # Создаем временный объект для проверки
                if isinstance(self.dragging_item, Robot):
                    # Проверяем пересечение со стенами
                    if self.robot_intersects_walls(new_pos):
                        logger.debug(f"Robot would intersect with walls")
                        # Не обновляем позицию робота, если он пересекается со стенами
                        return
                        
                    # Проверяем границы сцены
                    temp_robot = Robot(new_pos)
                    if not self.check_object_within_scene(temp_robot):
                        logger.debug(f"Robot would be out of bounds")
                        return
                    # Устанавливаем позицию реального робота только если проверка пройдена
                    self.dragging_item.setPos(new_pos)
                    # Сохраняем текущую позицию как последнюю допустимую
                    self.last_valid_robot_pos = new_pos
                    # Обновляем свойства в окне свойств в режиме реального времени
                    self.properties_window.update_properties(self.dragging_item)
                elif isinstance(self.dragging_item, Region):                        
                    # Создаем временный путь для проверки границ региона
                    path = self.dragging_item.path()
                    bounds = path.boundingRect()
                    
                    # Создаем временный регион для проверки
                    temp_points = [
                        QPointF(new_pos.x() + bounds.x(), new_pos.y() + bounds.y()), 
                        QPointF(new_pos.x() + bounds.x() + bounds.width(), new_pos.y() + bounds.y()),
                        QPointF(new_pos.x() + bounds.x() + bounds.width(), new_pos.y() + bounds.y() + bounds.height()),
                        QPointF(new_pos.x() + bounds.x(), new_pos.y() + bounds.y() + bounds.height())
                    ]
                    
                    # Создаем временный регион используя специальный метод
                    temp_region = Region.create_temp_region(temp_points)
                    temp_region_id = temp_region.id
                    
                    logger.debug(f"Current region: pos=({self.dragging_item.pos().x()}, {self.dragging_item.pos().y()}), bounds=({bounds.x()}, {bounds.y()}, {bounds.width()}, {bounds.height()})")
                    
                    # Проверяем границы
                    within_scene = self.check_object_within_scene(temp_region)
                    
                    # Освобождаем ID временного региона
                    try:
                        if temp_region_id in Region._existing_ids:
                            Region._existing_ids.remove(temp_region_id)
                            logger.debug(f"Освободили временный ID {temp_region_id}")
                    except Exception as e:
                        logger.debug(f"Ошибка при освобождении ID временного региона: {e}")
                    
                    if not within_scene:
                        logger.debug(f"ERR region would be out of bounds")
                        return
                
                    self.dragging_item.setPos(new_pos)
                    # Обновляем свойства в окне свойств в режиме реального времени
                    self.properties_window.update_properties(self.dragging_item)
            elif isinstance(self.dragging_item, StartPosition):
                # Для стартовой позиции используем половинный шаг сетки
                if self.snap_to_grid_enabled:
                    # Вычисляем позицию с половинным шагом сетки
                    half_grid_pos = self.snap_to_half_grid(posOriginal - self.drag_offset)
                    new_pos = half_grid_pos
                else:
                    new_pos = posOriginal - self.drag_offset
                
                # Создаем временную стартовую позицию для проверки
                temp_start = StartPosition(new_pos)
                if not self.check_object_within_scene(temp_start):
                    logger.debug(f"ERR start position would be out of bounds")
                    # Ограничиваем позицию в пределах сцены
                    x = max(min(new_pos.x(), self.scene_width/2 - 25), -self.scene_width/2 + 25)
                    y = max(min(new_pos.y(), self.scene_height/2 - 25), -self.scene_height/2 + 25)
                    new_pos = QPointF(x, y)
                
                # Обновляем позицию и свойства
                self.dragging_item.setPos(new_pos)
                self.properties_window.update_properties(self.dragging_item)
            elif isinstance(self.dragging_item, Wall):
                # Вычисляем смещение относительно точки захвата
                dx = pos.x() - self.grab_point.x()
                dy = pos.y() - self.grab_point.y()
                new_pos_x1 = self.initial_line.x1() + dx
                new_pos_y1 = self.initial_line.y1() + dy
                new_pos_x2 = self.initial_line.x2() + dx
                new_pos_y2 = self.initial_line.y2() + dy
                logger.debug(f"to: {new_pos_x1, new_pos_y1, new_pos_x2, new_pos_y2}")
                
                # Создаем временную стену для проверки границ
                temp_wall = Wall(QPointF(new_pos_x1, new_pos_y1), QPointF(new_pos_x2, new_pos_y2), is_temp=True)
                temp_wall_id = temp_wall.id
                
                # Обновляем саму линию стены, смещая обе точки, если нет пересечения с роботом
                if not self.wall_intersects_robot(new_pos_x1, new_pos_y1, new_pos_x2, new_pos_y2, thickness=self.dragging_item.stroke_width) and self.check_object_within_scene(temp_wall):
                    with self.dragging_item.updating():
                        self.dragging_item.setLine(new_pos_x1, new_pos_y1, new_pos_x2, new_pos_y2)
                    self.properties_window.update_properties(self.dragging_item)
                    
                # Очищаем временный ID
                Wall.cleanup_temp_id(temp_wall_id)
            return
        elif self.edit_mode and self.selected_marker:            
            wall = self.selected_marker.parentItem()
            if self.selected_marker == wall.start_marker:
                logger.debug(f"Moving wall start marker to {pos}")
                if self.wall_intersects_robot(pos.x(), pos.y(), wall.line().x2(), wall.line().y2(), thickness=wall.stroke_width):
                    logger.debug(f"ERR robot intersects")
                    return 
                else:
                    with wall.updating():
                        wall.setLine(pos.x(), pos.y(), wall.line().x2(), wall.line().y2())
                    self.properties_window.update_properties(wall)  # Обновляем свойства
            else:
                if self.wall_intersects_robot(wall.line().x1(), wall.line().y1(), pos.x(), pos.y(), thickness=wall.stroke_width):
                    logger.debug(f"ERR robot intersects")
                    return 
                else:                    
                    with wall.updating():
                        wall.setLine(wall.line().x1(), wall.line().y1(), pos.x(), pos.y())
                    self.properties_window.update_properties(wall)  # Обновляем свойства
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
        # После отпускания кнопки мыши возвращаем стандартный курсор, если не над объектом
        self.setCursor(Qt.CursorShape.ArrowCursor)
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.edit_mode and self.selected_marker:
                logger.debug("Clearing selected marker")
                self.selected_marker = None
            elif hasattr(self, 'dragging_item') and self.dragging_item:
                # Проверяем, находится ли объект в пределах сцены
                if isinstance(self.dragging_item, Robot):
                    # Проверяем пересечение со стенами
                    if self.robot_intersects_walls(self.dragging_item.pos()):
                        logger.debug(f"Robot intersects with walls, resetting position")
                        # Возвращаем робота в последнюю допустимую позицию
                        if hasattr(self, 'last_valid_robot_pos'):
                            self.dragging_item.setPos(self.last_valid_robot_pos)
                        else:
                            # Если нет последней допустимой позиции, возвращаем в центр
                            self.dragging_item.setPos(0, 0)
                    # Проверка на выход за границы сцены
                    elif not self.check_object_within_scene(self.dragging_item):
                        logger.debug(f"Robot is out of bounds, resetting position")
                        # Возвращаем робота в последнюю допустимую позицию
                        if hasattr(self, 'last_valid_robot_pos'):
                            self.dragging_item.setPos(self.last_valid_robot_pos)
                        else:
                            # Если нет последней допустимой позиции, возвращаем в центр
                            self.dragging_item.setPos(0, 0)
                    else:
                        # Сохраняем текущую позицию как последнюю допустимую
                        self.last_valid_robot_pos = self.dragging_item.pos()
                
                # Обновляем свойства в окне свойств после завершения перетаскивания
                logger.debug(f"Updating properties after dragging for: {self.dragging_item}")
                self.properties_window.update_properties(self.dragging_item)
                self.dragging_item = None  # Сбрасываем перетаскиваемый объект

        super().mouseReleaseEvent(event)

    def update_robot_position(self, x, y):
        """
        Обновляет позицию робота.
        
        Args:
            x: Новая координата X
            y: Новая координата Y
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """    

        logger.debug(f"Updating robot position to {x}, {y}")
        if self.robot_model:
            new_pos = QPointF(x, y)
            
            # Проверяем пересечение со стенами
            if self.robot_intersects_walls(new_pos):
                logger.debug(f"Robot would intersect with walls, canceling update")
                # Показываем предупреждение о пересечении со стенами
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Робот пересекается со стенами. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.robot_model)
                return False
            
            # Создаем временного робота для проверки границ
            temp_robot = Robot(new_pos)
            
            # Проверяем, находится ли робот в пределах сцены
            if not self.check_object_within_scene(temp_robot):
                logger.warning(f"Robot position update to ({x}, {y}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Робот выходит за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.robot_model)
                return False
            
            # Устанавливаем новую позицию только если все проверки пройдены
            self.robot_model.setPos(new_pos)
            # Сохраняем как последнюю допустимую позицию
            self.last_valid_robot_pos = new_pos
            return True
        return False
    
    def update_robot_rotation(self, direction):
        """
        Обновляет направление робота.
        
        Args:
            direction: Новое направление в градусах
            
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """
        if self.robot_model:
            self.robot_model.set_direction(direction)
            return True
        return False
    
    def update_robot_id(self, new_id):
        """
        Обновляет ID робота.
        
        Args:
            new_id: Новый ID робота
            
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """
        if self.robot_model:
            old_id = self.robot_model.id
            # Используем метод set_id для установки нового ID
            result = self.robot_model.set_id(new_id)
            if result:
                logger.debug(f"Robot ID changed from {old_id} to {new_id}")
                # Обновляем свойства объекта с новым ID
                self.properties_updated.emit(self.robot_model)
                return True
            else:
                logger.warning(f"Failed to change robot ID from {old_id} to {new_id}")
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"Не удалось изменить ID робота. Возможно, ID '{new_id}' уже используется.",
                    QMessageBox.StandardButton.Ok
                )
                return False
        return False
    
    def update_robot_name(self, name):
        """
        Обновляет имя робота.
        
        Args:
            name: Новое имя робота
            
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """
        if self.robot_model:
            self.robot_model.set_name(name)
            logger.debug(f"Robot name changed to {name}")
            return True
        return False
    
    def update_wall_point1(self, x1, y1):
        """Обновляет первую точку стены."""
        logger.debug(f"Updating wall point1 to {x1}, {y1}")
        if self.selected_item and isinstance(self.selected_item, Wall):
            # Получаем координаты второй точки
            line = self.selected_item.line()
            x2, y2 = line.x2(), line.y2()
            
            # Создаем временную стену для проверки пересечения с роботом
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2), is_temp=True)
            thickness = self.stroke_width
            temp_wall_id = temp_wall.id
            
            # Проверяем пересечение с роботом, передавая координаты и толщину
            if self.wall_intersects_robot(x1, y1, x2, y2, thickness=thickness):
                # Очищаем временный ID
                Wall.cleanup_temp_id(temp_wall_id)
                
                logger.debug(f"Wall would intersect with robot, canceling update")
                # Показываем предупреждение о пересечении с роботом
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Стена пересекается с роботом. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.selected_item)
                return False
            
            if not self.check_object_within_scene(temp_wall):
                # Очищаем временный ID
                Wall.cleanup_temp_id(temp_wall_id)
                
                logger.warning(f"Wall point1 update to ({x1}, {y1}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Стена выйдет за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.selected_item)
                return False
            
            # Очищаем временный ID
            Wall.cleanup_temp_id(temp_wall_id)
                
            # Если все проверки пройдены, обновляем стену
            with self.selected_item.updating():
                self.selected_item.setLine(x1, y1, x2, y2)
            return True
        return False
    
    def update_wall_point2(self, x2, y2):
        """Обновляет вторую точку стены."""
        logger.debug(f"Updating wall point2 to {x2}, {y2}")
        if self.selected_item and isinstance(self.selected_item, Wall):
            # Получаем координаты первой точки
            line = self.selected_item.line()
            x1, y1 = line.x1(), line.y1()
            
            # Создаем временную стену для проверки пересечения с роботом
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2), is_temp=True)
            thickness = self.selected_item.stroke_width
            temp_wall_id = temp_wall.id
            
            # Проверяем пересечение с роботом, передавая координаты и толщину
            if self.wall_intersects_robot(x1, y1, x2, y2, thickness=thickness):
                # Очищаем временный ID
                Wall.cleanup_temp_id(temp_wall_id)
                
                logger.debug(f"Wall would intersect with robot, canceling update")
                # Показываем предупреждение о пересечении с роботом
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Стена пересекается с роботом. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.selected_item)
                return False
            
            if not self.check_object_within_scene(temp_wall):
                # Очищаем временный ID
                Wall.cleanup_temp_id(temp_wall_id)
                
                logger.warning(f"Wall point2 update to ({x2}, {y2}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Стена выйдет за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильными координатами
                self.properties_updated.emit(self.selected_item)
                return False
            
            # Очищаем временный ID
            Wall.cleanup_temp_id(temp_wall_id)
                
            # Если все проверки пройдены, обновляем стену
            with self.selected_item.updating():
                self.selected_item.setLine(x1, y1, x2, y2)
            return True
        return False
    
    def update_wall_size(self, width):
        """Обновляет размер стены."""
        logger.debug(f"Updating wall size to {width}")
        if self.selected_item and isinstance(self.selected_item, Wall):
            self.selected_item.set_stroke_width(width)            
            return True
        return False
    
    def update_region_position(self, x, y):
        """Обновляет позицию региона."""
        if self.selected_item and isinstance(self.selected_item, Region):
            # Получаем boundingRect из пути региона
            path_rect = self.selected_item.path().boundingRect()
            
            # Создаем точки для временного региона
            points = [
                QPointF(x + path_rect.x(), y + path_rect.y()),
                QPointF(x + path_rect.x() + path_rect.width(), y + path_rect.y()),
                QPointF(x + path_rect.x() + path_rect.width(), y + path_rect.y() + path_rect.height()),
                QPointF(x + path_rect.x(), y + path_rect.y() + path_rect.height())
            ]
            
            # Создаем временный регион для проверки границ сцены
            temp_region = Region.create_temp_region(points)
            
            if not self.check_object_within_scene(temp_region):
                logger.warning(f"Region position update to ({x}, {y}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    "Регион выйдет за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильной позицией
                self.properties_updated.emit(self.selected_item)
                return False
            
            # Освобождаем ID временного региона
            try:
                if temp_region.id in Region._existing_ids:
                    Region._existing_ids.remove(temp_region.id)
            except Exception as e:
                logger.debug(f"Ошибка при освобождении ID временного региона: {e}")
            
            # Если проверка пройдена, обновляем позицию
            self.selected_item.setPos(x, y)
            return True
        return False
    
    def update_region_size(self, width, height):
        """Обновляет размеры выбранного региона."""
        if not self.selected_item or not isinstance(self.selected_item, Region):
            return
        
        # Статическая переменная для отслеживания показа диалога
        if not hasattr(self, '_showing_warning_dialog'):
            self._showing_warning_dialog = False
        
        logger.debug(f"===== НАЧАЛО update_region_size: width={width}, height={height} =====")
        
        # Получаем текущие координаты (позицию) региона
        pos = self.selected_item.pos()
        x = pos.x()
        y = pos.y()
        
        # Сохраняем текущий ID и цвет
        current_id = self.selected_item.id
        current_color = self.selected_item.color
        
        # Создаем временный регион для проверки границ
        temp_points = [
            QPointF(0, 0),
            QPointF(width, 0),
            QPointF(width, height),
            QPointF(0, height)
        ]
        
        # Создаем временный регион используя специальный метод
        temp_region = Region.create_temp_region(temp_points)
        temp_region_id = temp_region.id
        temp_region.setPos(x, y)
        
        # Проверяем границы
        within_scene = self.check_object_within_scene(temp_region)
        
        # Освобождаем ID временного региона
        try:
            if temp_region_id in Region._existing_ids:
                Region._existing_ids.remove(temp_region_id)
                logger.debug(f"Освободили временный ID {temp_region_id}")
        except Exception as e:
            logger.debug(f"Ошибка при освобождении ID временного региона: {e}")
        
        # Если новый регион выходит за границы сцены, показываем ошибку и не меняем размер
        if not within_scene:
            logger.warning(f"Регион с новыми размерами выходит за границы сцены - отмена изменения размера")
            
            # Показываем предупреждение только если оно еще не отображается
            if not self._showing_warning_dialog:
                logger.warning(f"[ДИАЛОГ_1] Показываю предупреждение о выходе за границы в update_region_size")
                self._showing_warning_dialog = True
                
                # Показываем сообщение один раз
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"Регион с новыми размерами выходит за границы сцены.",
                    QMessageBox.StandardButton.Ok
                )
                
                self._showing_warning_dialog = False
            else:
                logger.warning(f"Диалог уже отображается, пропускаем показ")
            
            # Обновляем значения в окне свойств до текущих значений
            # Блокируем сигналы, чтобы не вызывать повторное обновление
            self.properties_window.region_width.blockSignals(True)
            self.properties_window.region_height.blockSignals(True)
            
            # Устанавливаем текущие значения размеров
            current_width = self.selected_item.path().boundingRect().width()
            current_height = self.selected_item.path().boundingRect().height()
            self.properties_window.region_width.setValue(int(current_width))
            self.properties_window.region_height.setValue(int(current_height))
            
            # Разблокируем сигналы
            self.properties_window.region_width.blockSignals(False)
            self.properties_window.region_height.blockSignals(False)
            
            logger.debug(f"===== КОНЕЦ update_region_size (выход за границы) =====")
            return
        
        # Освобождаем ID региона перед его удалением
        try:
            logging.debug(f"Освобождаем ID {current_id} из Region._existing_ids")
            Region._existing_ids.remove(current_id)
        except Exception as e:
            logger.debug(f"Ошибка при освобождении ID: {e}")
        
        # Удаляем старый регион из списка и сцены
        self.regions.remove(self.selected_item)
        self.scene().removeItem(self.selected_item)
        
        # Создаем новый регион с теми же ID и цветом, используя (0,0) как базовую точку
        new_points = [
            QPointF(0, 0),
            QPointF(width, 0),
            QPointF(width, height),
            QPointF(0, height)
        ]
        
        # Создаем новый регион с теми же ID и цветом
        new_region = Region(new_points, region_id=current_id, color=current_color)
        
        # Устанавливаем позицию региона
        new_region.setPos(x, y)
        
        # Добавляем новый регион на сцену
        self.objects_layer.addToGroup(new_region)
        self.regions.append(new_region)
        
        # Обновляем выбранный элемент
        self.selected_item = new_region
        self.item_selected.emit(new_region)
        
        logger.debug(f"Регион обновлен с id={current_id}, позиция=({x}, {y}), размер=({width}, {height})")
        logger.debug(f"===== КОНЕЦ update_region_size (успешно) =====")
    
    def update_region_color(self, color):
        """Обновляет цвет региона."""
        if self.selected_item and isinstance(self.selected_item, Region):
            self.selected_item.set_color(color)
            return True
        return False

    def set_grid_snap(self, enabled):
        """Включает/выключает привязку к сетке."""
        if self.snap_to_grid_enabled != enabled:
            self.snap_to_grid_enabled = enabled
            # Эмитируем сигнал об изменении режима привязки к сетке
            logger.debug(f"Изменение режима привязки к сетке: {enabled}")
            self.grid_snap_changed.emit(enabled)
    
    def set_grid_size(self, size):
        """Устанавливает размер сетки."""
        self.grid_size = size

    def update_wall_id(self, new_id):
        """Обновляет ID выбранной стены."""
        if self.selected_item and isinstance(self.selected_item, Wall):
            old_id = self.selected_item.id
            # Используем метод set_id для установки нового ID
            result = self.selected_item.set_id(new_id)
            if result:
                logger.debug(f"Wall ID changed from {old_id} to {new_id}")
                # Обновляем свойства объекта с новым ID
                self.properties_updated.emit(self.selected_item)
                return True
            else:
                logger.warning(f"Failed to change wall ID from {old_id} to {new_id}")
                # Показываем предупреждение о дублировании ID
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"ID '{new_id}' уже используется другой стеной. Пожалуйста, выберите другой ID.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильным ID
                self.properties_updated.emit(self.selected_item)
                return False
        return False

    def update_region_id(self, new_id):
        """Обновляет ID выбранного региона."""
        if self.selected_item and isinstance(self.selected_item, Region):
            old_id = self.selected_item.id
            # Используем метод set_id класса Region для установки ID
            result = self.selected_item.set_id(new_id)
            if result:
                logger.debug(f"Region ID changed from {old_id} to {new_id}")
                # Обновляем свойства объекта с новым ID
                self.properties_updated.emit(self.selected_item)
                return True
            else:
                logger.warning(f"Failed to change region ID from {old_id} to {new_id}")
                # Показываем предупреждение о дублировании ID
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"ID '{new_id}' уже используется другим регионом. Пожалуйста, выберите другой ID.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильным ID
                self.properties_updated.emit(self.selected_item)
                return False
        return False

    def set_theme(self, is_dark_theme=True):
        """Устанавливает тему для сцены"""
        self.setStyleSheet(AppStyles.get_scene_style(is_dark_theme))

    def wheelEvent(self, event):
        """Обработка события колесика мыши для масштабирования и прокрутки"""
        # Проверяем, зажата ли клавиша Ctrl
        is_ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        
        # Если Ctrl зажат, выполняем масштабирование
        if is_ctrl_pressed:
            # Получаем текущее положение курсора в координатах сцены
            view_pos = event.position()
            scene_pos = self.mapToScene(int(view_pos.x()), int(view_pos.y()))
            
            # Определяем направление прокрутки
            scroll_direction = 1 if event.angleDelta().y() > 0 else -1
            
            # Изменяем масштаб
            old_scale = self._scale_factor
            if scroll_direction > 0:
                # Увеличиваем масштаб
                self.scale_view(self._scale_factor + self._scale_step)
            else:
                # Уменьшаем масштаб
                self.scale_view(self._scale_factor - self._scale_step)
                
            # Если масштаб не изменился, используем стандартную прокрутку
            if self._scale_factor == old_scale:
                super().wheelEvent(event)
                return
                
            # Корректируем положение сцены, чтобы точка под курсором осталась на месте
            new_pos = self.mapFromScene(scene_pos)
            delta = QPointF(new_pos.x() - view_pos.x(), new_pos.y() - view_pos.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + int(delta.y()))
            
            # Обновляем видимость скроллбаров после изменения масштаба и прокрутки
            self.update_scrollbars_visibility()
            
            # Сообщаем об изменении масштаба
            logger.debug(f"Scale changed to: {self._scale_factor}")
            
            # Подавляем стандартную обработку события
            event.accept()
        else:
            # Если Ctrl не зажат, используем стандартную прокрутку
            super().wheelEvent(event)
            
            # Обновляем видимость скроллбаров после прокрутки
            self.update_scrollbars_visibility()
    
    def scale_view(self, new_scale):
        """Масштабирует представление до указанного значения"""
        # Ограничиваем масштаб минимальным и максимальным значениями
        new_scale = max(min(new_scale, self._max_scale), self._min_scale)
        
        # Если масштаб не изменился, ничего не делаем
        if new_scale == self._scale_factor:
            return
            
        # Сохраняем новый масштаб
        self._scale_factor = new_scale
        
        # Применяем новый масштаб
        self.setTransform(QTransform().scale(self._scale_factor, self._scale_factor))
        
        # Обновляем видимость скроллбаров
        self.update_scrollbars_visibility()
        
        logger.debug(f"View scaled to: {self._scale_factor}")
    
    def resetScale(self):
        """Сбрасывает масштаб к стандартному (1.0)"""
        self.scale_view(1.0)
        logger.debug("Scale reset to 1.0")
    
    def zoomIn(self):
        """Увеличивает масштаб на один шаг"""
        self.scale_view(self._scale_factor + self._scale_step)
        logger.debug(f"Zoomed in to: {self._scale_factor}")
    
    def zoomOut(self):
        """Уменьшает масштаб на один шаг"""
        self.scale_view(self._scale_factor - self._scale_step)
        logger.debug(f"Zoomed out to: {self._scale_factor}")
    
    def currentScale(self):
        """Возвращает текущий масштаб"""
        return self._scale_factor

    def delete_wall(self, wall):
        """Удаляет стену со сцены"""
        if wall in self.walls:
            self.scene().removeItem(wall)
            self.walls.remove(wall)
            logger.debug(f"Удалена стена {wall.id}")
    
    def delete_region(self, region):
        """Удаляет регион со сцены"""
        if region in self.regions:
            self.scene().removeItem(region)
            self.regions.remove(region)
            logger.debug(f"Удален регион {region.id}")
            
    def delete_selected_item(self):
        """
        Удаляет выбранный элемент на сцене.
        Временная заглушка.
        """
        logger.debug("Попытка удалить элемент (заглушка)")
        if self.selected_item:
            logger.debug(f"Тип выбранного элемента: {type(self.selected_item)}")
            
            # Заглушка для отладки - просто снимаем выделение
            # TODO: реализовать полноценное удаление
            self.deselect_item()
            logger.debug("Снято выделение с объекта (заглушка)")

    def clear_scene(self):
        """
        Полностью очищает сцену от всех объектов, кроме сетки и осей.
        """
        logger.debug("Clearing scene...")
        
        # Удаляем все стены
        for wall in self.walls[:]:
            logger.debug(f"Removing wall {wall}")
            self.scene().removeItem(wall)
            self.walls.remove(wall)
        
        # Удаляем все регионы
        for region in self.regions[:]:
            logger.debug(f"Removing region {region}")
            region.remove_from_scene()
            self.regions.remove(region)
        
        # Удаляем робота
        if self.robot_model:
            logger.debug("Removing robot")
            self.scene().removeItem(self.robot_model)
            self.robot_model = None
            # Освобождаем экземпляр робота
            Robot.reset_instance()
            
        # Удаляем стартовую позицию
        if self.start_position_model:
            logger.debug("Removing start position")
            self.scene().removeItem(self.start_position_model)
            self.start_position_model = None
            # Освобождаем экземпляр стартовой позиции
            StartPosition.reset_instance()
        
        # Сбрасываем режим рисования
        self.drawing_mode = None
        self.selected_item = None
        
        # Очищаем другие выделенные элементы
        if self.selected_marker:
            self.scene().removeItem(self.selected_marker)
            self.selected_marker = None
        
        # Отправляем сигнал о том, что не выделено ни одного элемента
        self.item_deselected.emit()
        
        # Сбрасываем временные переменные
        self.wall_start = None
        self.region_start = None
        self.temp_wall = None
        self.temp_region = None
        
        # Обновляем сцену
        self.update()
        
        logger.debug("Scene cleared successfully")

    def place_robot(self, position, robot_id=None, name="", direction=0):
        """
        Размещает робота на сцене в указанной позиции.
        
        Args:
            position: Позиция для размещения робота (QPointF)
            robot_id: Идентификатор робота (игнорируется, т.к. робот один)
            name: Имя робота
            direction: Направление робота в градусах
            
        Returns:
            Robot: Модель робота или None, если размещение не удалось
        """
        logger.debug(f"Размещение робота в позиции: {position}, name={name}, direction={direction}")
        
        # Проверяем, не пересекается ли позиция робота со стенами
        for wall in self.walls:
            # Вычисляем расстояние от центра робота до стены
            line = wall.line()
            distance = self.distance_to_line(position, line)
            
            # Если расстояние меньше радиуса робота, то это пересечение
            if distance < 25:  # 25 - примерный радиус робота
                logger.warning(f"Робот пересекается со стеной id={wall.id} - отмена размещения")
                return None
        
        # Проверяем, находится ли робот в пределах сцены
        # Создаем временного робота для проверки границ
        temp_robot = Robot(position, name=name, direction=direction)
        if not self.check_object_within_scene(temp_robot):
            logger.warning("Робот выходит за границы сцены - отмена размещения")
            # Сбрасываем экземпляр, т.к. его не удалось разместить
            Robot.reset_instance()
            self.robot_model = None
            return None
            
        # Если у нас уже есть робот на сцене, удаляем его
        if self.robot_model:
            self.scene().removeItem(self.robot_model)
            
        # Создаем нового робота (или получаем существующий экземпляр)
        self.robot_model = Robot(position, name=name, direction=direction)
            
        # Добавляем робота на сцену
        self.scene().addItem(self.robot_model)
        
        # Настраиваем обработку событий для робота
        self.robot_model.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.robot_model.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        # Сохраняем текущую позицию как последнюю допустимую
        self.last_valid_robot_pos = position
        
        logger.debug(f"Робот успешно размещен в позиции {position}, id={self.robot_model.id}")
        return self.robot_model
        
    def place_region(self, points, region_id=None, color="#800000ff"):
        """
        Размещает регион на поле.
        
        Args:
            points: Список точек QPointF, определяющих контур региона
            region_id: Идентификатор региона (если None, будет сгенерирован автоматически)
            color: Цвет заливки региона в формате HEX с альфа-каналом
        
        Returns:
            Объект Region или None, если размещение не удалось
        """
        logger.debug(f"Placing region with id={region_id}, color={color}")
        
        # Проверяем, что у нас достаточно точек для формирования региона
        if not points or len(points) < 3:
            logger.warning("Недостаточно точек для создания региона (минимум 3 точки)")
            return None
        
        # Создаем регион
        region = Region(points, region_id, color)
        
        # Добавляем регион на сцену через слой объектов
        self.objects_layer.addToGroup(region)
        
        # Сохраняем ссылку на регион
        self.regions.append(region)
        
        logger.debug(f"Region placed successfully with id={region.id}")
        return region

    def update_start_position(self, x, y):
        """
        Обновляет позицию стартовой позиции.
        
        Args:
            x: Новая координата X
            y: Новая координата Y
            
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """
        if self.start_position_model:
            # Применяем привязку к сетке, если она включена
            if self.snap_to_grid_enabled:
                pos = self.snap_to_half_grid(QPointF(x, y))
                x, y = pos.x(), pos.y()
            
            # Создаем временный объект для проверки границ сцены
            temp_start = StartPosition(QPointF(x, y))
            if not self.check_object_within_scene(temp_start):
                logger.warning(f"Start position update to ({x}, {y}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"Стартовая позиция выйдет за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильной позицией
                self.properties_updated.emit(self.start_position_model)
                return False
            
            # Если проверка пройдена, обновляем позицию
            self.start_position_model.setPos(x, y)
            return True
            
        return False

    def update_start_position_direction(self, direction):
        """
        Обновляет направление стартовой позиции.
        
        Args:
            direction: Новое направление (в градусах)
            
        Returns:
            bool: True, если обновление прошло успешно, False в противном случае
        """
        if self.start_position_model:
            self.start_position_model.set_direction(direction)
            return True
        return False

    def place_start_position(self, position, direction=0):
        """
        Размещает стартовую позицию на сцене.
        
        Args:
            position: Позиция стартовой позиции (QPointF)
            direction: Направление стартовой позиции (в градусах)
            
        Returns:
            StartPosition: Объект стартовой позиции, если размещение успешно, None в противном случае
        """
        # Создаем временный объект для проверки границ сцены
        temp_start = StartPosition(position, direction)
        
        if not self.check_object_within_scene(temp_start):
            logger.warning("Стартовая позиция выходит за границы сцены - отмена размещения")
            # Сбрасываем экземпляр, т.к. его не удалось разместить
            StartPosition.reset_instance()
            self.start_position_model = None
            return None
            
        # Если у нас уже есть стартовая позиция на сцене, удаляем ее
        if self.start_position_model:
            self.scene().removeItem(self.start_position_model)
            
        # Создаем новую стартовую позицию (или получаем существующий экземпляр)
        self.start_position_model = StartPosition(position, direction)
            
        # Добавляем стартовую позицию на сцену
        self.scene().addItem(self.start_position_model)
        
        # Настраиваем обработку событий для стартовой позиции
        self.start_position_model.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.start_position_model.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        logger.debug(f"Стартовая позиция успешно размещена в позиции {position}, direction={direction}")
        
        return self.start_position_model

    def snap_to_half_grid(self, pos):
        """
        Привязывает координаты к половинному шагу сетки.
        Для использования при перетаскивании стартовой позиции.
        
        Args:
            pos: Позиция (QPointF)
            
        Returns:
            QPointF: Координаты, привязанные к половинному шагу сетки
        """
        if not self.snap_to_grid_enabled:
            return pos
        
        # Берем половину шага сетки
        half_grid_size = self.grid_size / 2
        
        # Округляем координаты до половины шага сетки
        x = round(pos.x() / half_grid_size) * half_grid_size
        y = round(pos.y() / half_grid_size) * half_grid_size
        
        return QPointF(x, y)

    def is_supported_item(self, item):
        """
        Проверяет, является ли элемент поддерживаемым типом (Robot, Wall, Region, StartPosition).
        Также проверяет наличие data("its_wall") или data("wall_marker").
        """
        # Проверка на прямую поддержку типа
        if isinstance(item, (Robot, Region, StartPosition, Wall)):
            return True
        
        # Проверка на элементы стены по data
        if hasattr(item, 'data') and item.data(0) in ["its_wall", "wall_marker"]:
            return True
            
        # Проверяем, не является ли это подсветкой при наведении
        if hasattr(item, 'data') and item.data(0) == "hover_highlight":
            # Для hover_highlight передаем родителя в is_supported_item
            if item.parentItem():
                return self.is_supported_item(item.parentItem())
            return False
            
        # Проверка на родительский элемент
        if item and item.parentItem():
            if isinstance(item.parentItem(), (Robot, Region, StartPosition, Wall)):
                return True
            
        return False
        
    def handle_hover_for_item(self, item, pos):
        """
        Обрабатывает наведение мыши для объекта под курсором.
        Проверяет, имеет ли объект или его родитель поддержку HoverHighlightMixin.
        
        Args:
            item: Объект под курсором
            pos: Позиция курсора (QPointF)
        """
        # Находим целевой объект (либо сам элемент, либо его родитель)
        target_item = None
        
        # Проверяем, является ли сам элемент поддерживаемым
        if item and isinstance(item, HoverHighlightMixin):
            target_item = item
        # Проверяем родителя элемента
        elif item and item.parentItem() and isinstance(item.parentItem(), HoverHighlightMixin):
            target_item = item.parentItem()
            
        # Для всех зарегистрированных объектов с поддержкой наведения
        for obj in [obj for obj in self.objects_layer.childItems() if isinstance(obj, HoverHighlightMixin)]:
            # Если объект под курсором, обрабатываем наведение
            if obj == target_item:
                if not obj._is_hovered:
                    logger.debug(f"Hover enter for {obj} at {pos}")
                    obj._is_hovered = True
                    # Показываем подсветку при наведении только если объект не выделен
                    if obj != self.selected_item:
                        obj.set_hover_highlight(True)
            # Иначе убираем подсветку, если она была
            elif obj._is_hovered:
                logger.debug(f"Hover leave for {obj}")
                obj._is_hovered = False
                obj.set_hover_highlight(False)
                
    def robot_intersects_walls(self, robot_pos):
        """
        Проверяет, пересекается ли робот со стенами в указанной позиции.
        
        Args:
            robot_pos: Позиция робота (QPointF) - верхний левый угол
            
        Returns:
            bool: True, если робот пересекается хотя бы с одной стеной, False в противном случае
        """
        if not self.robot_model:
            return False
            
        # Размер робота - 50x50 пикселей
        robot_size = 50
        
        # Создаем прямоугольник робота
        robot_rect = QRectF(
            robot_pos.x(), 
            robot_pos.y(),
            robot_size, 
            robot_size
        )
        
        # Проверяем пересечение с каждой стеной
        for wall in self.walls:
            line = wall.line()
            
            # Получаем толщину стены из атрибута stroke_width
            thickness = wall.stroke_width
            
            # Проверяем пересечение линии стены с прямоугольником робота, учитывая толщину
            # Используем утилитарную функцию
            if line_with_thickness_intersects_rect(line, robot_rect, thickness):
                logger.debug(f"Robot intersects with wall {wall.id}")
                return True
                
        return False
