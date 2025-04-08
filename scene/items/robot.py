from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter, QTransform, QPen, QBrush, QPainterPath, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QRectF, Qt, QPointF, QSizeF
from .base_item import BaseSceneItem
import logging
import os # Импортируем os для работы с путями

logger = logging.getLogger(__name__)

# Определяем путь к директории с изображениями относительно этого файла
script_dir = os.path.dirname(os.path.abspath(__file__))
# Путь: robot.py -> items -> scene -> корень -> images
image_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'images'))
robot_image_path = os.path.join(image_dir, 'robot.svg')
logger.debug(f"Путь к изображению робота: {robot_image_path}")

class Robot(BaseSceneItem):
    """
    Класс робота. Реализует паттерн Singleton.
    """
    
    _id = "trikKitRobot"
    _instance = None
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Robot, cls).__new__(cls)
            logger.debug("Создан первый экземпляр робота")
        return cls._instance
    
    def __init__(self, pos, robot_id=None, name="", direction=0):
        if not hasattr(self, '_is_initialized') or not self._is_initialized:
            super().__init__(item_type="robot", item_id=self._id, z_value=1000)
            
            # Создаем дочерний QGraphicsPixmapItem для отображения
            self.pixmap_item = QGraphicsPixmapItem(self) 
            # Устанавливаем точку трансформации для дочернего элемента
            self.pixmap_item.setTransformOriginPoint(25, 25) 
            # Важно: отключаем взаимодействие с дочерним элементом,
            # чтобы родительский Robot ловил все события
            self.pixmap_item.setAcceptHoverEvents(False)
            self.pixmap_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.pixmap_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            
            self.renderer = QSvgRenderer()
            self.name = name
            self.update_appearance()
            self.setRotation(direction)
            self._is_initialized = True
            logger.debug(f"Робот инициализирован с id={self.id}")
        
        self.setPos(pos)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        if name:
            self.name = name
        if direction != 0:
            self.setRotation(direction)
    
    def create_hover_highlight(self):
        """Создает подсветку при наведении для робота."""
        hover_rect = QGraphicsRectItem(0, 0, 50, 50, self)
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        hover_rect.setData(0, "hover_highlight")
        hover_rect.setTransformOriginPoint(25, 25)
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        hover_rect.hide()
        return hover_rect
        
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку робота при выделении.
        """
        if enabled:
            if not hasattr(self, 'highlight_rect') or not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(0, 0, 50, 50, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
                self.highlight_rect.setTransformOriginPoint(25, 25)
            self.highlight_rect.show()
            self.set_hover_highlight(False)
        elif hasattr(self, 'highlight_rect') and self.highlight_rect:
            self.highlight_rect.hide()
            if self._is_hovered:
                self.set_hover_highlight(True)
    
    def boundingRect(self):
        return self.childrenBoundingRect()
    
    def paint(self, painter, option, widget):
        """Отрисовка робота не требуется, так как используется QGraphicsPixmapItem"""
        pass
    
    def shape(self):
        """
        Переопределяем shape(), чтобы робот реагировал на нажатие в любой точке изображения.
        """
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    def set_name(self, name):
        """
        Устанавливает имя робота.
        :param name: Новое имя робота.
        """
        self.name = name
    
    def update_appearance(self):
        """Обновляет внешний вид робота."""
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Используем абсолютный путь, построенный относительно файла
        if self.renderer.load(robot_image_path): 
            painter = QPainter(pixmap)
            self.renderer.render(painter, QRectF(0, 0, 50, 50))
            painter.end()
        else:
            logger.error(f"Не удалось загрузить изображение робота: {robot_image_path}")
            logger.debug("Рисуем синий квадрат вместо изображения робота.")
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(Qt.GlobalColor.blue))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(0, 0, 50, 50)
            painter.drawLine(0, 0, 50, 50)
            painter.drawLine(50, 0, 0, 50)
            painter.end()
        
        # Устанавливаем pixmap для дочернего элемента
        self.pixmap_item.setPixmap(pixmap)
        
        # Точка трансформации устанавливается для Robot (родителя)
        self.setTransformOriginPoint(25, 25)
    
    @classmethod
    def reset_instance(cls):
        """
        Сбрасывает экземпляр робота.
        Этот метод следует вызывать только при полной очистке сцены.
        """
        cls._instance = None
        logger.debug("Экземпляр робота сброшен") 