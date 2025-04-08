from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsItemGroup, QGraphicsItem, QMessageBox, QInputDialog,
    QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsPathItem
)
from PyQt6.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QImage, QTransform, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal, pyqtSlot, QThread, QTimer, QDataStream, QIODevice, QByteArray
from PyQt6.QtSvg import QSvgRenderer
from scene.items import Robot, Wall, Region, StartPosition
from scene.managers import SceneManager
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
        
        # Отключаем перехват событий для слоя объектов
        self.objects_layer.setFiltersChildEvents(False)
        
        # Устанавливаем z-index для слоев
        self.grid_layer.setZValue(0)
        self.axes_layer.setZValue(1)
        self.objects_layer.setZValue(2)
        
        # Добавляем слои в сцену в правильном порядке
        self.scene().addItem(self.grid_layer)
        self.scene().addItem(self.axes_layer)
        self.scene().addItem(self.objects_layer)
        
        self.grid_size = grid_size
        self.snap_to_grid_enabled = True

        self.drawing_mode = None
        self.edit_mode = False
        self.selected_item = None
        self.selected_marker = None
        self.dragging_item = None # <-- Инициализируем здесь
        
        self.temp_wall = None
        self.wall_start = None

        self.region_start = None
        self.temp_region = None
        
        # Инициализируем менеджер сцены
        self.scene_manager = SceneManager(scene_width, scene_height)

        self._current_robot_item = None
        self._current_start_item = None
        
        # Состояния объектов
        self.dragging_robot = False
        self.robot_offset = QPointF()
        self.scene_width = scene_width
        self.scene_height = scene_height

        # Инициализация масштаба
        self._scale_factor = 1.0
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._scale_step = 0.5

        self._scroll_manager = None

        self.draw_grid()
        self.draw_axes()
        self.init_robot(QPointF(0, 0))
        self.init_start_position(QPointF(25, 25))
        
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
        # Используем self.scene_manager.robot
        if not self.scene_manager.robot:
            return False
            
        # Получаем bounding rect из менеджера
        robot_rect = self.scene_manager.robot.boundingRect()
        # Учитываем позицию робота из менеджера
        robot_rect.translate(self.scene_manager.robot.pos())
        
        # Линия стены
        wall_line = QLineF(QPointF(x1, y1), QPointF(x2, y2))
        
        # Если толщина не указана, получаем её из временной стены
        if thickness is None:
            # Создаем временную стену для определения толщины линии
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2), is_temp=True)
            thickness = temp_wall.stroke_width
            Wall.cleanup_temp_id(temp_wall.id)
        
        # Проверяем пересечение линии стены с прямоугольником робота с учетом толщины
        # Используем утилитарную функцию
        return line_with_thickness_intersects_rect(wall_line, robot_rect, thickness)
    
    def add_wall(self, p1, p2, wall_id=None):
        """Добавляет стену на сцену."""
        wall_item = self.scene_manager.add_wall(p1, p2, wall_id)
        if wall_item:
            self.objects_layer.addToGroup(wall_item)
            logger.debug(f"Графический элемент стены добавлен: id={wall_item.id}")
            # --- Выделяем стену после добавления --- 
            self.select_item(wall_item)
            # --------------------------------------
            return wall_item
        else:
            logger.warning("Не удалось добавить стену (менеджер сцены)")
            return None

    def add_region(self, rect_or_points, region_id=None, color=None):
        """Добавляет регион на сцену."""
        region_item = self.scene_manager.add_region(rect_or_points, region_id, color)
        if region_item:
            self.objects_layer.addToGroup(region_item)
            logger.debug(f"Графический элемент региона добавлен: id={region_item.id}")
            # --- Выделяем регион после добавления --- 
            self.select_item(region_item)
            # ---------------------------------------
            return region_item
        else:
            logger.warning("Не удалось добавить регион (менеджер сцены)")
            return None

    def init_robot(self, position, name="", direction=0):
        """Инициализирует или обновляет позицию робота."""
        # Пытаемся разместить/обновить робота через менеджер
        robot_item = self.scene_manager.place_robot(position, name, direction)
        
        if robot_item:
            # Если менеджер вернул объект робота (успешное размещение)
            # Удаляем старый графический элемент робота со сцены, если он был
            if self._current_robot_item and self._current_robot_item.scene():
                self.objects_layer.removeFromGroup(self._current_robot_item)
            
            # Сохраняем ссылку на новый графический элемент и добавляем его на сцену
            self._current_robot_item = robot_item
            self.objects_layer.addToGroup(self._current_robot_item)
            logger.debug(f"Робот обновлен/добавлен на сцену: pos={position}, name={name}, direction={direction}")
        else:
            # Если менеджер вернул None (размещение не удалось)
            logger.warning("Не удалось разместить робота (менеджер сцены)")
            # Старый графический элемент остается на месте, если он был

    def init_start_position(self, position, direction=0):
        """Инициализирует или обновляет стартовую позицию."""
        # Пытаемся разместить/обновить стартовую позицию через менеджер
        start_item = self.scene_manager.place_start_position(position, direction)
        
        if start_item:
            # Если менеджер вернул объект старта (успешное размещение)
            # Удаляем старый графический элемент старта со сцены, если он был
            if self._current_start_item and self._current_start_item.scene():
                self.objects_layer.removeFromGroup(self._current_start_item)
                
            # Сохраняем ссылку на новый графический элемент и добавляем его на сцену
            self._current_start_item = start_item
            self.objects_layer.addToGroup(self._current_start_item)
            logger.debug(f"Стартовая позиция обновлена/добавлена на сцену: pos={position}, direction={direction}")
        else:
            # Если менеджер вернул None (размещение не удалось)
            logger.warning("Не удалось разместить стартовую позицию (менеджер сцены)")
            # Старый графический элемент остается на месте, если он был

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
        # Используем self.scene_manager.walls вместо self.walls
        for wall in self.scene_manager.walls:
            if (wall.line().x1() < -width // 2 or wall.line().x2() > width // 2 or
                wall.line().y1() < -height // 2 or wall.line().y2() > height // 2):
                return False
        # Используем self.scene_manager.regions вместо self.regions
        for region in self.scene_manager.regions:
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
    
    def is_supported_item(self, item):
        """
        Проверяет, является ли элемент поддерживаемым типом для выделения/взаимодействия
        (Robot, Wall, Region, StartPosition).
        """
        return isinstance(item, (Robot, Wall, Region, StartPosition))
        
    def get_selectable_parent(self, item):
        logger.debug(f"[GET_PARENT] Checking item: {item}") # <-- Лог входа
        if not item:
            logger.debug("[GET_PARENT] Item is None, returning None")
            return None

        # Если сам элемент подходит
        if self.is_supported_item(item):
            logger.debug(f"[GET_PARENT] Item itself is supported: {item}, returning item")
            return item

        # Проверяем родителя
        parent = item.parentItem()
        if parent and self.is_supported_item(parent):
            logger.debug(f"[GET_PARENT] Parent is supported: {parent}, returning parent")
            return parent
            
        # Особый случай для маркеров стены (они не QGraphicsItemGroup)
        if hasattr(item, 'data') and item.data(0) == "wall_marker" and parent and isinstance(parent, Wall):
             logger.debug(f"[GET_PARENT] Item is wall_marker, returning parent Wall: {parent}")
             return parent # Возвращаем стену, если кликнули на маркер
             
        # Рекурсивно идем вверх (на всякий случай, если вложенность > 1)
        current = parent
        while current:
            if self.is_supported_item(current):
                 logger.debug(f"[GET_PARENT] Found supported ancestor: {current}, returning ancestor")
                 return current
            current = current.parentItem()
            
        logger.debug("[GET_PARENT] No supported parent/ancestor found, returning None")
        return None
        
    def mousePressEvent(self, event):
        posOriginal = self.mapToScene(event.pos())
        pos = self.snap_to_grid(posOriginal)

        item_at_click = self.scene().itemAt(posOriginal, self.transform())
        # Ищем родительский элемент, который можно выделить
        target_item_for_selection = self.get_selectable_parent(item_at_click)

        logger.debug(f"CLICK: position={posOriginal}, item={type(item_at_click)}, parent={type(item_at_click.parentItem()) if item_at_click else None}, target={target_item_for_selection}")
            
        if event.button() == Qt.MouseButton.LeftButton:
            if target_item_for_selection: # Если нашли объект для выделения
                self.select_item(target_item_for_selection) # Передаем найденный родительский объект
                
                # Если в режиме редактирования, меняем курсор и готовимся к перетаскиванию
                if self.edit_mode:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    # Если кликнули на маркер стены
                    if item_at_click and hasattr(item_at_click, 'data') and item_at_click.data(0) == "wall_marker":
                         self.selected_marker = item_at_click
                         self.dragging_item = None # Не перетаскиваем всю стену, а только маркер
                    else:
                        # Перетаскиваем основной объект
                        self.dragging_item = target_item_for_selection
                        if isinstance(target_item_for_selection, Wall):
                            self.grab_point = pos
                            line = self.dragging_item.line()
                            self.initial_line = QLineF(line.x1(), line.y1(), line.x2(), line.y2())
                        elif isinstance(target_item_for_selection, (Robot, Region, StartPosition)):
                            self.drag_offset = pos - self.dragging_item.pos()
                    return # Завершаем обработку, т.к. начали перетаскивание/выделение
            else: # Если кликнули не на поддерживаемый объект или пустое место
                 if item_at_click and item_at_click.scene() == self.scene():
                     logger.debug(f"Clicked on non-selectable item: {item_at_click}")
                 else:
                     logger.debug("Clicked on empty space or outside scene")
                 self.deselect_item()
                 self.setCursor(Qt.CursorShape.ArrowCursor)

            # --- Обработка режимов РИСОВАНИЯ --- 
            if not self.edit_mode:
                if self.drawing_mode == "wall": 
                    if self.wall_start is None:
                        self.wall_start = pos
                    else:
                        self.add_wall(self.wall_start, pos)
                        self.wall_start = None
                        if self.temp_wall:
                            self.scene().removeItem(self.temp_wall)
                            self.temp_wall = None
                elif self.drawing_mode == "region":
                    if self.region_start is None:
                        self.region_start = pos
                        logger.debug(f"Region start: {self.region_start}")
                    else:
                        # --- Возвращаем синий цвет по умолчанию --- 
                        self.add_region(QRectF(self.region_start, pos).normalized(), color="#800000FF")
                        # ---------------------------------------
                        self.region_start = None
                        if self.temp_region:
                            self.scene().removeItem(self.temp_region)
                            self.temp_region = None
                        
        # Обработка клика правой кнопкой (например, для удаления)
        elif event.button() == Qt.MouseButton.RightButton:
            if target_item_for_selection:
                logger.debug(f"Right click on: {target_item_for_selection}")
                # TODO: Показать контекстное меню для удаления?
                # Временно удаляем объект по правому клику
                # self.delete_item(target_item_for_selection)
            else:
                logger.debug("Right click on empty space")

    def mouseMoveEvent(self, event):
        posOriginal = self.mapToScene(event.pos())
        pos = self.snap_to_grid(posOriginal)
        self.mouse_coords_updated.emit(pos.x(), pos.y())
        
        # --- Режим РИСОВАНИЯ (Остается в начале) --- 
        logger.debug(f"[DRAW_CHECK] edit={self.edit_mode}, draw_mode={self.drawing_mode}, wall_start={self.wall_start is not None}, region_start={self.region_start is not None}")
        if self.drawing_mode:
            logger.debug(f"[DRAW_INSIDE] Entered 'if self.drawing_mode'. draw_mode='{self.drawing_mode}', wall_start set: {self.wall_start is not None}")
            if self.drawing_mode == "wall" and self.wall_start:
                if self.temp_wall:
                    self.scene().removeItem(self.temp_wall)
                self.temp_wall = QGraphicsLineItem(QLineF(self.wall_start, pos))
                pen = QPen(Qt.GlobalColor.gray, 2, Qt.PenStyle.DashLine)
                self.temp_wall.setPen(pen)
                self.temp_wall.setZValue(3)
                self.scene().addItem(self.temp_wall)
                self.scene().update(self.sceneRect()) # Обновляем сцену
                logger.debug(f"[DRAW_WALL_MOVE] Added temp_wall to scene: {self.temp_wall}")
            elif self.drawing_mode == "region" and self.region_start:
                if self.temp_region:
                     self.scene().removeItem(self.temp_region)
                rect = QRectF(self.region_start, pos).normalized()
                self.temp_region = QGraphicsRectItem(rect)
                pen = QPen(Qt.GlobalColor.gray, 2, Qt.PenStyle.DashLine)
                self.temp_region.setPen(pen)
                self.temp_region.setBrush(QBrush(Qt.GlobalColor.transparent))
                self.temp_region.setZValue(3)
                self.scene().addItem(self.temp_region)
                self.scene().update(self.sceneRect()) # Обновляем сцену
                logger.debug(f"[DRAW_REGION_MOVE] Added temp_region to scene: {self.temp_region}")
        # --- Конец блока РИСОВАНИЯ ---

        # --- Логика перетаскивания объектов (перемещена обратно внутрь if event.buttons) ---
        # if self.edit_mode and self.dragging_item and not self.selected_marker: 
        #    # ... (этот блок теперь ниже)
        # --- Конец перемещенной логики ---

        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.edit_mode:
                if self.selected_marker:
                    # --- Восстанавливаем логику перетаскивания маркера --- 
                    if self.selected_item and isinstance(self.selected_item, Wall):
                        new_line = None
                        if self.selected_marker == self.selected_item.start_marker:
                            new_line = QLineF(pos, self.selected_item.line().p2())
                        elif self.selected_marker == self.selected_item.end_marker:
                            new_line = QLineF(self.selected_item.line().p1(), pos)
                        
                        if new_line:
                            can_move = True
                            # ... (проверки пересечений и границ) ...
                            if self.scene_manager.robot and \
                               self.scene_manager.wall_intersects_robot(new_line.x1(), new_line.y1(), new_line.x2(), new_line.y2(), self.selected_item.stroke_width):
                                can_move = False
                            if not self.scene_manager._check_wall_within_scene(Wall(new_line.p1(), new_line.p2(), is_temp=True)):
                                can_move = False
                            if can_move:
                                self.selected_item.setLine(new_line)
                                self.properties_updated.emit(self.selected_item)
                    # --- Конец логики маркера ---
                elif self.dragging_item:
                    if isinstance(self.dragging_item, Wall):
                         # --- Восстанавливаем логику перетаскивания стены --- 
                        delta = pos - self.grab_point
                        new_line = self.initial_line.translated(delta)
                        can_move = True
                        # ... (проверки пересечений и границ для стены) ...
                        if self.scene_manager.robot and \
                           self.scene_manager.wall_intersects_robot(new_line.x1(), new_line.y1(), new_line.x2(), new_line.y2(), self.dragging_item.stroke_width):
                            can_move = False
                        if not self.scene_manager._check_wall_within_scene(Wall(new_line.p1(), new_line.p2(), is_temp=True)):
                            can_move = False
                        if can_move:
                            self.dragging_item.setLine(new_line)
                            self.properties_updated.emit(self.dragging_item)
                        # --- Конец логики стены ---
                    elif isinstance(self.dragging_item, (Robot, Region, StartPosition)):
                        logger.debug(f"[DRAG_MOVE] Moving item: {self.dragging_item} with button pressed") 
                        new_pos = pos - self.drag_offset
                        can_move = True
                        # ... (проверки пересечений и границ для Robot, Region, StartPosition) ...
                        if isinstance(self.dragging_item, Robot):
                            if self.robot_intersects_walls(new_pos):
                                logger.debug("[DRAG_MOVE] Robot intersects wall, cancel")
                                can_move = False
                            if not self.scene_manager._check_robot_within_scene(Robot(new_pos)):
                                logger.debug("[DRAG_MOVE] Robot out of bounds, cancel")
                                can_move = False
                        elif isinstance(self.dragging_item, Region):
                            if not self.scene_manager._check_region_within_scene(Region(self.dragging_item.boundingRect().translated(new_pos), is_temp=True)):
                                logger.debug("[DRAG_MOVE] Region out of bounds, cancel")
                                can_move = False
                        elif isinstance(self.dragging_item, StartPosition):
                            temp_start_pos = StartPosition(new_pos, self.dragging_item.rotation())
                            if not self.scene_manager._check_start_position_within_scene(temp_start_pos):
                                logger.debug("[DRAG_MOVE] StartPos out of bounds, cancel")
                                can_move = False
                            StartPosition.reset_instance()
                        
                        if can_move:
                            logger.debug(f"[DRAG_MOVE] Setting pos for {self.dragging_item} to {new_pos}")
                            self.dragging_item.setPos(new_pos)
                            self.properties_updated.emit(self.dragging_item) # Обновляем свойства при перетаскивании
                        else:
                            logger.debug(f"[DRAG_MOVE] Move cancelled for {self.dragging_item}")
            # --- Конец блока РЕДАКТИРОВАНИЯ ---
        # --- Конец блока if event.buttons() ... ---

        # --- Обработка наведения --- 
        item_under_cursor = self.scene().itemAt(posOriginal, self.transform())
        self.handle_hover_for_item(item_under_cursor, posOriginal)
        # --- Конец обработки наведения ---

        # --- Управление курсором (Добавляем логирование) --- 
        target_item = self.get_selectable_parent(item_under_cursor)
        if self.edit_mode:
            is_wall_marker = item_under_cursor and hasattr(item_under_cursor, 'data') and item_under_cursor.data(0) == "wall_marker"
            logger.debug(f"[CURSOR_EDIT] dragging={self.dragging_item is not None}, marker={self.selected_marker is not None}, target={target_item}, is_marker={is_wall_marker}") # <-- Лог состояния
            if self.dragging_item or self.selected_marker:
                cursor = Qt.CursorShape.ClosedHandCursor
            elif target_item or is_wall_marker:
                cursor = Qt.CursorShape.OpenHandCursor
            else:
                cursor = Qt.CursorShape.ArrowCursor
            self.setCursor(cursor)
            logger.debug(f"[CURSOR_EDIT] Set cursor: {cursor}") # <-- Лог установки
        elif self.drawing_mode:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif target_item: # Режим наблюдения и курсор над объектом
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        # --- Конец управления курсором ---

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
        """Обновляет размер выбранного региона."""
        if self.selected_item and isinstance(self.selected_item, Region):
            logger.debug(f"Обновление размера региона {self.selected_item.id} на {width}x{height}")
            # Используем setRect вместо set_size
            try:
                # Устанавливаем прямоугольник в локальных координатах (0,0) с новыми размерами
                self.selected_item.prepareGeometryChange() # Важно вызвать перед изменением геометрии
                self.selected_item.setRect(0, 0, width, height)
                self.scene().update() # Обновляем сцену для перерисовки
                self.properties_updated.emit(self.selected_item) # Обновляем свойства
            except Exception as e:
                logger.error(f"Ошибка при обновлении размера региона: {e}")
        else:
            logger.warning("Попытка обновить размер, но регион не выбран")
    
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
        """Очищает сцену от всех объектов."""
        # Очищаем состояние в менеджере (удаляет ссылки на объекты Robot, Wall и т.д.)
        self.scene_manager.clear()
        
        # Удаляем все графические элементы из слоя объектов
        # childItems() возвращает копию, поэтому безопасно удалять в цикле
        for item in self.objects_layer.childItems():
            self.objects_layer.removeFromGroup(item)
        
        # Сбрасываем ссылки на текущие графические элементы робота и старта
        self._current_robot_item = None
        self._current_start_item = None
        
        # Сбрасываем выделение и режим рисования
        self.selected_item = None
        self.drawing_mode = None
        self.item_deselected.emit() # Сообщаем окну свойств
        
        logger.debug("Графическая сцена очищена")

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
        # Используем self.scene_manager.robot
        if not self.scene_manager.robot:
            logger.warning("robot_intersects_walls вызван без робота на сцене")
            return False
            
        robot_size = 50 # TODO: Получать размер из Robot?
        robot_rect = QRectF(robot_pos.x(), robot_pos.y(), robot_size, robot_size)
        
        # Используем self.scene_manager.walls
        for wall in self.scene_manager.walls:
            line = wall.line()
            thickness = wall.stroke_width
            if line_with_thickness_intersects_rect(line, robot_rect, thickness):
                logger.debug(f"Robot at {robot_pos} intersects with wall {wall.id}")
                return True
                
        return False

    @pyqtSlot(int, int)
    def update_robot_position(self, x, y):
        if self.scene_manager.robot:
            new_pos = QPointF(x, y)
            # Сначала проверяем в менеджере, можно ли туда ставить
            if self.scene_manager.robot_intersects_walls(new_pos):
                logger.warning(f"Нельзя переместить робота в ({x},{y}), пересечение со стеной.")
                # Восстанавливаем старые значения в properties
                self.properties_updated.emit(self.scene_manager.robot)
                return
            if not self.scene_manager._check_robot_within_scene(Robot(new_pos)): # Используем временный объект
                 logger.warning(f"Нельзя переместить робота в ({x},{y}), выходит за границы.")
                 self.properties_updated.emit(self.scene_manager.robot)
                 return

            self.scene_manager.robot.setPos(new_pos)
            self.properties_updated.emit(self.scene_manager.robot)
            logger.debug(f"Позиция робота обновлена на ({x}, {y})")
        else:
            logger.warning("Попытка обновить позицию несуществующего робота")

    @pyqtSlot(int)
    def update_robot_rotation(self, rotation):
        if self.scene_manager.robot:
            self.scene_manager.robot.setRotation(rotation)
            self.properties_updated.emit(self.scene_manager.robot)
            logger.debug(f"Направление робота обновлено на {rotation}")
        else:
            logger.warning("Попытка обновить направление несуществующего робота")

    @pyqtSlot(int, int)
    def update_wall_point1(self, x, y):
        if self.selected_item and isinstance(self.selected_item, Wall):
            line = self.selected_item.line()
            new_p1 = QPointF(x, y)
            new_line = QLineF(new_p1, line.p2())
            
            # Проверяем пересечение с роботом
            if self.scene_manager.robot and \
               self.scene_manager.wall_intersects_robot(new_p1.x(), new_p1.y(), line.x2(), line.y2(), self.selected_item.stroke_width):
                logger.warning(f"Нельзя переместить точку стены p1 в ({x},{y}), пересечение с роботом.")
                self.properties_updated.emit(self.selected_item)
                return
            # Проверяем выход за границы
            if not (-self.scene_width / 2 <= x <= self.scene_width / 2 and -self.scene_height / 2 <= y <= self.scene_height / 2):
                logger.warning(f"Нельзя переместить точку стены p1 в ({x},{y}), выходит за границы.")
                self.properties_updated.emit(self.selected_item)
                return
            
            self.selected_item.setLine(new_line)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"Позиция точки p1 стены {self.selected_item.id} обновлена на ({x}, {y})")
        else:
            logger.warning("Попытка обновить точку p1 невыделенной или неверной стены")

    @pyqtSlot(int, int)
    def update_wall_point2(self, x, y):
        if self.selected_item and isinstance(self.selected_item, Wall):
            line = self.selected_item.line()
            new_p2 = QPointF(x, y)
            new_line = QLineF(line.p1(), new_p2)
            
            # Проверяем пересечение с роботом
            if self.scene_manager.robot and \
               self.scene_manager.wall_intersects_robot(line.x1(), line.y1(), new_p2.x(), new_p2.y(), self.selected_item.stroke_width):
                logger.warning(f"Нельзя переместить точку стены p2 в ({x},{y}), пересечение с роботом.")
                self.properties_updated.emit(self.selected_item)
                return
            # Проверяем выход за границы
            if not (-self.scene_width / 2 <= x <= self.scene_width / 2 and -self.scene_height / 2 <= y <= self.scene_height / 2):
                logger.warning(f"Нельзя переместить точку стены p2 в ({x},{y}), выходит за границы.")
                self.properties_updated.emit(self.selected_item)
                return
            
            self.selected_item.setLine(new_line)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"Позиция точки p2 стены {self.selected_item.id} обновлена на ({x}, {y})")
        else:
            logger.warning("Попытка обновить точку p2 невыделенной или неверной стены")
            
    # --- Добавляем слот для обновления толщины стены --- 
    @pyqtSlot(int)
    def update_wall_stroke_width(self, width):
        if self.selected_item and isinstance(self.selected_item, Wall):
            # Проверяем пересечение с роботом при новой толщине
            line = self.selected_item.line()
            if self.scene_manager.robot and \
               self.scene_manager.wall_intersects_robot(line.x1(), line.y1(), line.x2(), line.y2(), width):
                logger.warning(f"Нельзя изменить толщину стены на {width}, пересечение с роботом.")
                self.properties_updated.emit(self.selected_item)
                return
                
            self.selected_item.set_stroke_width(width)
            self.properties_updated.emit(self.selected_item) # Обновляем свойства
            logger.debug(f"Толщина стены {self.selected_item.id} обновлена на {width}")
        else:
            logger.warning("Попытка обновить толщину невыделенной или неверной стены")
            
    @pyqtSlot(str)
    def update_wall_id(self, new_id):
        if self.selected_item and isinstance(self.selected_item, Wall):
            old_id = self.selected_item.id
            # TODO: Добавить валидацию ID в SceneManager или здесь?
            self.selected_item.id = new_id
            # Обновляем ID в менеджере? (Пока нет явной необходимости)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"ID стены {old_id} изменен на {new_id}")
        else:
            logger.warning("Попытка обновить ID невыделенной или неверной стены")

    @pyqtSlot(int, int)
    def update_region_position(self, x, y):
        if self.selected_item and isinstance(self.selected_item, Region):
            new_pos = QPointF(x, y)
            # TODO: Проверка границ/пересечений?
            self.selected_item.setPos(new_pos)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"Позиция региона {self.selected_item.id} обновлена на ({x}, {y})")
        else:
            logger.warning("Попытка обновить позицию невыделенного или неверного региона")

    @pyqtSlot(int, int)
    def update_region_size(self, width, height):
        if self.selected_item and isinstance(self.selected_item, Region):
            # TODO: Проверка границ/пересечений?
            self.selected_item.set_size(width, height)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"Размер региона {self.selected_item.id} обновлен на {width}x{height}")
        else:
            logger.warning("Попытка обновить размер невыделенного или неверного региона")

    @pyqtSlot(str)
    def update_region_color(self, color_hex):
        if self.selected_item and isinstance(self.selected_item, Region):
            self.selected_item.set_color(color_hex)
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"Цвет региона {self.selected_item.id} обновлен на {color_hex}")
        else:
            logger.warning("Попытка обновить цвет невыделенного или неверного региона")
            
    @pyqtSlot(str)
    def update_region_id(self, new_id):
        if self.selected_item and isinstance(self.selected_item, Region):
            old_id = self.selected_item.id
            # TODO: Добавить валидацию ID
            self.selected_item.id = new_id
            self.properties_updated.emit(self.selected_item)
            logger.debug(f"ID региона {old_id} изменен на {new_id}")
        else:
            logger.warning("Попытка обновить ID невыделенного или неверного региона")
            
    @pyqtSlot(float, float)
    def update_start_position_position(self, x, y):
        if self.scene_manager.start_position:
            new_pos = QPointF(x, y)
            # Проверка границ
            temp_start = StartPosition(new_pos)
            if not self.scene_manager._check_start_position_within_scene(temp_start):
                logger.warning(f"Нельзя переместить стартовую позицию в ({x},{y}), выходит за границы.")
                self.properties_updated.emit(self.scene_manager.start_position)
                StartPosition.reset_instance() # Сбрасываем временный объект
                return
            StartPosition.reset_instance() # Сбрасываем временный объект
            
            self.scene_manager.start_position.setPos(new_pos)
            self.properties_updated.emit(self.scene_manager.start_position)
            logger.debug(f"Позиция стартовой точки обновлена на ({x}, {y})")
        else:
            logger.warning("Попытка обновить позицию несуществующей стартовой точки")
            
    @pyqtSlot(float)
    def update_start_position_direction(self, direction):
        if self.scene_manager.start_position:
            self.scene_manager.start_position.setRotation(direction)
            self.properties_updated.emit(self.scene_manager.start_position)
            logger.debug(f"Направление стартовой точки обновлено на {direction}")
        else:
            logger.warning("Попытка обновить направление несуществующей стартовой точки")
