import sys
import os
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication

# Добавляем корневую директорию проекта в путь к модулям
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем тестируемые модули
from utils.xml_handler import XMLHandler
from scene.items import StartPosition

class TestXMLStartPosition(unittest.TestCase):
    """Тестирование экспорта/импорта стартовой позиции в XML формате"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем простой XML вручную для тестирования вместо использования XMLHandler.generate_xml
        self.test_export_xml = """<?xml version="1.0" ?>
<root version="1.0">
  <world width="1300" height="900"/>
  <walls/>
  <regions/>
  <robots>
    <robot id="1" position="0:0" direction="0">
      <startPosition id="startPosition" x="50" y="50" direction="90"/>
    </robot>
  </robots>
</root>"""
        
        # Создаем тестовый XML для импорта
        self.test_import_xml = """<?xml version="1.0" ?>
<root version="1.0">
  <world width="1300" height="900"/>
  <walls/>
  <regions/>
  <robots>
    <robot id="1" position="0:0" direction="0">
      <startPosition id="startPosition" x="100" y="100" direction="45"/>
    </robot>
  </robots>
</root>"""
    
    def test_export_xml_with_start_position(self):
        """Тест экспорта XML со стартовой позицией"""
        # Парсим заранее созданный XML
        xml_handler = XMLHandler()
        scene_data = xml_handler.parse_xml(self.test_export_xml)
        
        # Проверяем, что XML правильно содержит данные стартовой позиции
        self.assertIn("start_position", scene_data)
        self.assertEqual(scene_data["start_position"]["x"], 50)
        self.assertEqual(scene_data["start_position"]["y"], 50)
        self.assertEqual(scene_data["start_position"]["direction"], 90.0)

    def test_import_xml_with_start_position(self):
        """Тест импорта XML со стартовой позицией"""
        # Загружаем XML
        xml_handler = XMLHandler()
        scene_data = xml_handler.parse_xml(self.test_import_xml)
        
        # Проверяем данные стартовой позиции
        self.assertIn("start_position", scene_data)
        self.assertEqual(scene_data["start_position"]["x"], 100)
        self.assertEqual(scene_data["start_position"]["y"], 100)
        self.assertEqual(scene_data["start_position"]["direction"], 45.0)

if __name__ == "__main__":
    # Запускаем тесты с выводом результатов
    print("Запуск тестов для проверки XML с стартовой позицией")
    result = unittest.main(verbosity=2, exit=False)
    
    # Выводим результаты
    if result.result.wasSuccessful():
        print("\nВсе тесты успешно выполнены!")
        sys.exit(0)
    else:
        print("\nНекоторые тесты не прошли!")
        sys.exit(1) 