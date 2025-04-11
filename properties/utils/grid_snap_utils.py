"""
Утилиты для работы с привязкой к сетке.
"""
import logging

logger = logging.getLogger(__name__)

def snap_to_grid(value, grid_size):
    """
    Привязывает значение к сетке.
    
    Args:
        value (float): Исходное значение
        grid_size (float): Размер ячейки сетки
        
    Returns:
        float: Значение, привязанное к сетке
    """
    # Используем round() для более точного округления
    return round(value / grid_size) * grid_size

def snap_rotation_to_grid(rotation, grid_size=45):
    """
    Привязывает угол поворота к сетке.
    
    Args:
        rotation (float): Исходный угол поворота
        grid_size (float): Размер ячейки сетки для поворота (по умолчанию 45 градусов)
        
    Returns:
        float: Угол поворота, привязанный к сетке
    """
    # Используем round() для согласованности с snap_to_grid
    return round(rotation / grid_size) * grid_size

def is_snap_enabled(obj):
    """
    Проверяет, включена ли привязка к сетке.
    
    Args:
        scene: Сцена, содержащая настройки привязки
        
    Returns:
        bool: True если привязка включена, False в противном случае
    """
    if not obj:
        return False
    
    # Если передан сам FieldWidget
    if hasattr(obj, 'snap_to_grid_enabled'):
        return obj.snap_to_grid_enabled
    
    # Если передана сцена, получаем родительский FieldWidget
    if hasattr(obj, 'parent'):
        field_widget = obj.parent()
        if hasattr(field_widget, 'snap_to_grid_enabled'):
            return field_widget.snap_to_grid_enabled

def get_grid_size(field_widget, default_size=50):
    """
    Возвращает размер сетки из field_widget или значение по умолчанию.

    Args:
        field_widget: Виджет поля.
        default_size: Размер сетки по умолчанию.

    Returns:
        int: Размер сетки.
    """
    if field_widget and hasattr(field_widget, 'grid_size'):
        grid_size = getattr(field_widget, 'grid_size', default_size)
        logger.debug(f"Получен grid_size={grid_size} из field_widget")
        return grid_size
    logger.warning(f"Не удалось получить grid_size из field_widget, используется значение по умолчанию {default_size}")
    return default_size 