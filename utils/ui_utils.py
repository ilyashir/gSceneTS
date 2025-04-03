"""
Утилиты для работы с UI-компонентами.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSpinBox, QDoubleSpinBox,
    QSlider, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def create_labeled_spinbox(
    label_text: str,
    min_value: int,
    max_value: int,
    default_value: int = 0,
    parent: QWidget = None
) -> Tuple[QLabel, QSpinBox]:
    """
    Создание пары метка + спинбокс.
    
    Args:
        label_text: Текст метки
        min_value: Минимальное значение
        max_value: Максимальное значение
        default_value: Значение по умолчанию
        parent: Родительский виджет
        
    Returns:
        Tuple[QLabel, QSpinBox]: (метка, спинбокс)
    """
    label = QLabel(label_text, parent)
    spinbox = QSpinBox(parent)
    spinbox.setRange(min_value, max_value)
    spinbox.setValue(default_value)
    return label, spinbox

def create_labeled_double_spinbox(
    label_text: str,
    min_value: float,
    max_value: float,
    default_value: float = 0.0,
    decimals: int = 2,
    parent: QWidget = None
) -> Tuple[QLabel, QDoubleSpinBox]:
    """
    Создание пары метка + спинбокс с плавающей точкой.
    
    Args:
        label_text: Текст метки
        min_value: Минимальное значение
        max_value: Максимальное значение
        default_value: Значение по умолчанию
        decimals: Количество знаков после запятой
        parent: Родительский виджет
        
    Returns:
        Tuple[QLabel, QDoubleSpinBox]: (метка, спинбокс)
    """
    label = QLabel(label_text, parent)
    spinbox = QDoubleSpinBox(parent)
    spinbox.setRange(min_value, max_value)
    spinbox.setDecimals(decimals)
    spinbox.setValue(default_value)
    return label, spinbox

def create_labeled_slider(
    label_text: str,
    min_value: int,
    max_value: int,
    default_value: int = 0,
    orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    parent: QWidget = None
) -> Tuple[QLabel, QSlider]:
    """
    Создание пары метка + слайдер.
    
    Args:
        label_text: Текст метки
        min_value: Минимальное значение
        max_value: Максимальное значение
        default_value: Значение по умолчанию
        orientation: Ориентация слайдера
        parent: Родительский виджет
        
    Returns:
        Tuple[QLabel, QSlider]: (метка, слайдер)
    """
    label = QLabel(label_text, parent)
    slider = QSlider(orientation, parent)
    slider.setRange(min_value, max_value)
    slider.setValue(default_value)
    return label, slider

def create_group_box(
    title: str,
    layout: QVBoxLayout,
    parent: QWidget = None
) -> QGroupBox:
    """
    Создание группы с заголовком.
    
    Args:
        title: Заголовок группы
        layout: Макет для содержимого
        parent: Родительский виджет
        
    Returns:
        QGroupBox: Созданная группа
    """
    group = QGroupBox(title, parent)
    group.setLayout(layout)
    return group

def create_horizontal_layout(parent: QWidget = None) -> QHBoxLayout:
    """
    Создание горизонтального макета.
    
    Args:
        parent: Родительский виджет
        
    Returns:
        QHBoxLayout: Созданный макет
    """
    layout = QHBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    return layout

def create_vertical_layout(parent: QWidget = None) -> QVBoxLayout:
    """
    Создание вертикального макета.
    
    Args:
        parent: Родительский виджет
        
    Returns:
        QVBoxLayout: Созданный макет
    """
    layout = QVBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    return layout 