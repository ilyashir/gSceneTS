from PyQt6.QtWidgets import QGraphicsRectItem, QMessageBox
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF
import logging

class Region(QGraphicsRectItem):
    _next_id = 1  # Счетчик для генерации уникальных ID
    _existing_ids = set()  # Множество для хранения всех существующих ID

    def __init__(self, pos, width, height, color="#0000ff"):
        """
        Инициализация региона.

        :param pos: Начальная позиция региона (QPointF).
        :param width: Ширина региона.
        :param height: Высота региона.
        """
        super().__init__(pos.x(), pos.y(), width, height)
        
        # Генерация уникального ID
        self.id = f"r{Region._next_id}"
        Region._next_id += 1
        Region._existing_ids.add(self.id)  # Добавляем ID в множество существующих

        # Настройка внешнего вида региона
        self.color = color
        self.normal_pen = QPen(QColor(self.color), 1)  # Обычный контур
        self.highlight_pen = QPen(Qt.GlobalColor.green, 3)  # Контур при выделении
        self.setPen(self.normal_pen)

        # Настройка диагональной штриховки
        self.brush = QBrush(QColor(self.color), Qt.BrushStyle.DiagCrossPattern)
        self.setBrush(self.brush)

        self.setZValue(1)  

    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку региона.
        :param enabled: Если True, регион выделяется жёлтым контуром.
        """
        self.setPen(self.highlight_pen if enabled else self.normal_pen)

    def set_color(self, color):
        """
        Устанавливает новый цвет региона и обновляет штриховку.
        :param color: Новый цвет в формате HEX.
        """
        self.color = color
        self.brush.setColor(QColor(self.color))
        self.setBrush(self.brush)  

    def set_id(self, new_id):
        """
        Устанавливает новый ID для региона, если он уникален.
        :param new_id: Новый ID.
        :return: True, если ID установлен успешно, False в противном случае.
        """
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Attempting to set region ID from '{self.id}' to '{new_id}'")
        
        # Проверяем, что ID изменился
        if new_id == self.id:
            logger.debug(f"New ID is the same as current ID, no change needed")
            return True
        
        # Проверяем уникальность ID
        if new_id in Region._existing_ids:
            # Если ID уже занят, выводим уведомление в лог
            logger.warning(f"ID '{new_id}' already used by another region")
            return False
        
        # Удаляем старый ID из множества и добавляем новый
        logger.debug(f"Removing old ID '{self.id}' from existing_ids")
        Region._existing_ids.remove(self.id)
        self.id = new_id
        logger.debug(f"Adding new ID '{new_id}' to existing_ids")
        Region._existing_ids.add(self.id)
        logger.debug(f"Region ID successfully set to '{new_id}'")
        return True