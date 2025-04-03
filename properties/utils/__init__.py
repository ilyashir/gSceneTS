"""
Модуль utils содержит вспомогательные функции и утилиты для работы со свойствами.
Включает в себя функции для:
- Работы с привязкой к сетке
- Управления сигналами
- Расчета диапазонов значений
"""

from properties.utils.grid_snap_utils import (
    snap_to_grid, snap_rotation_to_grid, is_snap_enabled, get_grid_size
) 