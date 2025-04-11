"""
Менеджер горячих клавиш для приложения.
"""

import logging
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QObject

from .shortcuts_config import DEFAULT_SHORTCUTS

logger = logging.getLogger(__name__)

class ShortcutsManager(QObject):
    """
    Менеджер горячих клавиш приложения.
    
    Позволяет регистрировать, управлять и отслеживать горячие клавиши.
    """
    
    def __init__(self, main_window):
        """
        Инициализирует менеджер горячих клавиш.
        
        Args:
            main_window: Главное окно приложения, к которому будут привязаны горячие клавиши
        """
        super().__init__(main_window)
        self.main_window = main_window
        self.shortcuts = {}
        self.actions = {}
        logger.debug("Инициализирован менеджер горячих клавиш")
    
    def register_shortcut(self, name, key_sequence, callback, context=None, description=None):
        """
        Регистрирует новую горячую клавишу.
        
        Args:
            name: Уникальное имя для горячей клавиши
            key_sequence: Последовательность клавиш (строка или QKeySequence)
            callback: Функция, которая будет вызвана при нажатии горячей клавиши
            context: Контекст горячей клавиши (по умолчанию - Qt.ShortcutContext.WindowShortcut)
            description: Описание горячей клавиши для пользователя
            
        Returns:
            QShortcut: Созданный объект горячей клавиши
        """
        if name in self.shortcuts:
            logger.warning(f"[HOTKEY] Горячая клавиша с именем '{name}' уже зарегистрирована. Перезаписываем.")
        
        # Создаем объект QShortcut
        shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
        shortcut.activated.connect(callback)
        
        # Устанавливаем контекст, если указан
        if context:
            shortcut.setContext(context)
        
        # Сохраняем информацию о горячей клавише
        self.shortcuts[name] = {
            "shortcut": shortcut,
            "key_sequence": key_sequence,
            "callback": callback,
            "description": description or ""
        }
        
        logger.debug(f"[HOTKEY] Зарегистрирована горячая клавиша: {name} -> {key_sequence}")
        return shortcut
    
    def register_from_config(self, name, callback, context=None):
        """
        Регистрирует горячую клавишу из конфигурации по умолчанию.
        
        Args:
            name: Имя горячей клавиши в конфигурации
            callback: Функция, которая будет вызвана при нажатии горячей клавиши
            context: Контекст горячей клавиши
            
        Returns:
            QShortcut: Созданный объект горячей клавиши или None, если клавиша не найдена
        """
        shortcut_config = DEFAULT_SHORTCUTS.get(name)
        if not shortcut_config:
            logger.warning(f"[HOTKEY] Горячая клавиша с именем '{name}' не найдена в конфигурации.")
            return None
        
        return self.register_shortcut(
            name, 
            shortcut_config["key"],
            callback,
            context,
            shortcut_config.get("description")
        )
    
    def unregister_shortcut(self, name):
        """
        Удаляет зарегистрированную горячую клавишу.
        
        Args:
            name: Имя горячей клавиши
            
        Returns:
            bool: True, если клавиша была успешно удалена, иначе False
        """
        if name not in self.shortcuts:
            logger.warning(f"[HOTKEY] Горячая клавиша с именем '{name}' не зарегистрирована.")
            return False
        
        # Удаляем объект QShortcut
        shortcut_info = self.shortcuts.pop(name)
        shortcut_info["shortcut"].setEnabled(False)
        shortcut_info["shortcut"].deleteLater()
        
        logger.debug(f"[HOTKEY] Удалена горячая клавиша: {name}")
        return True
    
    def get_shortcut(self, name):
        """
        Возвращает объект горячей клавиши по имени.
        
        Args:
            name: Имя горячей клавиши
            
        Returns:
            dict: Информация о горячей клавише или None, если клавиша не найдена
        """
        return self.shortcuts.get(name)
    
    def setup_all_shortcuts(self):
        """
        Настраивает все горячие клавиши из конфигурации по умолчанию.
        
        Этот метод должен быть переопределен в подклассе.
        """
        logger.warning("Метод setup_all_shortcuts должен быть переопределен в подклассе.")
    
    def show_shortcuts_dialog(self):
        """
        Показывает диалоговое окно со списком всех доступных горячих клавиш.
        """
        if not self.shortcuts:
            QMessageBox.information(
                self.main_window,
                "Горячие клавиши",
                "Горячие клавиши не настроены."
            )
            return
        
        # Формируем текст с описанием всех горячих клавиш
        shortcuts_text = "Доступные горячие клавиши:\n\n"
        
        # Группируем горячие клавиши по категориям
        from .shortcuts_config import get_shortcuts_by_category, ShortcutCategory
        
        for category in ShortcutCategory:
            category_shortcuts = get_shortcuts_by_category(category)
            if not category_shortcuts:
                continue
            
            shortcuts_text += f"--- {ShortcutCategory.get_display_name(category)} ---\n"
            
            for name, config in category_shortcuts.items():
                if name in self.shortcuts:
                    display_name = config.get("display_name", name)
                    key = self.shortcuts[name]["key_sequence"]
                    shortcuts_text += f"{display_name}: {key}\n"
            
            shortcuts_text += "\n"
        
        # Показываем диалоговое окно
        QMessageBox.information(
            self.main_window,
            "Горячие клавиши",
            shortcuts_text
        ) 