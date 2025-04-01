"""
Реализация горячих клавиш для приложения.
"""

import logging
from PyQt6.QtCore import Qt

from .shortcuts_manager import ShortcutsManager

logger = logging.getLogger(__name__)

class AppShortcutsManager(ShortcutsManager):
    """
    Менеджер горячих клавиш, специфичный для нашего приложения.
    
    Настраивает горячие клавиши для основных функций приложения.
    """
    
    def __init__(self, main_window):
        """
        Инициализирует менеджер горячих клавиш приложения.
        
        Args:
            main_window: Главное окно приложения
        """
        super().__init__(main_window)
        logger.debug("Инициализирован менеджер горячих клавиш приложения")
    
    def setup_all_shortcuts(self):
        """
        Настраивает все горячие клавиши для приложения.
        """
        self.setup_navigation_shortcuts()
        self.setup_mode_shortcuts()
        self.setup_tool_shortcuts()
        self.setup_file_shortcuts()
        self.setup_edit_shortcuts()
        
        logger.debug("Настроены все горячие клавиши")
    
    def setup_navigation_shortcuts(self):
        """
        Настраивает горячие клавиши для навигации.
        """
        # Увеличение масштаба
        self.register_from_config("zoom_in", 
                                 lambda: self.main_window.field_widget.zoomIn())
        
        # Уменьшение масштаба
        self.register_from_config("zoom_out", 
                                 lambda: self.main_window.field_widget.zoomOut())
        
        # Сброс масштаба
        self.register_from_config("reset_zoom", 
                                 lambda: self.main_window.field_widget.resetScale())
        
        logger.debug("Настроены горячие клавиши для навигации")
    
    def setup_mode_shortcuts(self):
        """
        Настраивает горячие клавиши для переключения режимов.
        """
        # Режим наблюдателя
        self.register_from_config("observer_mode", 
                                 lambda: self.main_window.set_mode("observer"))
        
        # Режим рисования
        self.register_from_config("drawing_mode", 
                                 lambda: self.main_window.set_mode("drawing"))
        
        # Режим редактирования
        self.register_from_config("edit_mode", 
                                 lambda: self.main_window.set_mode("edit"))
        
        logger.debug("Настроены горячие клавиши для переключения режимов")
    
    def setup_tool_shortcuts(self):
        """
        Настраивает горячие клавиши для инструментов рисования.
        
        Эти клавиши активны только в режиме рисования.
        """
        # Инструмент Стена
        self.register_from_config("wall_tool", 
                                 lambda: self.main_window.set_drawing_type("wall"))
        
        # Инструмент Регион
        self.register_from_config("region_tool", 
                                 lambda: self.main_window.set_drawing_type("region"))
        
        logger.debug("Настроены горячие клавиши для инструментов рисования")
    
    def setup_file_shortcuts(self):
        """
        Настраивает горячие клавиши для файловых операций.
        """
        # Генерировать XML
        self.register_from_config("generate_xml", 
                                 lambda: self.main_window.generate_xml())
        
        logger.debug("Настроены горячие клавиши для файловых операций")
    
    def setup_edit_shortcuts(self):
        """
        Настраивает горячие клавиши для операций редактирования.
        """
        # Удаление выбранного объекта
        self.register_from_config("delete", 
                                 lambda: self.main_window.field_widget.delete_selected_item())
        
        logger.debug("Настроены горячие клавиши для операций редактирования") 