import unittest
import sys
import os
import logging

# Добавляем корневую директорию в sys.path для импорта модулей проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.type_utils import (
    safe_cast, 
    is_numeric, 
    is_string, 
    is_dict, 
    is_list, 
    get_nested_value, 
    set_nested_value
)

class TestTypeUtils(unittest.TestCase):
    """Тесты утилит для работы с типами данных"""
    
    def test_safe_cast_int(self):
        """Тестирование безопасного приведения к int."""
        # Стандартное приведение строки к int
        self.assertEqual(safe_cast("123", int), 123)
        
        # Приведение float к int
        self.assertEqual(safe_cast(123.5, int), 123)
        
        # Неверное значение с default=None
        self.assertIsNone(safe_cast("abc", int))
        
        # Неверное значение с указанным default
        self.assertEqual(safe_cast("abc", int, 0), 0)
        
        # None значение
        self.assertIsNone(safe_cast(None, int))
        self.assertEqual(safe_cast(None, int, 0), 0)
    
    def test_safe_cast_float(self):
        """Тестирование безопасного приведения к float."""
        # Стандартное приведение строки к float
        self.assertEqual(safe_cast("123.5", float), 123.5)
        
        # Приведение int к float
        self.assertEqual(safe_cast(123, float), 123.0)
        
        # Неверное значение с default=None
        self.assertIsNone(safe_cast("abc", float))
        
        # Неверное значение с указанным default
        self.assertEqual(safe_cast("abc", float, 0.0), 0.0)
    
    def test_safe_cast_str(self):
        """Тестирование безопасного приведения к str."""
        # Приведение числа к строке
        self.assertEqual(safe_cast(123, str), "123")
        
        # Приведение float к строке
        self.assertEqual(safe_cast(123.5, str), "123.5")
        
        # Приведение None к строке
        self.assertIsNone(safe_cast(None, str))
        self.assertEqual(safe_cast(None, str, ""), "")
    
    def test_safe_cast_custom_type(self):
        """Тестирование безопасного приведения к пользовательскому типу."""
        class CustomType:
            def __init__(self, value):
                if not isinstance(value, int):
                    raise ValueError("Value must be an integer")
                self.value = value
            
            def __eq__(self, other):
                return isinstance(other, CustomType) and self.value == other.value
        
        # Успешное приведение
        self.assertEqual(safe_cast(123, CustomType), CustomType(123))
        
        # Неудачное приведение
        self.assertIsNone(safe_cast("abc", CustomType))
        self.assertEqual(safe_cast("abc", CustomType, CustomType(0)), CustomType(0))
    
    def test_is_numeric(self):
        """Тестирование функции проверки числовых значений."""
        # Положительные тесты
        self.assertTrue(is_numeric(0))
        self.assertTrue(is_numeric(123))
        self.assertTrue(is_numeric(-456))
        self.assertTrue(is_numeric(123.456))
        self.assertTrue(is_numeric(-789.012))
        
        # Отрицательные тесты
        self.assertFalse(is_numeric("123"))
        self.assertFalse(is_numeric([1, 2, 3]))
        self.assertFalse(is_numeric({"value": 123}))
        self.assertFalse(is_numeric(None))
    
    def test_is_string(self):
        """Тестирование функции проверки строковых значений."""
        # Положительные тесты
        self.assertTrue(is_string(""))
        self.assertTrue(is_string("abc"))
        self.assertTrue(is_string("123"))
        
        # Отрицательные тесты
        self.assertFalse(is_string(123))
        self.assertFalse(is_string(123.456))
        self.assertFalse(is_string([1, 2, 3]))
        self.assertFalse(is_string({"value": "abc"}))
        self.assertFalse(is_string(None))
    
    def test_is_dict(self):
        """Тестирование функции проверки словарей."""
        # Положительные тесты
        self.assertTrue(is_dict({}))
        self.assertTrue(is_dict({"key": "value"}))
        self.assertTrue(is_dict({"numbers": [1, 2, 3]}))
        
        # Отрицательные тесты
        self.assertFalse(is_dict("string"))
        self.assertFalse(is_dict(123))
        self.assertFalse(is_dict([1, 2, 3]))
        self.assertFalse(is_dict(None))
    
    def test_is_list(self):
        """Тестирование функции проверки списков."""
        # Положительные тесты
        self.assertTrue(is_list([]))
        self.assertTrue(is_list([1, 2, 3]))
        self.assertTrue(is_list(["a", "b", "c"]))
        self.assertTrue(is_list([{"key": "value"}, [1, 2, 3]]))
        
        # Отрицательные тесты
        self.assertFalse(is_list("string"))
        self.assertFalse(is_list(123))
        self.assertFalse(is_list({"key": "value"}))
        self.assertFalse(is_list(None))
    
    def test_get_nested_value(self):
        """Тестирование получения значения из вложенного словаря."""
        # Тестовые данные
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                },
                "numbers": [1, 2, 3]
            },
            "empty": {}
        }
        
        # Получение значения по строковому пути
        self.assertEqual(get_nested_value(data, "level1.level2.level3"), "value")
        
        # Получение значения по списку ключей
        self.assertEqual(get_nested_value(data, ["level1", "level2", "level3"]), "value")
        
        # Получение значения, отсутствующего в словаре
        self.assertIsNone(get_nested_value(data, "level1.missing"))
        self.assertEqual(get_nested_value(data, "level1.missing", "default"), "default")
        
        # Получение значения из пустого словаря
        self.assertIsNone(get_nested_value(data, "empty.missing"))
        
        # Получение значения из списка
        self.assertEqual(get_nested_value(data, "level1.numbers"), [1, 2, 3])
        
        # Попытка доступа через несловарный тип
        self.assertIsNone(get_nested_value(data, "level1.numbers.0"))
    
    def test_set_nested_value(self):
        """Тестирование установки значения во вложенный словарь."""
        # Тестовые данные
        data = {
            "level1": {
                "level2": {}
            }
        }
        
        # Установка значения по строковому пути
        self.assertTrue(set_nested_value(data, "level1.level2.level3", "value"))
        self.assertEqual(data["level1"]["level2"]["level3"], "value")
        
        # Установка значения по списку ключей
        self.assertTrue(set_nested_value(data, ["level1", "new_key", "sub_key"], 123))
        self.assertEqual(data["level1"]["new_key"]["sub_key"], 123)
        
        # Переопределение значения
        self.assertTrue(set_nested_value(data, "level1.level2.level3", "new_value"))
        self.assertEqual(data["level1"]["level2"]["level3"], "new_value")
        
        # Создание нового пути
        self.assertTrue(set_nested_value(data, "new_path.sub_path", [1, 2, 3]))
        self.assertEqual(data["new_path"]["sub_path"], [1, 2, 3])
        
        # Попытка установки значения через несловарный тип
        data["conflict"] = "string"
        self.assertFalse(set_nested_value(data, "conflict.key", "value"))

if __name__ == "__main__":
    unittest.main() 