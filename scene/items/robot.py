from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter, QTransform, QPen, QBrush, QPainterPath, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QRectF, Qt, QPointF, QSizeF
from .base_item import BaseSceneItem
import logging

logger = logging.getLogger(__name__)

class Robot(BaseSceneItem):
    """
    Класс робота. Реализует паттерн Singleton.
    """
    
    # Фиксированный ID для робота
    _id = "trikKitRobot"
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        """
        Реализация паттерна Singleton: гарантируем, что существует только один экземпляр робота.
        """
        if cls._instance is None:
            cls._instance = super(Robot, cls).__new__(cls)
            logger.debug("Создан первый экземпляр робота")
        return cls._instance
    
    def __init__(self, pos, robot_id=None, name="", direction=0):
        """
        Инициализация робота.
        
        Args:
            pos: Позиция робота (QPointF)
            robot_id: Уникальный идентификатор робота (игнорируется, всегда используется "trikKitRobot")
            name: Имя робота
            direction: Направление робота в градусах
        """
        # Проверяем, был ли уже инициализирован экземпляр
        if not hasattr(self, '_is_initialized') or not self._is_initialized:
            super().__init__(item_type="robot", item_id=self._id, z_value=1000)
            
            # Инициализация SVG-рендерера
            self.renderer = QSvgRenderer()
            
            # Настройка свойств робота
            self.name = name
            
            # Обновление внешнего вида робота и настройка точки трансформации
            self.update_appearance()   
            
            # Настройка отображения
            self.setRotation(direction)
            
            # Помечаем, что экземпляр уже инициализирован
            self._is_initialized = True
            
            logger.debug(f"Робот инициализирован с id={self.id}")
        
        # Обновляем позицию при каждом вызове
        self.setPos(pos)
        
        # Включаем обработку событий мыши
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        # Обновляем свойства, если они переданы
        if name:
            self.name = name
        if direction != 0:
            self.setRotation(direction)
    
    def create_hover_highlight(self):
        """Создает подсветку при наведении для робота."""
        hover_rect = QGraphicsRectItem(0, 0, 50, 50, self)
        
        # Настраиваем перо с пунктирной линией синего цвета
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        # Устанавливаем данные для идентификации объекта при кликах
        hover_rect.setData(0, "hover_highlight")
        
        # Устанавливаем точку трансформации для выделения
        hover_rect.setTransformOriginPoint(25, 25)
        
        # Отключаем обработку событий мыши для прямоугольника подсветки
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        # Скрываем прямоугольник по умолчанию
        hover_rect.hide()
        
        return hover_rect
        
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку робота при выделении.
        :param enabled: Если True, робот выделяется прямоугольником.
        """
        if enabled:
            # Создаем прямоугольник для выделения
            if not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(0, 0, 50, 50, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
                
                # Устанавливаем точку трансформации для выделения
                self.highlight_rect.setTransformOriginPoint(25, 25)
            
            # Показываем выделение
            self.highlight_rect.show()
            
            # Скрываем обводку при наведении, если она есть
            self.set_hover_highlight(False)
            
        elif hasattr(self, 'highlight_rect') and self.highlight_rect:
            # Скрываем прямоугольник выделения
            self.highlight_rect.hide()
            
            # Если сейчас курсор наведен на объект, показываем обводку при наведении
            if self._is_hovered:
                self.set_hover_highlight(True)
    
    def boundingRect(self):
        """Возвращает прямоугольник, охватывающий робота"""
        return QRectF(0, 0, 50, 50)
    
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
        # Создаем пустой pixmap для начала
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Пытаемся загрузить SVG файл
        if self.renderer.load("images/robot.svg"):  # Используем SVG
            painter = QPainter(pixmap)
            
            # Рендерим SVG без применения поворота здесь
            # (поворот будет применен через setRotation)
            self.renderer.render(painter, QRectF(0, 0, 50, 50))
            painter.end()
        else:
            # Если SVG/PNG не загрузился, рисуем синий квадрат
            logger.debug("Изображение не загружено. Рисуем синий квадрат.")
            painter = QPainter(pixmap)
            
            # Рисуем синий квадрат и диагонали без применения поворота
            painter.setBrush(QBrush(Qt.GlobalColor.blue))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(0, 0, 50, 50)
            painter.drawLine(0, 0, 50, 50)
            painter.drawLine(50, 0, 0, 50)
            painter.end()
        
        # Устанавливаем pixmap
        self.setPixmap(pixmap)
        
        # Устанавливаем точку трансформации в центр изображения
        self.setTransformOriginPoint(25, 25)  # 50/2 = 25 (размер робота 50x50)
    
    @classmethod
    def reset_instance(cls):
        """
        Сбрасывает экземпляр робота.
        Этот метод следует вызывать только при полной очистке сцены.
        """
        cls._instance = None
        logger.debug("Экземпляр робота сброшен") 