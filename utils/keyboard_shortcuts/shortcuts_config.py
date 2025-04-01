"""
Конфигурация горячих клавиш приложения.
"""

from enum import Enum, auto
from PyQt6.QtCore import Qt


class ShortcutCategory(Enum):
    """Категории горячих клавиш."""
    FILE = auto()         # Файловые операции
    EDIT = auto()         # Редактирование
    VIEW = auto()         # Просмотр
    NAVIGATION = auto()   # Навигация
    MODE = auto()         # Режимы работы
    TOOLS = auto()        # Инструменты
    
    @classmethod
    def get_display_name(cls, category):
        """Возвращает отображаемое имя категории."""
        display_names = {
            cls.FILE: "Файл",
            cls.EDIT: "Редактирование",
            cls.VIEW: "Вид",
            cls.NAVIGATION: "Навигация",
            cls.MODE: "Режимы",
            cls.TOOLS: "Инструменты"
        }
        return display_names.get(category, str(category))


# Определяем горячие клавиши по умолчанию
DEFAULT_SHORTCUTS = {
    # Файловые операции
    "new_scene": {
        "key": "Ctrl+N",
        "display_name": "Новая сцена",
        "description": "Создать новую сцену",
        "category": ShortcutCategory.FILE
    },
    "open_scene": {
        "key": "Ctrl+O",
        "display_name": "Открыть сцену",
        "description": "Открыть существующую сцену",
        "category": ShortcutCategory.FILE
    },
    "save_scene": {
        "key": "Ctrl+S",
        "display_name": "Сохранить сцену",
        "description": "Сохранить текущую сцену",
        "category": ShortcutCategory.FILE
    },
    "save_scene_as": {
        "key": "Ctrl+Shift+S",
        "display_name": "Сохранить сцену как",
        "description": "Сохранить текущую сцену с новым именем",
        "category": ShortcutCategory.FILE
    },
    "export_image": {
        "key": "Ctrl+E",
        "display_name": "Экспорт изображения",
        "description": "Экспортировать сцену как изображение",
        "category": ShortcutCategory.FILE
    },
    "generate_xml": {
        "key": "Ctrl+G",
        "display_name": "Генерировать XML",
        "description": "Генерировать XML-представление сцены",
        "category": ShortcutCategory.FILE
    },
    
    # Редактирование
    "delete": {
        "key": "Delete",
        "display_name": "Удалить",
        "description": "Удалить выбранный объект",
        "category": ShortcutCategory.EDIT
    },
    "select_all": {
        "key": "Ctrl+A",
        "display_name": "Выбрать все",
        "description": "Выбрать все объекты на сцене",
        "category": ShortcutCategory.EDIT
    },
    
    # Навигация
    "zoom_in": {
        "key": "Ctrl++",
        "display_name": "Увеличить",
        "description": "Увеличить масштаб",
        "category": ShortcutCategory.NAVIGATION
    },
    "zoom_out": {
        "key": "Ctrl+-",
        "display_name": "Уменьшить",
        "description": "Уменьшить масштаб",
        "category": ShortcutCategory.NAVIGATION
    },
    "reset_zoom": {
        "key": "Ctrl+0",
        "display_name": "Сбросить масштаб",
        "description": "Сбросить масштаб к 100%",
        "category": ShortcutCategory.NAVIGATION
    },
    
    # Режимы работы
    "observer_mode": {
        "key": "F1",
        "display_name": "Режим наблюдателя",
        "description": "Переключиться в режим наблюдателя",
        "category": ShortcutCategory.MODE
    },
    "drawing_mode": {
        "key": "F2",
        "display_name": "Режим рисования",
        "description": "Переключиться в режим рисования",
        "category": ShortcutCategory.MODE
    },
    "edit_mode": {
        "key": "F3",
        "display_name": "Режим редактирования",
        "description": "Переключиться в режим редактирования",
        "category": ShortcutCategory.MODE
    },
    
    # Инструменты рисования
    "wall_tool": {
        "key": "W",
        "display_name": "Инструмент Стена",
        "description": "Выбрать инструмент Стена",
        "category": ShortcutCategory.TOOLS
    },
    "region_tool": {
        "key": "R",
        "display_name": "Инструмент Регион",
        "description": "Выбрать инструмент Регион",
        "category": ShortcutCategory.TOOLS
    }
}

def get_shortcut_by_name(name):
    """Возвращает конфигурацию горячей клавиши по имени."""
    return DEFAULT_SHORTCUTS.get(name)

def get_shortcuts_by_category(category):
    """Возвращает список горячих клавиш по категории."""
    return {name: config for name, config in DEFAULT_SHORTCUTS.items() 
            if config["category"] == category} 