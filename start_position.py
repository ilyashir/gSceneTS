from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem
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
            
            # Настройка выделения
            self.highlight_rect = None
            
            # Помечаем, что экземпляр уже инициализирован
            self._is_initialized = True
            
            logger.debug(f"Стартовая позиция инициализирована с id={self.id}")
        
        # Обновляем позицию при каждом вызове
        self.setPos(pos)
        
        # Включаем обработку событий мыши
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        # Обновляем направление, если оно задано
        if direction != 0:
            self._direction = direction
    
    def boundingRect(self):
        """
        Возвращает прямоугольник, содержащий элемент.
        """
        # Половина размера клетки (зоны видимости), уменьшена в 2 раза
        half_size = 12
        return QRectF(-half_size, -half_size, 2 * half_size, 2 * half_size)
    
    def paint(self, painter, option, widget):
        """
        Отрисовка диагонального креста стартовой позиции.
        """
        # Настройка пера для рисования
        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(3)  # Уменьшаем толщину линии для соответствия уменьшенному размеру
        painter.setPen(pen)
        
        # Рисуем диагональный крест (в 2 раза меньше)
        half_size = 12
        painter.drawLine(-half_size, -half_size, half_size, half_size)  # Диагональная линия "\"
        painter.drawLine(-half_size, half_size, half_size, -half_size)  # Диагональная линия "/"
    
    def shape(self):
        """
        Переопределяем shape(), чтобы стартовая позиция реагировала на нажатие в области диагонального креста.
        """
        path = QPainterPath()
        half_size = 12
        
        # Просто используем квадрат вокруг креста для упрощения кликабельной области
        path.addRect(-half_size, -half_size, 2 * half_size, 2 * half_size)
        
        return path
    
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку стартовой позиции.
        :param enabled: Если True, стартовая позиция выделяется прямоугольником.
        """
        if enabled:
            # Создаем прямоугольник для выделения
            if not self.highlight_rect:
                size = 24  # Удвоенный half_size
                self.highlight_rect = QGraphicsRectItem(-12, -12, size, size, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 2))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
                
            # Показываем выделение
            self.highlight_rect.show()
            
        elif hasattr(self, 'highlight_rect') and self.highlight_rect:
            # Скрываем прямоугольник выделения
            self.highlight_rect.hide()
    
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