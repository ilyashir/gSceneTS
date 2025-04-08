"""
Properties package.
Contains classes for managing object properties.
"""

from .properties_manager import PropertiesManager
from .properties_window_adapter import PropertiesWindow
from .robot_properties_widget import RobotPropertiesWidget
from .wall_properties_widget import WallPropertiesWidget
from .region_properties_widget import RegionPropertiesWidget
from .start_position_properties_widget import StartPositionPropertiesWidget

__all__ = [
    'PropertiesManager', 
    'PropertiesWindow', 
    'RobotPropertiesWidget', 
    'WallPropertiesWidget', 
    'RegionPropertiesWidget',
    'StartPositionPropertiesWidget'
] 