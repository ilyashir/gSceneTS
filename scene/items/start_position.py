from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter, QTransform, QPen, QBrush, QPainterPath, QColor
from PyQt6.QtCore import QRectF, Qt, QPointF, QSizeF
from .base_item import BaseSceneItem
import logging

logger = logging.getLogger(__name__)

class StartPosition(BaseSceneItem):
    """
    Класс стартовой позиции. Реализует паттерн Singleton.
    Рисует красный крестик 25x25.
    Работает с координатами центра.
    """
    
    _id = "startPosition"
    _instance = None
    
    # Размер элемента
    ITEM_SIZE = 25
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StartPosition, cls).__new__(cls)
            logger.debug("Создан первый экземпляр стартовой позиции")
        return cls._instance
    
    def __init__(self, pos, direction=0):
        if not hasattr(self, '_is_initialized') or not self._is_initialized:
            super().__init__(item_type="start_position", item_id=self._id, z_value=900)
            
            # Устанавливаем точку трансформации в центр
            center = self.ITEM_SIZE / 2
            self.setTransformOriginPoint(center, center)
            
            self.setRotation(direction)
            self._is_initialized = True
            logger.debug(f"Стартовая позиция инициализирована с id={self.id}")
        
        # Используем переопределенный setPos, который ожидает центр
        self.setPos(pos) 
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        if direction != 0:
            self.setRotation(direction)

    def pos(self) -> QPointF:
        """Возвращает координаты центра элемента."""
        center_offset = self.ITEM_SIZE / 2
        # Получаем позицию левого верхнего угла от базового класса
        top_left_pos = super().pos()
        # Возвращаем позицию центра
        return top_left_pos + QPointF(center_offset, center_offset)

    def setPos(self, *args):
        """Устанавливает позицию элемента по его центру."""
        if len(args) == 1 and isinstance(args[0], QPointF):
            center_pos = args[0]
        elif len(args) == 2:
            center_pos = QPointF(args[0], args[1])
        else:
            raise TypeError("setPos принимает QPointF или две координаты (x, y)")

        center_offset = self.ITEM_SIZE / 2
        # Вычисляем позицию левого верхнего угла
        top_left_pos = center_pos - QPointF(center_offset, center_offset)
        # Устанавливаем позицию левого верхнего угла с помощью базового класса
        super().setPos(top_left_pos)
    
    def create_hover_highlight(self):
        # Используем ITEM_SIZE
        hover_rect = QGraphicsRectItem(0, 0, self.ITEM_SIZE, self.ITEM_SIZE, self)
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        hover_rect.setData(0, "hover_highlight")
        hover_rect.setTransformOriginPoint(self.ITEM_SIZE / 2, self.ITEM_SIZE / 2)
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        hover_rect.hide()
        return hover_rect
        
    def set_highlight(self, enabled):
        # Используем ITEM_SIZE
        size = self.ITEM_SIZE
        if enabled:
            if not hasattr(self, 'highlight_rect') or not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(0, 0, size, size, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
                self.highlight_rect.setTransformOriginPoint(size / 2, size / 2)
            self.highlight_rect.show()
            self.set_hover_highlight(False)
        elif hasattr(self, 'highlight_rect') and self.highlight_rect:
            self.highlight_rect.hide()
            if self._is_hovered:
                self.set_hover_highlight(True)
    
    def boundingRect(self):
        # Возвращаем фиксированный размер
        return QRectF(0, 0, self.ITEM_SIZE, self.ITEM_SIZE)
    
    def paint(self, painter, option, widget):
        pen = QPen(Qt.GlobalColor.red, 2) # Красный цвет, толщина 2
        painter.setPen(pen)
        size = self.ITEM_SIZE
        # Рисуем две диагональные линии
        painter.drawLine(0, 0, size, size)
        painter.drawLine(size, 0, 0, size)
    
    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    @classmethod
    def reset_instance(cls):
        cls._instance = None
        logger.debug("Экземпляр стартовой позиции сброшен") 