from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsItemGroup, QGraphicsItem, QMessageBox
)
from PyQt6.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QImage, QTransform, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal
from PyQt6.QtSvg import QSvgRenderer
from robot import Robot
from wall import Wall
from region import Region
from styles import AppStyles

import logging

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
        
        # Создаем группы для слоев
        self.grid_layer = QGraphicsItemGroup()
        self.axes_layer = QGraphicsItemGroup()
        self.objects_layer = QGraphicsItemGroup()
        
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
        self.wall_start = None  # Добавляем инициализацию wall_start

        self.region_start = None  # Начальная точка региона
        self.temp_region = None  # Временный прямоугольник для отрисовки региона
        
        # Состояния объектов
        self.walls = []
        self.regions = []
        self.robot_model = None  
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
        """Выделяеv объект"""
        # Проверяем, не выделяем ли тот же объект
        logger.debug(f"Selecting item: {item}, а был выделен {self.selected_item}")
        if item == self.selected_item:
            logger.debug(f"Item {item} is already selected, skipping")
            return
        if self.selected_item:
            self.deselect_item()

        if isinstance(item, (Wall, Robot, Region)):
            logger.debug(f"Selecting item: {item}")
            self.selected_item = item
            self.selected_item.set_highlight(True)
            self.item_selected.emit(item)

    def deselect_item(self):
        """Снимает выделение с объекта."""
        if self.selected_item:
            logger.debug(f"Deselecting item: {self.selected_item}")
            if isinstance(self.selected_item, (Wall, Robot, Region)):
                self.selected_item.set_highlight(False)
            self.selected_item = None
            self.item_deselected.emit()
    
    def wall_intersects_robot(self, x1, y1, x2, y2):
        """Проверяет, пересекается ли стена с роботом."""
        if not self.robot_model: 
            return False
            
        robot_rect = self.robot_model.boundingRect()
        # Учитываем позицию робота при проверке пересечения
        robot_rect.translate(self.robot_model.pos())
        
        # Линия стены
        wall_line = QLineF(QPointF(x1, y1), QPointF(x2, y2))
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
        
        # Проверяем пересечение с роботом
        if self.wall_intersects_robot(p1.x(), p1.y(), p2.x(), p2.y()):
            logger.warning("Стена пересекается с роботом - отмена добавления")
            return None
            
        # Создаем новую стену
        wall = Wall(p1, p2, wall_id)
        
        # Проверяем, находится ли стена в пределах сцены
        if not self.check_object_within_scene(wall):
            logger.warning("Стена выходит за границы сцены - отмена добавления")
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
        
    def add_region(self, rect, region_id=None, color=None):
        """
        Добавляет регион на сцену с заданными параметрами.
        
        Args:
            rect: Прямоугольник региона (QRectF)
            region_id: Идентификатор региона (если None, будет сгенерирован)
            color: Цвет региона (если None, будет использован цвет по умолчанию)
            
        Returns:
            Region: Добавленный регион или None, если добавление не удалось
        """
        logger.debug(f"Добавление региона: {rect}, id={region_id}, color={color}")
        
        # Извлекаем позицию и размеры из прямоугольника
        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()
        
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
        
        logger.debug(f"Регион успешно добавлен с id={region.id}, позиция=({x}, {y}), размер=({width}, {height})")
        
        # Автоматически выделяем созданный регион
        self.select_item(region)
        
        return region

    def init_robot(self, pos):
        logger.debug(f"Setting robot position to {pos}")
        if self.robot_model is not None:
            logger.debug("Removing existing robot from scene")
            self.scene().removeItem(self.robot_model)
        self.robot_model = Robot(pos)
        self.objects_layer.addToGroup(self.robot_model)

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

        return True
    
    def check_object_within_scene(self, item):
        """
        Проверяет, находится ли объект в пределах сцены.
        :param item: Объект для проверки (Wall, Region или Robot).
        :return: True, если объект находится в пределах сцены, иначе False.
        """
        if isinstance(item, Wall):
            # Для стены проверяем обе точки
            line = item.line()
            return (
                -self.scene_width / 2 <= line.x1() <= self.scene_width / 2 and
                -self.scene_width / 2 <= line.x2() <= self.scene_width / 2 and
                -self.scene_height / 2 <= line.y1() <= self.scene_height / 2 and
                -self.scene_height / 2 <= line.y2() <= self.scene_height / 2
            )
        elif isinstance(item, Region):
            # Для региона проверяем, что все точки находятся в пределах сцены
            path = item.path()
            # Получаем ограничивающий прямоугольник
            rect = path.boundingRect()
            pos = item.pos()
            
            # Вычисляем координаты углов региона
            top_left = (pos.x() + rect.x(), pos.y() + rect.y())
            top_right = (pos.x() + rect.x() + rect.width(), pos.y() + rect.y())
            bottom_left = (pos.x() + rect.x(), pos.y() + rect.y() + rect.height())
            bottom_right = (pos.x() + rect.x() + rect.width(), pos.y() + rect.y() + rect.height())
            
            logger.debug(f"Region bounds check: TL={top_left}, TR={top_right}, BL={bottom_left}, BR={bottom_right}")
            logger.debug(f"Scene bounds: x=({-self.scene_width/2}, {self.scene_width/2}), y=({-self.scene_height/2}, {self.scene_height/2})")
            
            # Проверяем, что все углы региона находятся в пределах сцены
            return (
                -self.scene_width / 2 <= top_left[0] <= self.scene_width / 2 and
                -self.scene_width / 2 <= top_right[0] <= self.scene_width / 2 and
                -self.scene_width / 2 <= bottom_left[0] <= self.scene_width / 2 and
                -self.scene_width / 2 <= bottom_right[0] <= self.scene_width / 2 and
                -self.scene_height / 2 <= top_left[1] <= self.scene_height / 2 and
                -self.scene_height / 2 <= top_right[1] <= self.scene_height / 2 and
                -self.scene_height / 2 <= bottom_left[1] <= self.scene_height / 2 and
                -self.scene_height / 2 <= bottom_right[1] <= self.scene_height / 2
            )
        elif isinstance(item, Robot):
            # Для робота проверяем его позицию и размеры
            # Размер робота фиксирован - 50x50 пикселей
            pos = item.pos()
            logger.debug(f"Checking robot position: pos=({pos.x()}, {pos.y()})")
            logger.debug(f"Scene bounds: x=({-self.scene_width/2}, {self.scene_width/2}), y=({-self.scene_height/2}, {self.scene_height/2})")
            
            # Проверяем, что робот полностью находится в пределах сцены
            return (
                -self.scene_width / 2 <= pos.x() <= self.scene_width / 2 - 50 and
                -self.scene_height / 2 <= pos.y() <= self.scene_height / 2 - 50
            )
        return False
    
    def mousePressEvent(self, event):
        posOriginal = self.mapToScene(event.pos()) # оригинальные координаты
        pos = self.snap_to_grid(posOriginal) # координаты с привязкой к сетке

        item = self.scene().itemAt(posOriginal, self.transform())
        print("click", type(item))
        if event.button() == Qt.MouseButton.LeftButton:
            
            # Если в режиме редактирования и нажали на объект, меняем курсор на "кулачок"
            if self.edit_mode and item and (isinstance(item, (Robot, Region)) or 
                      (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker")) or 
                      (item.parentItem() and isinstance(item.parentItem(), (Robot, Region)))):
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            # Проверка клика по выделяемому объекту или его дочернему элементу
            if item:
                # Проверяем, не является ли item частью уже выделенного объекта
                parent_item = item.parentItem()
                if parent_item and parent_item == self.selected_item:
                    # Если кликнули на дочерний элемент выделенного объекта (например, рамку выделения)
                    target_item = parent_item
                # Иначе проверяем тип объекта
                elif isinstance(item, (Robot, Region)) or (hasattr(item, 'data') and item.data(0) in ["its_wall", "wall_marker"]):
                    # Выделяем объект или его родительский элемент
                    if isinstance(item, (Robot, Region)):
                        target_item = item
                    else:
                        target_item = item.parentItem()
                    
                    self.select_item(target_item)
                else:
                    # Клик по другому объекту, не являющемуся выделяемым
                    # Не будем снимать выделение при клике на объекты вне сцены (например, кнопки подтверждения)
                    if item.scene() == self.scene():
                        self.deselect_item()
            else:
                # Клик по пустому месту
                self.deselect_item()

            # Обработка перемещения объектов в режиме редактирования
            if self.edit_mode:
                if item and hasattr(item, 'data') and item.data(0) == "wall_marker":  # Проверяем свойство
                    self.selected_marker = item
                    self.dragging_item = None  # Сбрасываем перетаскиваемый объект
                    return
                elif item and hasattr(item, 'data') and item.data(0) == "its_wall":
                    self.dragging_item = item.parentItem()
                    # Сохраняем точку захвата
                    self.grab_point = pos
                    # Сохраняем начальные координаты стены
                    line = self.dragging_item.line()
                    self.initial_line = QLineF(line.x1(), line.y1(), line.x2(), line.y2())
                    return
                elif item and (isinstance(item, (Robot, Region)) or 
                              (parent_item and isinstance(parent_item, (Robot, Region)))):
                    # Если кликнули на робота/регион или на его дочерний элемент
                    drag_item = item if isinstance(item, (Robot, Region)) else parent_item
                    self.dragging_item = drag_item
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
        
        # Меняем курсор при наведении на объекты (редактируемые)
        if self.edit_mode:
            if item and (isinstance(item, (Robot, Region)) or 
                        (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker")) or 
                        (item.parentItem() and isinstance(item.parentItem(), (Robot, Region)))):
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
            if item and (isinstance(item, (Robot, Region)) or 
                       (hasattr(item, 'data') and (item.data(0) == "its_wall" or item.data(0) == "wall_marker")) or 
                       (item.parentItem() and isinstance(item.parentItem(), (Robot, Region)))):
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
                    temp_robot = Robot(new_pos)
                    logger.debug(f"from: {temp_robot.x(), temp_robot.y(), temp_robot.x() + temp_robot.boundingRect().width(), temp_robot.y() + temp_robot.boundingRect().height()}")  
                    if not self.check_object_within_scene(temp_robot):
                        logger.debug(f"ERR robot would be out of bounds")
                        return
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
                temp_wall = Wall(QPointF(new_pos_x1, new_pos_y1), QPointF(new_pos_x2, new_pos_y2))
                
                # Обновляем саму линию стены, смещая обе точки, если нет пересечения с роботом
                if self.wall_intersects_robot(new_pos_x1, new_pos_y1, new_pos_x2, new_pos_y2) or not self.check_object_within_scene(temp_wall):
                    logger.debug(f"ERR robot intersects or wall would be out of bounds")
                    return 
                else:
                    with self.dragging_item.updating():
                        self.dragging_item.setLine(
                            new_pos_x1,
                            new_pos_y1,
                            new_pos_x2,
                            new_pos_y2
                        )
                    # Обновляем свойства в окне свойств в режиме реального времени
                    self.properties_window.update_properties(self.dragging_item)
            return
        elif self.edit_mode and self.selected_marker:            
            wall = self.selected_marker.parentItem()
            if self.selected_marker == wall.start_marker:
                logger.debug(f"Moving wall start marker to {pos}")
                if self.wall_intersects_robot(pos.x(), pos.y(), wall.line().x2(), wall.line().y2()):
                    logger.debug(f"ERR robot intersects")
                    return 
                else:
                    with wall.updating():
                        wall.setLine(pos.x(), pos.y(), wall.line().x2(), wall.line().y2())
                    self.properties_window.update_properties(wall)  # Обновляем свойства
            else:
                if self.wall_intersects_robot(wall.line().x1(), wall.line().y1(), pos.x(), pos.y()):
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
        if self.robot_model:
            # Создаем временный объект для проверки границ сцены
            temp_robot = Robot(QPointF(x, y))
            if not self.check_object_within_scene(temp_robot):
                logger.warning(f"Robot position update to ({x}, {y}) rejected - would be out of scene bounds")
                # Показываем предупреждение о выходе за границы сцены
                QMessageBox.warning(
                    None,
                    "Ошибка",
                    f"Робот выйдет за границы сцены. Пожалуйста, укажите другие координаты.",
                    QMessageBox.StandardButton.Ok
                )
                # Обновляем свойства с правильной позицией
                self.properties_updated.emit(self.robot_model)
                return False
            
            # Если проверка пройдена, обновляем позицию
            self.robot_model.setPos(x, y)
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
            
            # Проверяем пересечение с роботом, передавая координаты
            if self.wall_intersects_robot(x1, y1, x2, y2):
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
            
            # Создаем временную стену для проверки границ сцены
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2))
            if not self.check_object_within_scene(temp_wall):
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
            
            # Проверяем пересечение с роботом, передавая координаты
            if self.wall_intersects_robot(x1, y1, x2, y2):
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
            
            # Создаем временную стену для проверки границ сцены
            temp_wall = Wall(QPointF(x1, y1), QPointF(x2, y2))
            if not self.check_object_within_scene(temp_wall):
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
        self.snap_to_grid_enabled = enabled
    
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
        Очищает сцену от всех объектов: стен, регионов и робота.
        """
        logger.debug("Очистка сцены...")
        
        # Удаляем все стены
        for wall in self.walls[:]:
            wall.remove_from_scene()
            self.walls.remove(wall)
            
        # Удаляем все регионы
        for region in self.regions[:]:
            region.remove_from_scene()
            self.regions.remove(region)
            
        # Удаляем робота
        if self.robot_model:
            self.scene().removeItem(self.robot_model)
            # Сбрасываем экземпляр робота
            Robot.reset_instance()
            self.robot_model = None
            
        # Сбрасываем выделение
        self.selected_item = None
        self.selected_marker = None
        
        # Обновляем view
        self.scene().update()
        logger.debug("Сцена очищена")
        
        # Сигнализируем о снятии выделения
        self.item_deselected.emit()

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
        
        logger.debug(f"Робот успешно размещен в позиции {position}, id={self.robot_model.id}")
        return self.robot_model
        
    def distance_to_line(self, point, line):
        """
        Вычисляет расстояние от точки до линии.
        
        Args:
            point: Точка (QPointF)
            line: Линия (QLineF)
            
        Returns:
            float: Расстояние от точки до линии
        """
        # Формула для расстояния от точки до линии
        x0, y0 = point.x(), point.y()
        x1, y1 = line.x1(), line.y1()
        x2, y2 = line.x2(), line.y2()
        
        # Если точки отрезка совпадают, возвращаем расстояние до одной из них
        if x1 == x2 and y1 == y2:
            return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5
            
        # Вычисляем расстояние
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        
        return numerator / denominator

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
