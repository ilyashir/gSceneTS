from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QPainterPath, QColor
from PyQt6.QtCore import QRectF, Qt, QPointF
from .base_item import BaseSceneItem
import logging

logger = logging.getLogger(__name__)

class Region(BaseSceneItem):
    """
    Класс региона (цветной области) на сцене.
    """
    
    _next_id = 1  # Счетчик для генерации уникальных ID
    _existing_ids = set()  # Множество для хранения всех существующих ID
    
    def __init__(self, rect, region_id=None, color="#ffff00", is_temp=False):
        """
        Инициализация региона.
        
        Args:
            rect: Прямоугольник региона (QRectF)
            region_id: Уникальный идентификатор региона (если None, будет сгенерирован)
            color: Цвет региона в HEX-формате
            is_temp: Флаг, указывающий, является ли регион временным (для проверок)
        """
        # Генерация ID для региона
        if region_id:
            self.id = region_id
            if not is_temp:
                Region._existing_ids.add(self.id)
        else:
            if is_temp:
                self.id = f"temp_r{Region._next_id}"
            else:
                self.id = f"r{Region._next_id}"
                Region._next_id += 1
                Region._existing_ids.add(self.id)
        
        # --- Инициализируем геометрию ПЕРЕД super().__init__ --- 
        self._rect = rect # Используем приватный атрибут для хранения QRectF
        # ---------------------------------------------------------
        
        # Инициализация базового класса
        super().__init__(item_type="region", item_id=self.id, is_temp=is_temp, z_value=5)
        
        # Настройка внешнего вида региона
        self.color = QColor(color)
        
        # Создаем QGraphicsRectItem для отображения
        # Используем self._rect для инициализации
        logger.debug(f"Инициализация региона: {self._rect}, c координатами: {self._rect.topLeft()}")
        self.region_rect = QGraphicsRectItem(self._rect, self)
        self.region_rect.setBrush(QBrush(self.color.lighter(150)))
        self.region_rect.setPen(QPen(self.color.darker(150), 2))
        self.region_rect.setData(0, "its_region")
        self.region_rect.setZValue(7)
        
        # Включаем обработку событий мыши
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        # Обновляем подсветку при наведении, если она была создана в super().__init__
        if hasattr(self, 'hover_rect') and self.hover_rect:
            self.hover_rect.setRect(self._rect)
    
    def create_hover_highlight(self):
        """Создает подсветку при наведении для региона."""
        hover_rect = QGraphicsRectItem(self._rect, self)
        
        # Настраиваем перо с пунктирной линией синего цвета
        pen = QPen(QColor("#3399FF"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        hover_rect.setPen(pen)
        hover_rect.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        # Устанавливаем данные для идентификации объекта при кликах
        hover_rect.setData(0, "hover_highlight")
        
        # Отключаем обработку событий мыши для прямоугольника подсветки
        hover_rect.setAcceptHoverEvents(False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        # Скрываем прямоугольник по умолчанию
        hover_rect.hide()
        
        return hover_rect
        
    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку региона при выделении.
        :param enabled: Если True, регион выделяется прямоугольником.
        """
        if enabled:
            if not hasattr(self, 'highlight_rect') or not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(self._rect, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            
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
        """Возвращает прямоугольник, охватывающий регион"""
        return self._rect
    
    def paint(self, painter, option, widget):
        """Отрисовка региона не требуется, так как используется QGraphicsRectItem"""
        pass
    
    def shape(self):
        """
        Переопределяем shape(), чтобы регион реагировал на нажатие в любой точке прямоугольника.
        """
        path = QPainterPath()
        path.addRect(self._rect)
        return path
    
    def set_color(self, color):
        """
        Устанавливает новый цвет для региона.
        :param color: Новый цвет в HEX-формате.
        """
        self.color = QColor(color)
        self.region_rect.setBrush(QBrush(self.color.lighter(150)))
        self.region_rect.setPen(QPen(self.color.darker(150), 2))
    
    def set_rect(self, rect):
        """
        Устанавливает новый прямоугольник для региона.
        :param rect: Новый прямоугольник (QRectF).
        """
        self.prepareGeometryChange()
        self._rect = rect
        self.region_rect.setRect(rect)
        
        if hasattr(self, 'highlight_rect') and self.highlight_rect:
            self.highlight_rect.setRect(rect)
        if hasattr(self, 'hover_rect') and self.hover_rect:
            self.hover_rect.setRect(rect)
        self.update()
    
    @classmethod
    def reset_ids(cls):
        """
        Сбрасывает счетчик ID и очищает множество существующих ID.
        Этот метод следует вызывать только при полной очистке сцены.
        """
        cls._next_id = 1
        cls._existing_ids.clear()
        logger.debug("Счетчик ID регионов сброшен") 

    def pos(self):
        """
        Возвращает позицию региона.
        """
        return self._rect.topLeft()
    
    def width(self):
        """
        Возвращает ширину региона.
        """
        return self._rect.width()
    
    def height(self):
        """
        Возвращает высоту региона.
        """
        return self._rect.height()
    
    

    
    
