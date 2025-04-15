"""
Base class for all scene items.
"""

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsItemGroup
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainterPath, QPen, QColor, QBrush
from utils.hover_highlight import HoverHighlightMixin
from abc import ABC, abstractmethod, ABCMeta
import logging

logger = logging.getLogger(__name__)

# Создаем метакласс, который наследует от метаклассов QGraphicsItem и ABC
class SceneItemMeta(type(QGraphicsItem), ABCMeta):
    pass

class BaseSceneItem(QGraphicsItem, HoverHighlightMixin, ABC, metaclass=SceneItemMeta):
    """
    Базовый класс для всех элементов сцены.
    Обеспечивает общую функциональность: идентификацию и базовое взаимодействие.
    """
    
    # Для реализации Singleton (опционально)
    _instance = None
    
    @classmethod
    def __new__(cls, *args, **kwargs):
        """
        Реализация паттерна Singleton (если нужно).
        По умолчанию создает новый экземпляр.
        Переопределите в подклассе для реализации Singleton.
        """
        return super(BaseSceneItem, cls).__new__(cls)
    
    def __init__(self, item_type: str, item_id: str = None, is_temp: bool = False, z_value: int = 0):
        """
        Инициализация базового элемента сцены.
        
        Args:
            item_type: Тип элемента (wall, robot, region, start_position)
            item_id: Уникальный идентификатор (если None, генерируется автоматически)
            is_temp: Флаг временного элемента (для предпросмотра)
            z_value: Z-индекс элемента на сцене
        """
        super().__init__()
        if not is_temp:
            HoverHighlightMixin.__init__(self)
        
        self.item_type = item_type
        self.is_temp = is_temp
        self.id = item_id  # ID будет установлен SceneManager'ом
        
        # Общие атрибуты
        self._updating = False
        self._is_initialized = False
        
        # Настройка отображения
        self.setZValue(z_value)
        
        # Базовые флаги
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        
        if not is_temp:
            # Инициализация подсветки
            self.init_hover_highlight()
        
        self._is_initialized = True
    
    @abstractmethod
    def create_hover_highlight(self):
        """
        Создание подсветки при наведении.
        Должен быть реализован в каждом конкретном классе.
        """
        pass
    
    @abstractmethod
    def set_highlight(self, enabled: bool):
        """
        Включение/выключение подсветки элемента при выделении.
        Должен быть реализован в каждом конкретном классе.
        
        Args:
            enabled: True для включения подсветки, False для выключения
        """
        pass
    
    def boundingRect(self):
        """
        Определение границ элемента.
        Должен быть переопределен в каждом конкретном классе.
        """
        return self.childrenBoundingRect()
    
    def paint(self, painter, option, widget):
        """
        Отрисовка элемента.
        Должен быть переопределен в каждом конкретном классе.
        """
        pass
    
    def shape(self):
        """
        Определяет форму элемента для взаимодействия.
        По умолчанию использует boundingRect.
        Может быть переопределен в конкретном классе.
        """
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    def x(self) -> float:
        """Возвращает X-координату элемента"""
        return self.pos().x()
    
    def y(self) -> float:
        """Возвращает Y-координату элемента"""
        return self.pos().y()
    
    def remove_from_scene(self):
        """Удаляет элемент со сцены"""
        if self.scene():
            self.scene().removeItem(self)
            logger.debug(f"{self.item_type} удален со сцены")
    
    @classmethod
    def reset_instance(cls):
        """
        Сброс экземпляра (для Singleton).
        По умолчанию ничего не делает.
        Переопределите в подклассе для реализации Singleton.
        """
        pass
    
    def __str__(self):
        """Строковое представление элемента"""
        return f"{self.item_type}(id={self.id}, temp={self.is_temp}, pos=({self.x()}, {self.y()}))" 