"""
Базовые исключения для приложения.
"""

class ApplicationError(Exception):
    """
    Базовый класс для исключений приложения.
    """
    pass

class ValidationError(ApplicationError):
    """
    Исключение для ошибок валидации.
    """
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class ResourceError(ApplicationError):
    """
    Исключение для ошибок работы с ресурсами.
    """
    def __init__(self, message: str, resource: str = None):
        self.message = message
        self.resource = resource
        super().__init__(message)

class ConfigError(ApplicationError):
    """
    Исключение для ошибок конфигурации.
    """
    def __init__(self, message: str, key: str = None):
        self.message = message
        self.key = key
        super().__init__(message)

class EventError(ApplicationError):
    """
    Исключение для ошибок событий.
    """
    def __init__(self, message: str, event_type: str = None):
        self.message = message
        self.event_type = event_type
        super().__init__(message)

def handle_application_error(error: ApplicationError) -> str:
    """
    Обработка исключений приложения.
    
    Args:
        error: Исключение для обработки
        
    Returns:
        str: Сообщение об ошибке
    """
    if isinstance(error, ValidationError):
        return f"Ошибка валидации: {error.message}"
    elif isinstance(error, ResourceError):
        return f"Ошибка ресурса: {error.message}"
    elif isinstance(error, ConfigError):
        return f"Ошибка конфигурации: {error.message}"
    elif isinstance(error, EventError):
        return f"Ошибка события: {error.message}"
    else:
        return f"Неизвестная ошибка: {str(error)}" 