from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QTransform
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
        # Инициализация базового класса
        super().__init__(item_type="wall", item_id=wall_id, is_temp=is_temp, z_value=10)
        
        # Создаем линию
        self._line = QLineF(p1.x(), p1.y(), p2.x(), p2.y())
        
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
        self.brick_width = 10  # Ширина кирпича
        self.brick_height = 5  # Высота кирпича
        self.brick_color = QColor(color)  # Цвет кирпича
        self.mortar_color = QColor("#8b4513")  # Цвет раствора между кирпичами

        # Создаем паттерн для кирпичной стены
        self.brick_pattern = self.create_brick_pattern()

        # Атрибуты стены
        self.stroke_color = "#ff000000"  # Цвет обводки (по умолчанию черный)
        self.stroke_width = width  # Ширина обводки (по умолчанию 10)

        # Настройка пера
        self._normal_pen = QPen(QColor(self.stroke_color), self.stroke_width)  # Паттерн для линии
        self._highlight_pen = QPen(QColor("#00ff22"), self.stroke_width+5)  # Контур при выделении
        self.setPen(self._normal_pen)

        # Создаем прямоугольник с паттерном кирпичной стены
        self.brick_rect = QGraphicsRectItem(self)
        self.brick_rect.setBrush(QBrush(self.create_brick_pattern()))
        self.brick_rect.setPen(QPen(Qt.GlobalColor.transparent))  # Прозрачная обводка
        self.brick_rect.setData(0, "its_wall")
        self.brick_rect.setZValue(12)

        # Обновляем прямоугольник в соответствии с линией
        self.update_brick_rect()

        # Добавляем маркеры на концах стены
        self.start_marker = QGraphicsEllipseItem(p1.x() - self.stroke_width // 2 - 1, 
                                                p1.y() - self.stroke_width // 2 - 1, 
                                                self.stroke_width + 2, 
                                                self.stroke_width + 2, self)
        self.start_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.start_marker.setData(0, "wall_marker")
        
        self.end_marker = QGraphicsEllipseItem(p2.x() - self.stroke_width // 2 - 1, 
                                              p2.y() - self.stroke_width // 2 - 1, 
                                              self.stroke_width + 2, 
                                              self.stroke_width + 2, self)
        self.end_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.end_marker.setData(0, "wall_marker")

    def create_hover_highlight(self):
        """Создает подсветку при наведении для стены."""
        line = self._line
        length = line.length()
        angle = line.angle()
        
        # Создаем прямоугольник для подсветки при наведении
        hover_rect = QGraphicsRectItem(self)
        
        # Настраиваем перо с пунктирной линией синего цвета
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        # Устанавливаем данные для идентификации объекта при кликах
        hover_rect.setData(0, "hover_highlight")
        
        # Создаем прямоугольник, покрывающий линию
        rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
        hover_rect.setRect(rect)
        
        # Применяем поворот к прямоугольнику подсветки
        transform = QTransform()
        transform.translate(line.p1().x(), line.p1().y())
        transform.rotate(-angle)
        hover_rect.setTransform(transform)
        hover_rect.setZValue(15)  # Между стеной и выделением
        
        # Отключаем обработку событий мыши для прямоугольника подсветки
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsPanel, False)
        
        # Скрываем прямоугольник по умолчанию
        hover_rect.hide()
        
        return hover_rect

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
        painter.setPen(QPen(self.mortar_color, 2))

        # Первый ряд кирпичей
        painter.drawRect(0, 0, self.brick_width, self.brick_height)
        painter.drawRect(self.brick_width, 0, self.brick_width, self.brick_height)

        # Второй ряд кирпичей (со смещением)
        painter.drawRect(self.brick_width // 2, self.brick_height, self.brick_width, self.brick_height)
        painter.drawRect(self.brick_width // 2 + self.brick_width, self.brick_height, self.brick_width, self.brick_height)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawRect(0, self.brick_height, self.brick_width // 2, self.brick_height)   

        painter.end()
        return pattern
    
    def update_brick_rect(self):
        """
        Обновляет прямоугольник с паттерном в соответствии с линией.
        """
        line = self._line
        length = line.length()
        angle = line.angle()

        # Создаем прямоугольник, покрывающий линию
        rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
        self.brick_rect.setRect(rect)

        # Поворачиваем прямоугольник в соответствии с углом линии
        transform = QTransform()
        transform.translate(line.p1().x(), line.p1().y())
        transform.rotate(-angle)
        self.brick_rect.setTransform(transform)
        
        # Обновляем подсветку при наведении, если она существует
        if hasattr(self, 'hover_rect') and self.hover_rect:
            rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
            self.hover_rect.setRect(rect)
            
            # Применяем поворот к прямоугольнику подсветки
            transform = QTransform()
            transform.translate(line.p1().x(), line.p1().y())
            transform.rotate(-angle)
            self.hover_rect.setTransform(transform)

    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку стены.
        :param enabled: Если True, стена выделяется зеленым контуром.
        """
        self.setPen(self._highlight_pen if enabled else self._normal_pen)

    def boundingRect(self):
        """Возвращает прямоугольник, охватывающий стену"""
        return self.childrenBoundingRect()

    def paint(self, painter, option, widget):
        """Отрисовка стены не требуется, так как используется QGraphicsRectItem"""
        pass

    def line(self):
        """Возвращает линию стены"""
        return self._line

    def setLine(self, line):
        """Устанавливает новую линию для стены"""
        self._line = line
        self.update_brick_rect() 