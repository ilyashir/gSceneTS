import logging
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui import QPainterPath, QPen, QBrush, QColor, QPainter, QTransform
from PyQt6.QtCore import Qt, QRectF, QPointF
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Region(QGraphicsPathItem):
    _next_id = 1  # Статический счетчик для генерации ID
    _existing_ids = set()  # Множество для отслеживания существующих ID
    
    def __init__(self, points, region_id=None, color="#800000ff"):
        """
        Инициализация региона с заданными точками и ID.
        
        Args:
            points: Список точек региона (QPointF)
            region_id: ID региона (если None, будет сгенерирован автоматически)
            color: Цвет заливки региона в HEX-формате с альфа-каналом
        """
        super().__init__()
        
        # Создаем путь из точек
        path = QPainterPath()
        if points and len(points) >= 3:
            path.moveTo(points[0])
            for i in range(1, len(points)):
                path.lineTo(points[i])
            path.closeSubpath()
        self.setPath(path)
        
        # Генерация или проверка ID
        if region_id is None:
            # Автоматически генерируем ID
            self._id = f"r{Region._next_id}"
            Region._next_id += 1
        else:
            # Используем предоставленный ID
            try:
                if isinstance(region_id, str):
                    if region_id.startswith('r'):
                        num_id = int(region_id[1:])
                        self._id = region_id  # Используем оригинальный ID с префиксом
                    else:
                        num_id = int(region_id)
                        self._id = f"r{num_id}"  # Добавляем префикс
                elif isinstance(region_id, int):
                    num_id = region_id
                    self._id = f"r{num_id}"  # Добавляем префикс
                else:
                    raise ValueError(f"Неподдерживаемый тип ID: {type(region_id)}")
                
                # Проверяем, что ID положительный
                if num_id <= 0:
                    logger.warning(f"Отрицательный или нулевой ID '{region_id}', будет сгенерирован новый")
                    self._id = f"r{Region._next_id}"
                    Region._next_id += 1
                else:
                    # Проверяем уникальность ID
                    if self._id in Region._existing_ids:
                        logger.warning(f"ID '{self._id}' уже используется, будет сгенерирован новый")
                        self._id = f"r{Region._next_id}"
                        Region._next_id += 1
                    else:
                        # Обновляем счетчик, если заданный ID больше текущего
                        if num_id >= Region._next_id:
                            Region._next_id = num_id + 1
            except (ValueError, TypeError) as e:
                logger.warning(f"Некорректный ID '{region_id}': {e}, будет сгенерирован новый")
                self._id = f"r{Region._next_id}"
                Region._next_id += 1
        
        # Добавляем ID в множество существующих
        Region._existing_ids.add(self._id)
        
        # Настройка внешнего вида региона
        self.color = color
        self.update_appearance()
        
        # Настройка взаимодействия с мышью
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        
        # Флаг для отслеживания изменений
        self._updating = False
        
        logger.debug(f"Регион создан с id={self.id}")
    
    @contextmanager
    def updating(self):
        """Контекстный менеджер для предотвращения бесконечной рекурсии при обновлении."""
        self._updating = True
        try:
            yield
        finally:
            self._updating = False
    
    @property
    def id(self):
        """Возвращает ID региона."""
        return self._id
    
    def update_appearance(self):
        """Обновляет внешний вид региона."""
        # Настраиваем кисть и перо
        brush = QBrush(QColor(self.color))
        pen = QPen(Qt.PenStyle.NoPen)  # Без контура
        
        self.setBrush(brush)
        self.setPen(pen)
    
    def set_color(self, color):
        """Устанавливает цвет заливки региона."""
        self.color = color
        self.update_appearance()
    
    def set_highlight(self, enabled):
        """Включает/выключает подсветку региона."""
        if enabled:
            # Создаем новое перо для подсветки с ярким зеленым цветом
            highlight_pen = QPen(QColor("#00FF00"), 2)
            self.setPen(highlight_pen)
            # Устанавливаем флаг перемещения
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        else:
            # Возвращаем оригинальное перо (без контура)
            self.setPen(QPen(Qt.PenStyle.NoPen))
            # Снимаем флаг перемещения
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
    
    def set_id(self, new_id):
        """Устанавливает новый ID региона, если он уникален."""
        logger.debug(f"Attempting to set region ID from '{self.id}' to '{new_id}'")
        
        # Преобразуем ID в строку с префиксом, если необходимо
        if isinstance(new_id, str):
            if new_id.startswith('r'):
                try:
                    num_id = int(new_id[1:])
                    new_id_str = new_id
                except ValueError:
                    logger.warning(f"Invalid region ID format: {new_id}")
                    return False
            else:
                try:
                    num_id = int(new_id)
                    new_id_str = f"r{num_id}"
                except ValueError:
                    logger.warning(f"Invalid region ID format: {new_id}")
                    return False
        elif isinstance(new_id, int):
            if new_id <= 0:
                logger.warning(f"Region ID must be positive: {new_id}")
                return False
            num_id = new_id
            new_id_str = f"r{new_id}"
        else:
            logger.warning(f"Unsupported ID type: {type(new_id)}")
            return False
        
        # Проверяем, что ID изменился
        if new_id_str == self._id:
            logger.debug(f"New ID is the same as current ID, no change needed")
            return True
        
        # Проверяем уникальность ID
        if new_id_str in Region._existing_ids:
            logger.warning(f"ID '{new_id_str}' already used by another region")
            return False
        
        # Обновляем ID
        Region._existing_ids.remove(self._id)
        old_id = self._id
        self._id = new_id_str
        Region._existing_ids.add(self._id)
        
        # Обновляем счетчик, если новый ID больше текущего
        if num_id >= Region._next_id:
            Region._next_id = num_id + 1
            
        logger.debug(f"Region ID changed from {old_id} to {self._id}")
        return True
    
    def remove_from_scene(self):
        """Удаляет регион из сцены и освобождает его ID."""
        # Удаляем ID из множества существующих
        if self._id in Region._existing_ids:
            Region._existing_ids.remove(self._id)
        
        # Удаляем регион из сцены
        scene = self.scene()
        if scene:
            scene.removeItem(self)