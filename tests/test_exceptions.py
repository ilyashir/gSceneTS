import unittest
import sys
import os

# Добавляем корневую директорию в sys.path для импорта модулей проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.exceptions import (
    ApplicationError,
    ValidationError,
    ResourceError,
    ConfigError,
    EventError,
    handle_application_error
)

class TestExceptions(unittest.TestCase):
    """Тесты исключений приложения"""
    
    def test_application_error(self):
        """Тестирование базового исключения ApplicationError."""
        # Создание исключения
        error = ApplicationError("Тестовая ошибка")
        
        # Проверка наследования
        self.assertIsInstance(error, Exception)
        
        # Проверка сообщения
        self.assertEqual(str(error), "Тестовая ошибка")
    
    def test_validation_error(self):
        """Тестирование исключения ValidationError."""
        # Создание исключения с полем
        error = ValidationError("Неверный формат", "email")
        
        # Проверка наследования
        self.assertIsInstance(error, ApplicationError)
        
        # Проверка атрибутов
        self.assertEqual(error.message, "Неверный формат")
        self.assertEqual(error.field, "email")
        
        # Проверка сообщения
        self.assertEqual(str(error), "Неверный формат")
        
        # Создание исключения без поля
        error = ValidationError("Неверный формат")
        self.assertEqual(error.message, "Неверный формат")
        self.assertIsNone(error.field)
    
    def test_resource_error(self):
        """Тестирование исключения ResourceError."""
        # Создание исключения с ресурсом
        error = ResourceError("Ресурс не найден", "image.png")
        
        # Проверка наследования
        self.assertIsInstance(error, ApplicationError)
        
        # Проверка атрибутов
        self.assertEqual(error.message, "Ресурс не найден")
        self.assertEqual(error.resource, "image.png")
        
        # Проверка сообщения
        self.assertEqual(str(error), "Ресурс не найден")
        
        # Создание исключения без ресурса
        error = ResourceError("Ресурс не найден")
        self.assertEqual(error.message, "Ресурс не найден")
        self.assertIsNone(error.resource)
    
    def test_config_error(self):
        """Тестирование исключения ConfigError."""
        # Создание исключения с ключом
        error = ConfigError("Неверный ключ конфигурации", "api_key")
        
        # Проверка наследования
        self.assertIsInstance(error, ApplicationError)
        
        # Проверка атрибутов
        self.assertEqual(error.message, "Неверный ключ конфигурации")
        self.assertEqual(error.key, "api_key")
        
        # Проверка сообщения
        self.assertEqual(str(error), "Неверный ключ конфигурации")
        
        # Создание исключения без ключа
        error = ConfigError("Неверный ключ конфигурации")
        self.assertEqual(error.message, "Неверный ключ конфигурации")
        self.assertIsNone(error.key)
    
    def test_event_error(self):
        """Тестирование исключения EventError."""
        # Создание исключения с типом события
        error = EventError("Ошибка обработки события", "click")
        
        # Проверка наследования
        self.assertIsInstance(error, ApplicationError)
        
        # Проверка атрибутов
        self.assertEqual(error.message, "Ошибка обработки события")
        self.assertEqual(error.event_type, "click")
        
        # Проверка сообщения
        self.assertEqual(str(error), "Ошибка обработки события")
        
        # Создание исключения без типа события
        error = EventError("Ошибка обработки события")
        self.assertEqual(error.message, "Ошибка обработки события")
        self.assertIsNone(error.event_type)
    
    def test_handle_application_error(self):
        """Тестирование функции обработки исключений."""
        # Обработка ValidationError
        error = ValidationError("Неверный формат", "email")
        self.assertEqual(handle_application_error(error), "Ошибка валидации: Неверный формат")
        
        # Обработка ResourceError
        error = ResourceError("Ресурс не найден", "image.png")
        self.assertEqual(handle_application_error(error), "Ошибка ресурса: Ресурс не найден")
        
        # Обработка ConfigError
        error = ConfigError("Неверный ключ конфигурации", "api_key")
        self.assertEqual(handle_application_error(error), "Ошибка конфигурации: Неверный ключ конфигурации")
        
        # Обработка EventError
        error = EventError("Ошибка обработки события", "click")
        self.assertEqual(handle_application_error(error), "Ошибка события: Ошибка обработки события")
        
        # Обработка базового ApplicationError
        error = ApplicationError("Неизвестная ошибка")
        expected = f"Неизвестная ошибка: {str(error)}"
        self.assertEqual(handle_application_error(error), expected)

if __name__ == "__main__":
    unittest.main() 