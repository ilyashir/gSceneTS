from PyQt6.QtCore import QPointF, QLineF, QRectF
from math import sqrt
import logging

logger = logging.getLogger(__name__)

def distance_to_line(point: QPointF, line: QLineF) -> float:
    """
    Вычисляет расстояние от точки до линии.
    
    Args:
        point: Точка (QPointF)
        line: Линия (QLineF)
        
    Returns:
        float: Расстояние от точки до линии
    """
    # Формула для расстояния от точки до линии
    x0, y0 = point.x(), point.y()
    x1, y1 = line.x1(), line.y1()
    x2, y2 = line.x2(), line.y2()
    
    # Если точки отрезка совпадают, возвращаем расстояние до одной из них
    if x1 == x2 and y1 == y2:
        return sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
        
    # Вычисляем расстояние
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    
    # Избегаем деления на ноль
    if denominator == 0:
        return sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
        
    return numerator / denominator

def line_intersects_rect(line: QLineF, rect: QRectF) -> bool:
    """
    Проверяет, пересекает ли линия прямоугольник.
    :param line: Линия (QLineF).
    :param rect: Прямоугольник (QRectF).
    :return: True, если линия пересекает прямоугольник, иначе False.
    """
    # Получаем стороны прямоугольника
    top = QLineF(rect.topLeft(), rect.topRight())
    right = QLineF(rect.topRight(), rect.bottomRight())
    bottom = QLineF(rect.bottomLeft(), rect.bottomRight())
    left = QLineF(rect.topLeft(), rect.bottomLeft())

    # Проверяем пересечение линии с каждой стороной прямоугольника
    for side in [top, right, bottom, left]:
        intersection_type, intersection_point = line.intersects(side)
        if intersection_type == QLineF.IntersectionType.BoundedIntersection:
            return True  # Линия пересекает прямоугольник

    # Проверяем, находится ли один из концов линии внутри прямоугольника
    if rect.contains(line.p1()) or rect.contains(line.p2()):
        return True

    return False  # Линия не пересекает прямоугольник
    
def line_with_thickness_intersects_rect(line: QLineF, rect: QRectF, thickness: float) -> bool:
    """
    Проверяет, пересекает ли линия с заданной толщиной прямоугольник.
    
    Args:
        line: Линия (QLineF)
        rect: Прямоугольник (QRectF)
        thickness: Толщина линии
        
    Returns:
        bool: True, если линия с учетом толщины пересекает прямоугольник, иначе False
    """
    # Проверяем сначала обычное пересечение
    if line_intersects_rect(line, rect):
        return True
        
    # Если обычное пересечение не обнаружено, проверяем с учетом толщины
    # Для этого создаем увеличенный прямоугольник с учетом половины толщины линии
    inflated_rect = QRectF(
        rect.x() - thickness / 2,
        rect.y() - thickness / 2,
        rect.width() + thickness,
        rect.height() + thickness
    )
    
    # Проверяем пересечение с увеличенным прямоугольником
    return line_intersects_rect(line, inflated_rect)
    
def cut_coords(x: float, y: float, scene_width: float, scene_height: float) -> tuple[float, float]:
    """
    Обрезает координаты, чтобы они не выходили за пределы сцены.
    
    Args:
        x: Координата X
        y: Координата Y
        scene_width: Ширина сцены
        scene_height: Высота сцены
        
    Returns:
        tuple[float, float]: Обрезанные координаты (x, y)
    """
    half_width = scene_width / 2
    half_height = scene_height / 2
    
    x = max(min(x, half_width), -half_width)
    y = max(min(y, half_height), -half_height)
    
    return x, y

def snap_to_grid(pos: QPointF, grid_size: int, snap_enabled: bool, scene_width: float, scene_height: float) -> QPointF:
    """
    Привязывает координаты точки к сетке, если привязка включена,
    и обрезает их по границам сцены.
    
    Args:
        pos: Исходная точка (QPointF)
        grid_size: Размер ячейки сетки
        snap_enabled: Флаг включения привязки к сетке
        scene_width: Ширина сцены
        scene_height: Высота сцены
        
    Returns:
        QPointF: Точка с координатами, привязанными к сетке (если включено) и обрезанными по границам сцены.
    """
    x_orig, y_orig = pos.x(), pos.y()
    
    if snap_enabled:
        x = round(x_orig / grid_size) * grid_size
        y = round(y_orig / grid_size) * grid_size
    else:
        x, y = x_orig, y_orig
        
    x_cut, y_cut = cut_coords(x, y, scene_width, scene_height)
    
    return QPointF(x_cut, y_cut) 