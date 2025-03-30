class AppStyles:
    #===============================
    # БАЗОВЫЕ ЦВЕТОВЫЕ КОНСТАНТЫ
    #===============================
    
    # Тёмная цветовая схема 
    PRIMARY_COLOR = "#007ACC"  # Синий 
    PRIMARY_DARK = "#005A9E"  # Темно-синий
    SECONDARY_COLOR = "#1E1E1E"  # Общий фон
    SECONDARY_DARK = "#252526"  # Темный фон для элементов ввода
    PANEL_COLOR = "#333333"  # Панели и фон
    BORDER_COLOR = "#555555"  # Границы
    TEXT_COLOR = "#CCCCCC"  # Основной текст
    TEXT_HIGHLIGHT = "#FFFFFF"  # Выделенный текст
    SUCCESS_COLOR = "#6A9955"  # Зеленый для подтверждения
    ERROR_COLOR = "#F14C4C"  # Красный для ошибок
    WARNING_COLOR = "#CCA700"  # Желтый для предупреждений
    
    # Светлая цветовая схема 
    LIGHT_PRIMARY_COLOR = "#0078D7"  # Синий для светлой темы
    LIGHT_PRIMARY_DARK = "#106EBE"  # Темно-синий для светлой темы
    LIGHT_SECONDARY_COLOR = "#F3F3F3"  # Общий фон (светлый)
    LIGHT_SECONDARY_DARK = "#E6E6E6"  # Светло-серый фон для элементов ввода
    LIGHT_PANEL_COLOR = "#F9F9F9"  # Панели и фон (светлый)
    LIGHT_BORDER_COLOR = "#CCCCCC"  # Границы (светлый)
    LIGHT_TEXT_COLOR = "#333333"  # Основной текст (темный)
    LIGHT_TEXT_HIGHLIGHT = "#000000"  # Выделенный текст (черный)
    LIGHT_SUCCESS_COLOR = "#107C10"  # Зеленый для подтверждения
    LIGHT_ERROR_COLOR = "#E81123"  # Красный для ошибок
    LIGHT_WARNING_COLOR = "#FF8C00"  # Оранжевый для предупреждений
    
    #===============================
    # ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ЦВЕТОВ
    #===============================
    
    @classmethod
    def get_primary_color(cls, is_dark_theme=True):
        return cls.PRIMARY_COLOR if is_dark_theme else cls.LIGHT_PRIMARY_COLOR
    
    @classmethod
    def get_primary_dark(cls, is_dark_theme=True):
        return cls.PRIMARY_DARK if is_dark_theme else cls.LIGHT_PRIMARY_DARK
    
    @classmethod
    def get_secondary_color(cls, is_dark_theme=True):
        return cls.SECONDARY_COLOR if is_dark_theme else cls.LIGHT_SECONDARY_COLOR
    
    @classmethod
    def get_secondary_dark(cls, is_dark_theme=True):
        return cls.SECONDARY_DARK if is_dark_theme else cls.LIGHT_SECONDARY_DARK
    
    @classmethod
    def get_panel_color(cls, is_dark_theme=True):
        return cls.PANEL_COLOR if is_dark_theme else cls.LIGHT_PANEL_COLOR
    
    @classmethod
    def get_border_color(cls, is_dark_theme=True):
        return cls.BORDER_COLOR if is_dark_theme else cls.LIGHT_BORDER_COLOR
    
    @classmethod
    def get_text_color(cls, is_dark_theme=True):
        return cls.TEXT_COLOR if is_dark_theme else cls.LIGHT_TEXT_COLOR
    
    @classmethod
    def get_text_highlight(cls, is_dark_theme=True):
        return cls.TEXT_HIGHLIGHT if is_dark_theme else cls.LIGHT_TEXT_HIGHLIGHT
    
    @classmethod
    def get_success_color(cls, is_dark_theme=True):
        return cls.SUCCESS_COLOR if is_dark_theme else cls.LIGHT_SUCCESS_COLOR
    
    @classmethod
    def get_error_color(cls, is_dark_theme=True):
        return cls.ERROR_COLOR if is_dark_theme else cls.LIGHT_ERROR_COLOR
    
    @classmethod
    def get_warning_color(cls, is_dark_theme=True):
        return cls.WARNING_COLOR if is_dark_theme else cls.LIGHT_WARNING_COLOR
    
    #===============================
    # ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ СТИЛЕЙ
    #===============================
    
    @classmethod
    def _get_theme_colors(cls, is_dark_theme=True):
        """Возвращает словарь с цветами для текущей темы"""
        if is_dark_theme:
            return {
                'primary': cls.PRIMARY_COLOR,
                'primary_dark': cls.PRIMARY_DARK,
                'background': cls.SECONDARY_COLOR,
                'secondary_dark': cls.SECONDARY_DARK,
                'panel': cls.PANEL_COLOR,
                'border': cls.BORDER_COLOR,
                'text': cls.TEXT_COLOR,
                'text_highlight': cls.TEXT_HIGHLIGHT,
                'success': cls.SUCCESS_COLOR,
                'error': cls.ERROR_COLOR,
                'warning': cls.WARNING_COLOR
            }
        else:
            return {
                'primary': cls.LIGHT_PRIMARY_COLOR,
                'primary_dark': cls.LIGHT_PRIMARY_DARK,
                'background': cls.LIGHT_SECONDARY_COLOR,
                'secondary_dark': cls.LIGHT_SECONDARY_DARK,
                'panel': cls.LIGHT_PANEL_COLOR,
                'border': cls.LIGHT_BORDER_COLOR,
                'text': cls.LIGHT_TEXT_COLOR,
                'text_highlight': cls.LIGHT_TEXT_HIGHLIGHT,
                'success': cls.LIGHT_SUCCESS_COLOR,
                'error': cls.LIGHT_ERROR_COLOR,
                'warning': cls.LIGHT_WARNING_COLOR
            }
    
    @classmethod
    def get_window_style(cls, is_dark_theme=True):
        """Генерирует стиль для основного окна приложения"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
            QMainWindow {{
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            QGraphicsView {{
                background-color: white;
                border: 1px solid {colors['border']};
            }}
            QPushButton {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {colors['primary_dark']};
            }}
            QLineEdit, QTextEdit {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 5px;
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 2px 5px;
                padding-right: 20px;
                min-height: 22px;
                min-width: 65px;
                selection-background-color: {colors['primary']}; 
            }}
            QToolBar {{
                background-color: {colors['panel']};
                border: none;
            }}
            QDockWidget {{
                background-color: {colors['panel']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
            QDockWidget::title {{
                background-color: {colors['panel']};
                color: {colors['text']};
                padding: 5px;
            }}
            QCheckBox {{
                color: {colors['text']};
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
            }}
            QGroupBox {{
                border: 1px solid {colors['border']};
                border-radius: 5px;
                margin-top: 10px;
                color: {colors['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
        """
    
    @classmethod
    def get_properties_style(cls, is_dark_theme=True):
        """Генерирует стиль для окна свойств"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
            QWidget {{
                background-color: {colors['panel']};
                color: {colors['text']};
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QGroupBox {{
                border: 1px solid {colors['border']};
                border-radius: 5px;
                margin-top: 10px;
                color: {colors['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
            QDockWidget {{
                background-color: {colors['panel']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
            QDockWidget::title {{
                background-color: {colors['panel']};
                color: {colors['text']};
                padding: 5px;
            }}
            QDockWidget::close-button, QDockWidget::float-button {{
                background-color: {colors['border'] if is_dark_theme else colors['secondary_dark']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
                background-color: {colors['primary']};
            }}
        """
    
    @classmethod
    def get_coords_label_style(cls, is_dark_theme=True):
        """Генерирует стиль для метки координат"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QLabel {{
            font-size: 14px;
            color: {colors['text']};
            background-color: {colors['background']};
            padding: 5px;
            border-radius: 3px;
        }}
    """
    
    @classmethod
    def get_checkbox_style(cls, is_dark_theme=True):
        """Генерирует стиль для чекбоксов"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QCheckBox {{
            color: {colors['text']};
            spacing: 8px;
            padding: 8px 0;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['secondary_dark']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 16 16'><path fill='white' d='M13 4L6 11 3 8 2 9 6 13 14 5 13 4z'/></svg>");
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
        }}
    """
    
    @classmethod
    def get_dialog_style(cls, is_dark_theme=True):
        """Генерирует стиль для диалогов"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QDialog {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        QMessageBox {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
    """
    
    @classmethod
    def get_toggle_button_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопок переключения"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QPushButton {{
            background-color: {colors['panel']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 3px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {colors['primary']};
            color: white;
        }}
    """
    
    @classmethod
    def get_mode_button_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопок режимов"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QPushButton {{
            background-color: {colors['panel']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 120px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary']};
            color: {colors['text_highlight']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
            border: 1px solid {colors['primary']};
        }}
        
        QPushButton:checked, QPushButton:flat {{
            background-color: {colors['primary']};
            color: {colors['text_highlight']};
            border: 1px solid {colors['primary_dark']};
        }}
    """
    
    @classmethod
    def get_tool_button_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопок инструментов"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QPushButton {{
            background-color: {colors['panel']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            margin: 2px;
            font-weight: normal;
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary']};
            color: {colors['text_highlight']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
            border: 1px solid {colors['primary']};
        }}
        
        QPushButton:checked, QPushButton:flat {{
            background-color: {colors['primary']};
            color: {colors['text_highlight']};
            border: 1px solid {colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['secondary_dark']};
            color: {colors['border']};
            border: 1px solid {colors['border']};
            opacity: 0.7;
        }}
    """
    
    @classmethod
    def get_accent_button_style(cls, is_dark_theme=True):
        """Генерирует стиль для акцентированных кнопок"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QPushButton {{
            background-color: {colors['primary']};
            color: {colors['text_highlight']};
            border: 1px solid {colors['primary_dark']};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: #0088E0;
            border: 1px solid {colors['primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
        }}
    """
    
    @classmethod
    def get_mode_label_style(cls, is_dark_theme=True):
        """Генерирует стиль для меток режимов"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QLabel {{
            color: {colors['text']};
            font-weight: bold;
        }}
    """
    
    @classmethod
    def get_scene_style(cls, is_dark_theme=True):
        """Генерирует стиль для сцены"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
        QGraphicsView {{
            background-color: white;
            border: 1px solid {colors['border']};
        }}
        
        QGraphicsView QScrollBar:horizontal {{
            height: 10px;
            background: transparent;
            margin: 0px;
            border-radius: 5px;
        }}
        
        QGraphicsView QScrollBar:vertical {{
            width: 10px;
            background: transparent;
            margin: 0px;
            border-radius: 5px;
        }}
        
        QGraphicsView QScrollBar::handle:horizontal,
        QGraphicsView QScrollBar::handle:vertical {{
            background: rgba(100, 100, 100, 0.5);
            border-radius: 5px;
        }}
        
        QGraphicsView QScrollBar::handle:horizontal:hover,
        QGraphicsView QScrollBar::handle:vertical:hover {{
            background: rgba(100, 100, 100, 0.8);
        }}
        
        QGraphicsView QScrollBar::add-line:horizontal,
        QGraphicsView QScrollBar::sub-line:horizontal,
        QGraphicsView QScrollBar::add-line:vertical,
        QGraphicsView QScrollBar::sub-line:vertical {{
            width: 0px;
            height: 0px;
        }}
        
        QGraphicsView QScrollBar::add-page:horizontal,
        QGraphicsView QScrollBar::sub-page:horizontal,
        QGraphicsView QScrollBar::add-page:vertical,
        QGraphicsView QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
    """
    
    @classmethod
    def get_theme_switch_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопки переключения темы"""
        colors = cls._get_theme_colors(is_dark_theme)
        background = '#1E1E1E' if is_dark_theme else '#F3F3F3'
        return f"""
        QPushButton {{
            background-color: {background};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 10px;
            padding: 0px 3px;
            margin: 2px;
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
            font-size: 14px;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: {colors['primary']};
            color: white;
        }}
    """


