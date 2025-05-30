"""
Прокси-файл для окна свойств.

Обеспечивает обратную совместимость с существующим кодом проекта.
Импортирует класс PropertiesWindow из адаптера properties.properties_window_adapter.
"""

from properties.properties_window_adapter import PropertiesWindow

__all__ = ["PropertiesWindow"] 