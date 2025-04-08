from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QTransform, QPainterPath, QPainterPathStroker
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
from contextlib import contextmanager
from .base_item import BaseSceneItem
import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Wall(BaseSceneItem):
    _next_id = 1  # Счетчик для генерации уникальных ID
    _existing_ids = set()  # Множество для хранения всех существующих ID

    def __init__(self, p1, p2, wall_id=None, width=10, color="#ff0000", is_temp=False):
        """
        Инициализация стены.
        
        Args:
            p1: Начальная точка стены (QPointF)
            p2: Конечная точка стены (QPointF)
            wall_id: Идентификатор стены (если None, будет сгенерирован)
            width: Толщина стены (по умолчанию 10)
            color: Цвет стены в HEX-формате
            is_temp: Флаг, указывающий, является ли стена временной (для проверок)
        """
        # Инициализируем линию ПЕРЕД вызовом super().__init__
        self._line = QLineF(p1.x(), p1.y(), p2.x(), p2.y())
        # Инициализируем толщину ПЕРЕД вызовом super().__init__
        self.stroke_width = width
        
        # Инициализация базового класса (теперь _line и stroke_width уже существуют)
        super().__init__(item_type="wall", item_id=wall_id, is_temp=is_temp, z_value=10)
        
        # Для временных стен не обновляем _existing_ids и не увеличиваем _next_id
        if wall_id:
            self.id = wall_id
            # Добавляем ID в множество только для не временных стен
            if not is_temp:
                Wall._existing_ids.add(self.id)
        else:
            if is_temp:
                # Для временных стен генерируем ID, но не добавляем его в _existing_ids
                self.id = f"temp_w{Wall._next_id}"
            else:
                # Для реальных стен генерируем ID и добавляем его в _existing_ids
                self.id = f"w{Wall._next_id}"
                Wall._next_id += 1
                Wall._existing_ids.add(self.id)

        # Настройка внешнего вида стены
        self.brick_width = 10
        self.brick_height = 5
        self.brick_color = QColor(color)
        self.mortar_color = QColor("#8b4513")
        self.brick_pattern = self.create_brick_pattern()

        # Атрибуты пера для контура (если понадобится)
        # self.stroke_color = "#ff000000"
        # self._pen = QPen(...) # Перо больше не нужно здесь

        # --- Возвращаем QGraphicsRectItem для отрисовки паттерна --- 
        self.brick_rect = QGraphicsRectItem(self)
        self.brick_rect.setBrush(QBrush(self.brick_pattern))
        self.brick_rect.setPen(QPen(Qt.GlobalColor.transparent)) # Без обводки самого прямоугольника
        self.brick_rect.setData(0, "its_wall") # Данные для идентификации
        self.brick_rect.setZValue(10) # Z-индекс такой же, как у Wall
        self.update_brick_rect_geometry() # Устанавливаем геометрию и трансформацию
        # -----------------------------------------------------------

        # Маркеры: радиус зависит от stroke_width
        marker_radius = max(3, self.stroke_width / 2) # Минимум 3, или половина толщины
        self.start_marker = QGraphicsEllipseItem(-marker_radius, -marker_radius, marker_radius*2, marker_radius*2, self)
        self.start_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.start_marker.setData(0, "wall_marker")
        self.start_marker.setPos(p1)
        self.start_marker.setZValue(12) # Поверх стены
        
        self.end_marker = QGraphicsEllipseItem(-marker_radius, -marker_radius, marker_radius*2, marker_radius*2, self)
        self.end_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.end_marker.setData(0, "wall_marker")
        self.end_marker.setPos(p2)
        self.end_marker.setZValue(12) # Поверх стены

        # Обновляем подсветку при наведении, если она была создана в super().__init__
        if hasattr(self, 'hover_rect') and self.hover_rect:
            self.update_hover_rect_geometry(self.hover_rect)

    def create_hover_highlight(self):
        """Создает подсветку при наведении для стены."""
        hover_rect = QGraphicsRectItem(self)
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        hover_rect.setData(0, "hover_highlight")
        # Обновляем геометрию подсветки
        self.update_hover_rect_geometry(hover_rect)
        hover_rect.setZValue(15)
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        hover_rect.hide()
        return hover_rect

    def update_hover_rect_geometry(self, hover_rect):
        """Обновляет геометрию и трансформацию прямоугольника подсветки."""
        line = self._line
        length = line.length()
        angle = line.angle()
        # --- Убираем padding --- 
        # padding = 5 
        # Используем только stroke_width
        rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
        # ----------------------
        hover_rect.setRect(rect)
        
        transform = QTransform()
        transform.translate(line.p1().x(), line.p1().y())
        transform.rotate(-angle)
        hover_rect.setTransform(transform)
        
    def create_brick_pattern(self):
        """
        Создает паттерн для кирпичной стены.
        """
        # Создаем изображение для паттерна
        pattern = QPixmap(self.brick_width * 2, self.brick_height * 2)
        pattern.fill(Qt.GlobalColor.transparent)

        # Рисуем кирпичи
        painter = QPainter(pattern)
        painter.setBrush(QBrush(self.brick_color))
        painter.setPen(QPen(self.mortar_color, 1)) # Уменьшил толщину раствора

        # Первый ряд кирпичей
        painter.drawRect(0, 0, self.brick_width, self.brick_height)
        painter.drawRect(self.brick_width, 0, self.brick_width, self.brick_height)

        # Второй ряд кирпичей (со смещением)
        painter.drawRect(self.brick_width // 2, self.brick_height, self.brick_width, self.brick_height)
        
        # --- Добавляем отрисовку половинок кирпичей --- 
        # Левая половинка второго ряда
        painter.drawRect(0, self.brick_height, self.brick_width // 2, self.brick_height)
        # Правая половинка второго ряда (отрезаем от полного кирпича)
        painter.drawRect(self.brick_width // 2 + self.brick_width, self.brick_height, self.brick_width // 2, self.brick_height)
        # ------------------------------------------------

        painter.end()
        return pattern
    
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку стены.
        :param enabled: Если True, стена выделяется зеленым контуром.
        """
        self.setZValue(11 if enabled else 10)
        # Обновляем внешний вид, чтобы перерисовалось выделение
        self.update()

    def boundingRect(self):
        """Возвращает прямоугольник, охватывающий стену"""
        return self.shape().controlPointRect()

    def paint(self, painter, option, widget):
        """Рисуем стену с паттерном и выделением."""
        # Отрисовка происходит через brick_rect, но рисуем выделение вручную
        if self.zValue() == 11: # Проверяем ZValue для выделения
            pen = QPen(QColor("#00ff22"), 2) # Зеленое, тонкое
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Рисуем контур вокруг формы стены
            path = self.shape()
            painter.drawPath(path)

    def shape(self):
        path = QPainterPath()
        # Создаем путь, соответствующий линии с ее толщиной
        # Используем QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(self.stroke_width + 4)  # +4 для небольшого запаса
        stroker.setCapStyle(Qt.PenCapStyle.FlatCap)
        
        linePath = QPainterPath()
        linePath.moveTo(self._line.p1())
        linePath.lineTo(self._line.p2())
        
        # Создаем контур с помощью экземпляра stroker
        path = stroker.createStroke(linePath)
        return path

    def line(self):
        """Возвращает линию стены"""
        return self._line

    def setLine(self, line):
        """Устанавливает новую линию для стены"""
        if self._line != line:
            self.prepareGeometryChange()
            self._line = line
            # Обновляем позицию маркеров
            self.start_marker.setPos(line.p1())
            self.end_marker.setPos(line.p2())
            # Обновляем геометрию brick_rect
            self.update_brick_rect_geometry()
            # Обновляем геометрию подсветки при наведении
            if hasattr(self, 'hover_rect') and self.hover_rect:
                self.update_hover_rect_geometry(self.hover_rect)
            self.update()  # Перерисовываем элемент

    def set_stroke_width(self, width):
        """Устанавливает толщину линии стены."""
        if self.stroke_width != width:
            self.prepareGeometryChange()
            self.stroke_width = width
            # Обновляем геометрию brick_rect
            self.update_brick_rect_geometry()
            # Обновляем размер маркеров
            marker_radius = max(3, self.stroke_width / 2)
            rect = QRectF(-marker_radius, -marker_radius, marker_radius*2, marker_radius*2)
            self.start_marker.setRect(rect)
            self.end_marker.setRect(rect)
            # Обновляем геометрию подсветки при наведении
            if hasattr(self, 'hover_rect') and self.hover_rect:
                self.update_hover_rect_geometry(self.hover_rect)
            self.update() # Перерисовываем элемент 

    # --- Добавляем метод для обновления геометрии brick_rect --- 
    def update_brick_rect_geometry(self):
        """Обновляет геометрию и трансформацию прямоугольника с паттерном."""
        line = self._line
        length = line.length()
        angle = line.angle()
        # Прямоугольник центрирован относительно линии
        rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
        self.brick_rect.setRect(rect)
        
        transform = QTransform()
        transform.translate(line.p1().x(), line.p1().y())
        transform.rotate(-angle)
        self.brick_rect.setTransform(transform)
    # ------------------------------------------------------------- 