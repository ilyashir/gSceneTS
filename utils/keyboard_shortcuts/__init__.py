"""
Модуль для работы с горячими клавишами приложения.
"""

from .shortcuts_manager import ShortcutsManager
from .shortcuts_config import DEFAULT_SHORTCUTS, ShortcutCategory
from .app_shortcuts import AppShortcutsManager

__all__ = ['ShortcutsManager', 'DEFAULT_SHORTCUTS', 'ShortcutCategory', 'AppShortcutsManager'] 