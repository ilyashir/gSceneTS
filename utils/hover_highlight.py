from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF
import logging

logger = logging.getLogger(__name__)

class HoverHighlightMixin:
    """
    Миксин для добавления функциональности подсветки при наведении мыши.
    Должен использоваться с классами, наследующими от QGraphicsItem.
    """
    
    def init_hover_highlight(self):
        """
        Инициализирует поддержку подсветки при наведении.
        Должен вызываться в __init__ класса.
        """
        # Инициализация атрибутов
        self._is_hovered = False
        
        # Создаем элемент для подсветки при наведении
        # Если класс переопределяет create_hover_highlight, будет использован его метод
        self.hover_rect = self.create_hover_highlight()
        
        # Включение обработки событий наведения
        self.setAcceptHoverEvents(True)
        
        # Явное указание, что объект принимает события мыши
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        
        logger.debug(f"Инициализирована подсветка при наведении для {self}")
    
    def create_hover_highlight(self):
        """
        Создает и возвращает графический элемент для подсветки при наведении.
        По умолчанию создает прямоугольник, соответствующий boundingRect объекта.
        
        Этот метод может быть переопределен в наследниках для создания
        специфической формы подсветки.
        
        Returns:
            QGraphicsRectItem: Элемент для подсветки при наведении
        """
        rect = self.boundingRect()
        hover_rect = QGraphicsRectItem(rect, self)
        
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
        hover_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsPanel, False)
        
        # Скрываем прямоугольник по умолчанию
        hover_rect.hide()
        
        return hover_rect
    
    def set_hover_highlight(self, enabled):
        """
        Включает или выключает подсветку объекта при наведении мыши.
        
        Args:
            enabled (bool): Если True, объект подсвечивается пунктирным прямоугольником.
        """
        # Проверка, что объект не выделен (используем highlight_rect, если он есть)
        if hasattr(self, 'highlight_rect') and enabled and self.highlight_rect and getattr(self.highlight_rect, 'isVisible', lambda: False)():
            logger.debug(f"Объект {self}: Не включаем обводку при наведении, т.к. объект выделен")
            return
        
        if enabled and self.hover_rect:
            # Показываем подсветку
            self.hover_rect.show()
            logger.debug(f"Объект {self}: Включена обводка при наведении")
        elif not enabled and self.hover_rect:
            # Скрываем подсветку
            self.hover_rect.hide()
            logger.debug(f"Объект {self}: Отключена обводка при наведении")
    
    def hoverEnterEvent(self, event):
        """Обработчик события входа курсора мыши в область элемента."""
        logger.debug(f"hoverEnterEvent: Наведение на {self}")
        self._is_hovered = True
        
        # Показываем обводку при наведении, только если объект не выделен
        if not hasattr(self, 'highlight_rect') or not self.highlight_rect or not self.highlight_rect.isVisible():
            self.set_hover_highlight(True)
            
        # Вызываем базовый метод, если он есть
        original_method = getattr(super(), 'hoverEnterEvent', None)
        if original_method:
            original_method(event)

    def hoverLeaveEvent(self, event):
        """Обработчик события выхода курсора мыши из области элемента."""
        logger.debug(f"hoverLeaveEvent: Покидание {self}")
        self._is_hovered = False
        
        # Отключаем обводку при наведении
        self.set_hover_highlight(False)
            
        # Вызываем базовый метод, если он есть
        original_method = getattr(super(), 'hoverLeaveEvent', None)
        if original_method:
            original_method(event) 