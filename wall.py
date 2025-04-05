from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QTransform
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
from contextlib import contextmanager
import logging
# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Wall(QGraphicsLineItem):
    _next_id = 1  # Счетчик для генерации уникальных ID
    _existing_ids = set()  # Множество для хранения всех существующих ID

    def __init__(self, p1, p2, wall_id=None, width=10, color="#ff0000", is_temp=False):
        """
        Инициализация стены.
        
        Args:
            p1: Начальная точка стены (QPointF)
            p2: Конечная точка стены (QPointF)
            wall_id: Идентификатор стены (если None, будет сгенерирован)
            width: Толщина стены (по умолчанию 10)
            color: Цвет стены в HEX-формате
            is_temp: Флаг, указывающий, является ли стена временной (для проверок)
        """
        super().__init__(p1.x(), p1.y(), p2.x(), p2.y())
        
        # Для временных стен не обновляем _existing_ids и не увеличиваем _next_id
        self.is_temp = is_temp
        
        if wall_id:
            self.id = wall_id
            # Добавляем ID в множество только для не временных стен
            if not is_temp:
                Wall._existing_ids.add(self.id)
        else:
            if is_temp:
                # Для временных стен генерируем ID, но не добавляем его в _existing_ids
                self.id = f"temp_w{Wall._next_id}"
            else:
                # Для реальных стен генерируем ID и добавляем его в _existing_ids
                self.id = f"w{Wall._next_id}"
                Wall._next_id += 1
                Wall._existing_ids.add(self.id)

        self.highlight_rect = None  # Прямоугольник для выделения
        self._updating = False  # Флаг для отслеживания состояния обновления

        # Настройка внешнего вида стены
        self.brick_width = 10  # Ширина кирпича
        self.brick_height = 5  # Высота кирпича
        self.brick_color = QColor(color)  # Цвет кирпича (кирпично-красный)
        self.mortar_color = QColor("#8b4513")  # Цвет раствора между кирпичами

        # Создаем паттерн для кирпичной стены
        self.brick_pattern = self.create_brick_pattern()

        # Атрибуты стены
        self.stroke_color = "#ff000000"  # Цвет обводки (по умолчанию черный)
        self.stroke_width = width  # Ширина обводки (по умолчанию 10)

        # Настройка пера
        self.normal_pen = QPen(QColor(self.stroke_color), self.stroke_width)  # Паттерн для линии
        self.highlight_pen = QPen(QColor("#00ff22")  , self.stroke_width+5)  # Контур при выделении


        # Создаем прямоугольник с паттерном кирпичной стены
        self.brick_rect = QGraphicsRectItem(self)
        self.brick_rect.setBrush(QBrush(self.create_brick_pattern()))
        self.brick_rect.setPen(QPen(Qt.GlobalColor.transparent))  # Прозрачная обводка
        self.brick_rect.setData(0, "its_wall")
        # Отключаем обработку событий мыши для прямоугольника
        
        self.brick_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.brick_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

        # Обновляем прямоугольник в соответствии с линией
        self.update_brick_rect()

        self.setPen(self.normal_pen)

        # Добавляем маркеры на концах стены
        self.start_marker = QGraphicsEllipseItem(p1.x() - self.stroke_width // 2 - 1, p1.y() - self.stroke_width // 2 - 1, self.stroke_width + 2, self.stroke_width + 2, self)
        self.start_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.start_marker.setData(0, "wall_marker")
        self.end_marker = QGraphicsEllipseItem(p2.x() - self.stroke_width // 2 - 1, p2.y() - self.stroke_width // 2 - 1, self.stroke_width + 2, self.stroke_width  + 2, self)
        self.end_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.end_marker.setData(0, "wall_marker") 

        self.setZValue(10)
        self.brick_rect.setZValue(12)

        # # Включаем обработку событий мыши
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def create_brick_pattern(self):
        """
        Создает паттерн для кирпичной стены.
        """
        # Создаем изображение для паттерна
        pattern = QPixmap(self.brick_width * 2, self.brick_height * 2)
        pattern.fill(Qt.GlobalColor.transparent)

        # Рисуем кирпичи
        painter = QPainter(pattern)
        painter.setBrush(QBrush(self.brick_color))
        painter.setPen(QPen(self.mortar_color, 2))

        # Первый ряд кирпичей
        painter.drawRect(0, 0, self.brick_width, self.brick_height)
        painter.drawRect(self.brick_width, 0, self.brick_width, self.brick_height)

        # Второй ряд кирпичей (со смещением)
        painter.drawRect(self.brick_width // 2, self.brick_height, self.brick_width, self.brick_height)
        painter.drawRect(self.brick_width // 2 + self.brick_width, self.brick_height, self.brick_width, self.brick_height)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawRect(0, self.brick_height, self.brick_width // 2, self.brick_height)   

        painter.end()
        return pattern
    
    def update_brick_rect(self):
        """
        Обновляет прямоугольник с паттерном в соответствии с линией.
        """
        line = self.line()
        length = line.length()
        angle = line.angle()

        # Создаем прямоугольник, покрывающий линию
        rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
        self.brick_rect.setRect(rect)

        # Поворачиваем прямоугольник в соответствии с углом линии
        transform = QTransform()
        transform.translate(line.p1().x(), line.p1().y())
        transform.rotate(-angle)
        self.brick_rect.setTransform(transform)

    def set_highlight(self, enabled):
        """
        Включает или выключает подсветку региона.
        :param enabled: Если True, регион выделяется жёлтым контуром.
        """
        # self.setPen(self.highlight_pen if enabled else self.normal_pen)

        """Включает или выключает подсветку робота."""
        if enabled:
            line = self.line()
            length = line.length()
            angle = line.angle()
            # Создаем прямоугольник для выделения
            if not self.highlight_rect:           
                self.highlight_rect = QGraphicsRectItem(self)
                self.highlight_rect.setData(0, "its_wall")
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.green, 2))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            
            # Создаем прямоугольник, покрывающий линию
            rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
            self.highlight_rect.setRect(rect)

            # Применяем поворот к прямоугольнику выделения
            transform = QTransform()
            transform.translate(line.p1().x(), line.p1().y())
            transform.rotate(-angle)
            self.highlight_rect.setTransform(transform)
            self.highlight_rect.setZValue(20)
            self.highlight_rect.show()

            self.start_marker.setBrush(QBrush(Qt.GlobalColor.red))
            self.start_marker.setPen(QPen(Qt.GlobalColor.green,2))
            self.start_marker.setZValue(40) 
            self.end_marker.setBrush(QBrush(Qt.GlobalColor.red))
            self.end_marker.setPen(QPen(Qt.GlobalColor.green,2))
            self.end_marker.setZValue(40)  
        else:
            # Скрываем прямоугольник выделения
            if self.highlight_rect:
                self.highlight_rect.hide()
                self.start_marker.setPen(QPen(Qt.GlobalColor.transparent))
                self.end_marker.setPen(QPen(Qt.GlobalColor.transparent))

    def update_appearance(self):
        """Обновляет внешний вид стены в зависимости от атрибутов."""
        logger.debug(f"Updating appearance of wall with stroke width {self.stroke_width}")
        pen = QPen(Qt.GlobalColor.black, self.stroke_width)
        pen.setColor(Qt.GlobalColor.transparent)  # Прозрачный цвет (для пользовательского цвета)
        self.setPen(pen)
        # Обновляем прямоугольник с паттерном "кирпичная стена" в соответствии с линией
        self.update_brick_rect()
        
        # Всегда обновляем размеры маркеров при обновлении внешнего вида
        self.update_markers()
        
        if self.highlight_rect:
            line = self.line()
            length = line.length()
            angle = line.angle()
            
            # Создаем прямоугольник, покрывающий линию
            rect = QRectF(0, -self.stroke_width / 2, length, self.stroke_width)
            self.highlight_rect.setRect(rect)

            # Применяем поворот к прямоугольнику выделения
            transform = QTransform()
            transform.translate(line.p1().x(), line.p1().y())
            transform.rotate(-angle)
            self.highlight_rect.setTransform(transform)
            self.highlight_rect.setZValue(20)

    def update_markers(self):
        """Обновляет размеры и позиции маркеров."""
        line = self.line()
        marker_size = self.stroke_width + 2
        self.start_marker.setRect(
            line.x1() - marker_size/2,
            line.y1() - marker_size/2,
            marker_size,
            marker_size
        )
        self.end_marker.setRect(
            line.x2() - marker_size/2,
            line.y2() - marker_size/2,
            marker_size,
            marker_size
        )

    def set_stroke_width(self, width):
        """Устанавливает ширину обводки стены."""
        self.stroke_width = width
        self.update_appearance()

    @contextmanager
    def updating(self):
        """Контекстный менеджер для временного изменения состояния обновления."""
        self._updating = True
        try:
            yield
        finally:
            self._updating = False

    def setLine(self, x1, y1, x2, y2):
        """Переопределенный метод установки линии с обновлением маркеров."""
        # Вызываем родительский метод для установки линии
        super().setLine(x1, y1, x2, y2)
        logger.debug(f"Wall line set to: {x1, y1, x2, y2}")
        # Обновляем внешний вид стены вместе с маркерами
        self.update_appearance()

    def set_id(self, new_id):
        """
        Устанавливает новый ID для стены, если он уникален.
        :param new_id: Новый ID.
        """
        logger.debug(f"Attempting to set wall ID from '{self.id}' to '{new_id}'")
        
        # Для временных стен всегда разрешаем изменение ID
        if self.is_temp:
            self.id = new_id
            return True
        
        # Сначала проверяем, изменился ли ID
        if new_id == self.id:
            logger.debug(f"New ID is the same as current ID, no change needed")
            return True
            
        # Затем проверяем уникальность среди существующих ID
        if new_id in self._existing_ids:
            # Если ID уже занят, выводим сообщение в лог
            logger.warning(f"ID '{new_id}' already used by another wall")
            return False
        else:
            # Удаляем старый ID из множества и добавляем новый
            logger.debug(f"Removing old ID '{self.id}' from existing_ids")
            self._existing_ids.remove(self.id)
            self.id = new_id
            logger.debug(f"Adding new ID '{new_id}' to existing_ids")
            self._existing_ids.add(self.id)
            logger.debug(f"Wall ID successfully set to '{new_id}'")
            return True

    @classmethod
    def cleanup_temp_id(cls, temp_id):
        """Удаляет временный ID из множества существующих ID.
        Этот метод должен вызываться явно после использования временной стены.
        
        Args:
            temp_id: Временный ID стены для удаления
        """
        if temp_id in cls._existing_ids:
            logger.debug(f"Удаляем временный ID {temp_id} из Wall._existing_ids")
            cls._existing_ids.remove(temp_id)
            return True
        return False

    @property
    def wall_id(self):
        """Возвращает идентификатор стены (для совместимости с PropertiesWindow)"""
        return self.id