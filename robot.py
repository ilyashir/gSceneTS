from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QTransform, QPen, QBrush, QPainterPath, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QRectF, Qt, QPointF, QSizeF
import logging

logger = logging.getLogger(__name__)

class Robot(QGraphicsPixmapItem):
    # Статический атрибут для хранения единственного экземпляра
    _instance = None
    # Фиксированный ID для робота
    _id = "trikKitRobot"
    
    def __new__(cls, pos, robot_id=None, name="", direction=0):
        """
        Реализует паттерн Singleton для класса Robot.
        Позволяет создать только один экземпляр робота.
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
            robot_id: Уникальный идентификатор робота (игнорируется, всегда используется "m1")
            name: Имя робота
            direction: Направление робота в градусах
        """
        # Проверяем, был ли уже инициализирован экземпляр
        if not hasattr(self, '_is_initialized') or not self._is_initialized:
            super().__init__()
            
            # Инициализация SVG-рендерера
            self.renderer = QSvgRenderer()
            
            # ID робота всегда "m1"
            self._id = "trikKitRobot"
            
            # Настройка свойств робота
            self.name = name
            self.direction = direction
            
            # Настройка выделения
            self.highlight_rect = None
            
            # Обновление внешнего вида робота и настройка точки трансформации
            self.update_appearance()   
            
            # Настройка отображения
            self.setZValue(1000)  # Робот всегда отображается поверх других объектов
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
            self.direction = direction
            self.setRotation(direction)
        
    @property
    def id(self):
        """Возвращает ID робота в формате 'm<номер>'"""
        return self._id
        
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку робота.
        :param enabled: Если True, робот выделяется эллипсом.
        """
        if enabled:
            # Создаем прямоугольник для выделения
            if not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(0, 0, 50, 50, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
                
                # Устанавливаем точку трансформации для выделения, чтобы оно вращалось вокруг центра
                self.highlight_rect.setTransformOriginPoint(25, 25)
            
            # Показываем выделение (оно уже будет вращаться вместе с роботом, так как оно его дочерний элемент)
            self.highlight_rect.show()
            
        elif hasattr(self, 'highlight_rect') and self.highlight_rect:
            # Скрываем прямоугольник выделения
            self.highlight_rect.hide()
        
    def set_name(self, name):
        """
        Устанавливает имя робота.
        :param name: Новое имя робота.
        """
        self.name = name
        
    def set_direction(self, direction):
        """
        Устанавливает направление робота.
        :param direction: Направление в градусах.
        """
        self.direction = direction
        self.setRotation(direction)
        
    def remove_from_scene(self):
        """
        Удаляет робота из сцены.
        Обратите внимание, что это не освобождает Singleton, 
        так как может быть только один робот.
        """
        scene = self.scene()
        if scene:
            scene.removeItem(self)
            logger.debug("Робот удален из сцены")
            
    @classmethod
    def reset_instance(cls):
        """
        Сбрасывает экземпляр робота.
        Этот метод следует вызывать только при полной очистке сцены.
        """
        cls._instance = None
        logger.debug("Экземпляр робота сброшен")

    def shape(self):
        """
        Переопределяем shape(), чтобы робот реагировал на нажатие в любой точке изображения.
        """
        path = QPainterPath()
        path.addRect(self.boundingRect())  # Добавляем прямоугольник, охватывающий весь робот
        return path

    def update_appearance(self):
        """Обновляет внешний вид робота в зависимости от направления."""
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
        
        # Устанавливаем pixmap в любом случае
        self.setPixmap(pixmap)
        
        # Устанавливаем точку трансформации в центр изображения
        self.setTransformOriginPoint(25, 25)  # 50/2 = 25 (размер робота 50x50)

    def draw_default_robot(self):
        """Рисует синий квадрат с диагональными полосками."""
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        # Рисуем синий квадрат и диагонали
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(0, 0, 50, 50)
        painter.drawLine(0, 0, 50, 50)
        painter.drawLine(50, 0, 0, 50)
        painter.end()
        self.setPixmap(pixmap)            