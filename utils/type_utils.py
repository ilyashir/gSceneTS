"""
Утилиты для работы с типами данных.
"""

from typing import Any, Union, Dict, List, Optional, TypeVar, Type
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

def safe_cast(value: Any, target_type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """
    Безопасное приведение значения к указанному типу.
    
    Args:
        value: Значение для приведения
        target_type: Целевой тип
        default: Значение по умолчанию
        
    Returns:
        Optional[T]: Приведенное значение или значение по умолчанию
    """
    try:
        if value is None:
            return default
        return target_type(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Ошибка при приведении значения {value} к типу {target_type}: {e}")
        return default

def is_numeric(value: Any) -> bool:
    """
    Проверка значения на числовой тип.
    
    Args:
        value: Проверяемое значение
        
    Returns:
        bool: True если значение числовое
    """
    return isinstance(value, (int, float))

def is_string(value: Any) -> bool:
    """
    Проверка значения на строковый тип.
    
    Args:
        value: Проверяемое значение
        
    Returns:
        bool: True если значение строковое
    """
    return isinstance(value, str)

def is_dict(value: Any) -> bool:
    """
    Проверка значения на словарь.
    
    Args:
        value: Проверяемое значение
        
    Returns:
        bool: True если значение является словарем
    """
    return isinstance(value, dict)

def is_list(value: Any) -> bool:
    """
    Проверка значения на список.
    
    Args:
        value: Проверяемое значение
        
    Returns:
        bool: True если значение является списком
    """
    return isinstance(value, list)

def get_nested_value(
    data: Dict[str, Any],
    path: Union[str, List[str]],
    default: Any = None
) -> Any:
    """
    Получение значения из вложенного словаря по пути.
    
    Args:
        data: Исходный словарь
        path: Путь к значению (строка или список ключей)
        default: Значение по умолчанию
        
    Returns:
        Any: Найденное значение или значение по умолчанию
    """
    if isinstance(path, str):
        path = path.split('.')
        
    current = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
            
    return current

def set_nested_value(
    data: Dict[str, Any],
    path: Union[str, List[str]],
    value: Any
) -> bool:
    """
    Установка значения во вложенный словарь по пути.
    
    Args:
        data: Исходный словарь
        path: Путь к значению (строка или список ключей)
        value: Значение для установки
        
    Returns:
        bool: True если значение установлено
    """
    if isinstance(path, str):
        path = path.split('.')
        
    current = data
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
        if not isinstance(current, dict):
            return False
            
    current[path[-1]] = value
    return True 