# Создание констант после определения класса
#===============================
# ТЕМНЫЕ СТИЛИ (DARK THEME)
#===============================

# Главное окно (темная тема)
AppStyles.DARK_MAIN_WINDOW = AppStyles.get_window_style(True)

# Окно свойств (темная тема)
AppStyles.DARK_PROPERTIES_WINDOW = AppStyles.get_properties_style(True)

# Метка координат (темная тема)
AppStyles.DARK_COORDS_LABEL = AppStyles.get_coords_label_style(True)

# Диалоговые окна (темная тема)
AppStyles.DARK_DIALOG = AppStyles.get_dialog_style(True)

# Стиль для элементов сцены (темная тема)
AppStyles.DARK_SCENE_STYLE = AppStyles.get_scene_style(True)

# Кнопка переключения свойств (темная тема)
AppStyles.DARK_TOGGLE_BUTTON = AppStyles.get_toggle_button_style(True)

# Стиль для кнопок режимов (темная тема)
AppStyles.DARK_MODE_BUTTON = AppStyles.get_mode_button_style(True)

# Стиль для кнопок инструментов (темная тема)
AppStyles.DARK_TOOL_BUTTON = AppStyles.get_tool_button_style(True)

# Акцентированная кнопка (темная тема)
AppStyles.DARK_ACCENT_BUTTON = AppStyles.get_accent_button_style(True)

