"""
Пакет свойств для элементов сцены.

Содержит виджеты и утилиты для управления свойствами различных элементов:
- Робот
- Стена
- Регион
"""

from properties.base_properties_widget import BasePropertiesWidget
from properties.robot_properties_widget import RobotPropertiesWidget
from properties.wall_properties_widget import WallPropertiesWidget
from properties.region_properties_widget import RegionPropertiesWidget
from properties.properties_manager import PropertiesManager

__all__ = [
    'BasePropertiesWidget',
    'RobotPropertiesWidget',
    'WallPropertiesWidget',
    'RegionPropertiesWidget',
    'PropertiesManager'
] 