"""
Утилиты для работы с логированием.
"""

import logging
import os
from datetime import datetime

def setup_logger(name, log_dir='logs'):
    """
    Настройка логгера с записью в файл и консоль.
    
    Args:
        name: Имя логгера
        log_dir: Директория для лог-файлов
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Создаем директорию для логов если её нет
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Хендлер для файла
    log_file = os.path.join(
        log_dir, 
        f'{name}_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем хендлеры к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_exception(logger, e, context=""):
    """
    Логирование исключения с контекстом.
    
    Args:
        logger: Логгер для записи
        e: Исключение
        context: Контекст ошибки
    """
    logger.error(f"{context}: {str(e)}", exc_info=True)

def log_value_change(logger, element_type, element_id, property_name, old_value, new_value):
    """
    Логирование изменения значения свойства.
    
    Args:
        logger: Логгер для записи
        element_type: Тип элемента
        element_id: ID элемента
        property_name: Имя свойства
        old_value: Старое значение
        new_value: Новое значение
    """
    logger.debug(
        f"Изменение свойства {property_name} для {element_type} {element_id}: "
        f"{old_value} -> {new_value}"
    ) 