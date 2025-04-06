from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPainter, QPen, QBrush, QPainterPath
from PyQt6.QtCore import QRectF, Qt, QPointF
import logging

logger = logging.getLogger(__name__)

class StartPosition(QGraphicsItem):
    """
    Класс, представляющий стартовую позицию робота на сцене.
    Отображается в виде красного креста.
    """
    
    # Статический атрибут для хранения единственного экземпляра
    _instance = None
    # Фиксированный ID для стартовой позиции
    _id = "startPosition"
    
    def __new__(cls, pos, direction=0):
        """
        Реализует паттерн Singleton для класса StartPosition.
        Позволяет создать только один экземпляр стартовой позиции.
        """
        if cls._instance is None:
            cls._instance = super(StartPosition, cls).__new__(cls)
            logger.debug("Создан первый экземпляр стартовой позиции")
        return cls._instance
    
    def __init__(self, pos, direction=0):
        """
        Инициализация стартовой позиции.
        
        Args:
            pos: Позиция стартовой позиции (QPointF)
            direction: Направление в градусах
        """
        # Проверяем, был ли уже инициализирован экземпляр
        if not hasattr(self, '_is_initialized') or not self._is_initialized:
            super().__init__()
            
            # Настройка свойств
            self._x = pos.x()
            self._y = pos.y()
            self._direction = direction
            
            # Настройка отображения
            self.setZValue(500)  # Стартовая позиция отображается под роботом, но над другими объектами
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            
            # Помечаем, что экземпляр уже инициализирован
            self._is_initialized = True
            
            logger.debug(f"Стартовая позиция инициализирована с id={self.id}")
        
        # Обновляем позицию при каждом вызове
        self.setPos(pos)
    
    def boundingRect(self):
        """
        Возвращает прямоугольник, содержащий элемент.
        """
        # Половина размера клетки (зоны видимости)
        half_size = 25
        return QRectF(-half_size, -half_size, 2 * half_size, 2 * half_size)
    
    def paint(self, painter, option, widget):
        """
        Отрисовка креста стартовой позиции.
        """
        # Настройка пера для рисования
        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(5)
        painter.setPen(pen)
        
        # Рисуем крест
        half_size = 25  # Половина размера клетки
        painter.drawLine(-half_size, 0, half_size, 0)  # Горизонтальная линия
        painter.drawLine(0, -half_size, 0, half_size)  # Вертикальная линия
    
    def shape(self):
        """
        Переопределяем shape(), чтобы стартовая позиция реагировала на нажатие в области креста.
        """
        path = QPainterPath()
        half_size = 25
        # Создаем форму для вертикальной линии
        path.addRect(-2.5, -half_size, 5, 2 * half_size)
        # Создаем форму для горизонтальной линии
        path.addRect(-half_size, -2.5, 2 * half_size, 5)
        return path
    
    @property
    def id(self):
        """Возвращает идентификатор стартовой позиции."""
        return self._id
    
    def x(self):
        """Возвращает X-координату стартовой позиции."""
        return self.pos().x()
    
    def y(self):
        """Возвращает Y-координату стартовой позиции."""
        return self.pos().y()
    
    def direction(self):
        """Возвращает направление стартовой позиции."""
        return self._direction
    
    def set_direction(self, direction):
        """
        Устанавливает направление стартовой позиции.
        :param direction: Направление в градусах.
        """
        self._direction = direction
    
    @classmethod
    def reset_instance(cls):
        """
        Сбрасывает экземпляр стартовой позиции.
        Этот метод следует вызывать только при полной очистке сцены.
        """
        cls._instance = None
        logger.debug("Экземпляр стартовой позиции сброшен") 