"""
Утилиты для работы с привязкой к сетке.
"""

def snap_to_grid(value, grid_size):
    """
    Привязывает значение к сетке.
    
    Args:
        value (float): Исходное значение
        grid_size (float): Размер ячейки сетки
        
    Returns:
        float: Значение, привязанное к сетке
    """
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

def get_grid_size(scene):
    """
    Получает размер ячейки сетки.
    
    Args:
        scene: Сцена, содержащая настройки сетки
        
    Returns:
        float: Размер ячейки сетки или 1 по умолчанию
    """
    if not scene:
        return 1
        
    field_widget = scene.parent()
    return getattr(field_widget, 'grid_size', 1) 