# Стиль для чекбоксов (темная тема)
AppStyles.DARK_CHECKBOX_STYLE = AppStyles.get_checkbox_style(True)

# Стиль для меток статуса (темная тема)
AppStyles.DARK_STATUS_LABEL = AppStyles.get_mode_label_style(True)

#===============================
# СВЕТЛЫЕ СТИЛИ (LIGHT THEME)
#===============================

# Главное окно (светлая тема)
AppStyles.LIGHT_MAIN_WINDOW = AppStyles.get_window_style(False)

# Окно свойств (светлая тема)
AppStyles.LIGHT_PROPERTIES_WINDOW = AppStyles.get_properties_style(False)

# Метка координат (светлая тема)
AppStyles.LIGHT_COORDS_LABEL = AppStyles.get_coords_label_style(False)

# Стиль для элементов сцены (светлая тема)
AppStyles.LIGHT_SCENE_STYLE = AppStyles.get_scene_style(False)

# Стиль для кнопок тем (светлая тема)
AppStyles.LIGHT_THEME_BUTTON = AppStyles.get_toggle_button_style(False)

# Стиль для чекбоксов (светлая тема)
AppStyles.LIGHT_CHECKBOX_STYLE = AppStyles.get_checkbox_style(False)

# Стиль для меток режимов (светлая тема)
AppStyles.LIGHT_MODE_LABEL = AppStyles.get_mode_label_style(False)

# Стиль для кнопок переключения (светлая тема)
AppStyles.LIGHT_TOGGLE_BUTTON = AppStyles.get_toggle_button_style(False)

# Кнопки режимов (светлая тема)
AppStyles.LIGHT_MODE_BUTTON = AppStyles.get_mode_button_style(False)

# Кнопки инструментов (светлая тема)
AppStyles.LIGHT_TOOL_BUTTON = AppStyles.get_tool_button_style(False)

# Акцентированная кнопка (светлая тема)
AppStyles.LIGHT_ACCENT_BUTTON = AppStyles.get_accent_button_style(False)

# Диалоговые окна (светлая тема)
AppStyles.LIGHT_DIALOG = AppStyles.get_dialog_style(False) 