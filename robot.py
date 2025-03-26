from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter, QTransform, QPen, QBrush, QPainterPath
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QRectF, Qt

class Robot(QGraphicsPixmapItem):
    def __init__(self, pos):
        super().__init__()
        self.setPos(pos)
        self.direction = 0.0  # Направление робота (по умолчанию 0 градусов)
        self.renderer = QSvgRenderer() # Инициализация рендера без файла
        self.highlight_rect = None  # Прямоугольник для выделения
        self.update_appearance()        

        # Устанавливаем высокое Z-value, чтобы робот был поверх других объектов
        self.setZValue(1000)  # Любое большое число

        # Включаем обработку событий мыши
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
    
    def shape(self):
        """
        Переопределяем shape(), чтобы робот реагировал на нажатие в любой точке изображения.
        """
        path = QPainterPath()
        path.addRect(self.boundingRect())  # Добавляем прямоугольник, охватывающий весь робот
        return path
    
    def update_appearance(self):
        """Обновляет внешний вид робота в зависимости от направления."""
        if not self.renderer.load("images/robot.svg"):  # Если SVG не загрузился
            print("SVG не загружен. Рисуем синий квадрат.")  # Отладочное сообщение
            self.draw_default_robot()  # Рисуем синий квадрат
        else:
            # Если SVG загрузился, рисуем его
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            
            # Применяем поворот на основе направления
            transform = QTransform()
            transform.rotate(self.direction)
            painter.setTransform(transform)
            
            # Рендерим SVG
            self.renderer.render(painter, QRectF(0, 0, 50, 50))
            painter.end()
            self.setPixmap(pixmap)

    def draw_default_robot(self):
        """Рисует синий квадрат с диагональными полосками."""
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        
        # Применяем поворот на основе направления
        transform = QTransform()
        transform.rotate(float(self.direction))
        painter.setTransform(transform)
        
        # Рисуем синий квадрат и диагонали
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(0, 0, 50, 50)
        painter.drawLine(0, 0, 50, 50)
        painter.drawLine(50, 0, 0, 50)
        painter.end()
        self.setPixmap(pixmap)

    def set_highlight(self, enabled):
        """Включает или выключает подсветку робота."""
        if enabled:
            # Создаем прямоугольник для выделения
            if not self.highlight_rect:
                self.highlight_rect = QGraphicsRectItem(0, 0, 50, 50, self)
                self.highlight_rect.setPen(QPen(Qt.GlobalColor.blue, 3))
                self.highlight_rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            
            # Применяем поворот к прямоугольнику выделения
            transform = QTransform()
            transform.rotate(float(self.direction))
            self.highlight_rect.setTransform(transform)
            self.highlight_rect.show()
        else:
            # Скрываем прямоугольник выделения
            if self.highlight_rect:
                self.highlight_rect.hide()

    def set_direction(self, direction):
        """Устанавливает направление робота и обновляет его внешний вид."""
        self.direction = float(direction)
        self.update_appearance()            