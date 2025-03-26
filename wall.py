from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QTransform
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
import logging
# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Wall(QGraphicsLineItem):
    _next_id = 1  # Счетчик для генерации уникальных ID

    def __init__(self, start, end):
        super().__init__(start.x(), start.y(), end.x(), end.y())
        self.id = f"w{Wall._next_id}"  # Генерация уникального ID
        Wall._next_id += 1  # Увеличиваем счетчик

        self.highlight_rect = None  # Прямоугольник для выделения

        # Настройка внешнего вида стены
        self.brick_width = 10  # Ширина кирпича
        self.brick_height = 5  # Высота кирпича
        self.brick_color = QColor("#b22222")  # Цвет кирпича (кирпично-красный)
        self.mortar_color = QColor("#8b4513")  # Цвет раствора между кирпичами

        # Создаем паттерн для кирпичной стены
        self.brick_pattern = self.create_brick_pattern()

        # Атрибуты стены
        self.stroke_color = "#ff000000"  # Цвет обводки (по умолчанию черный)
        self.stroke_width = 10  # Ширина обводки (по умолчанию 10)

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
        self.start_marker = QGraphicsEllipseItem(start.x() - self.stroke_width // 2 - 1, start.y() - self.stroke_width // 2 - 1, self.stroke_width + 2, self.stroke_width + 2, self)
        self.start_marker.setBrush(QBrush(Qt.GlobalColor.red))
        self.start_marker.setData(0, "wall_marker")
        self.end_marker = QGraphicsEllipseItem(end.x() - self.stroke_width // 2 - 1, end.y() - self.stroke_width // 2 - 1, self.stroke_width + 2, self.stroke_width  + 2, self)
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
        pen = QPen(Qt.GlobalColor.black, self.stroke_width)
        pen.setColor(Qt.GlobalColor.transparent)  # Прозрачный цвет (для пользовательского цвета)
        self.setPen(pen)
        
        self.update_brick_rect()
        
        # Обновляем размеры маркеров
        logger.debug(f"Updating marker to size {self.stroke_width}")
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
        
        if self.highlight_rect:
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

    def set_stroke_width(self, width):
        """Устанавливает ширину обводки стены."""
        self.stroke_width = width
        self.update_appearance()

    def setLine(self, x1, y1, x2, y2):
        """Переопределенный метод установки линии с обновлением маркеров."""
        # Вызываем родительский метод для установки линии
        super().setLine(x1, y1, x2, y2)
        
        # Обновляем позиции маркеров
        if hasattr(self, 'start_marker'):
            # Устанавливаем позицию с учетом размера маркера
            self.start_marker.setRect(
                x1 - self.stroke_width // 2 - 1,
                y1 - self.stroke_width // 2 - 1,
                self.stroke_width + 2,
                self.stroke_width + 2
            )
        
        if hasattr(self, 'end_marker'):
            # Устанавливаем позицию с учетом размера маркера
            self.end_marker.setRect(
                x2 - self.stroke_width // 2 - 1,
                y2 - self.stroke_width // 2 - 1,
                self.stroke_width + 2,
                self.stroke_width + 2
            )
        
        # Обновляем внешний вид стены
        self.update_appearance()