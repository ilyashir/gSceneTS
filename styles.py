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
    FLOAT_BUTTON_COLOR = "#E6E6E6" # Синий для плавающих кнопок
    CLOSE_BUTTON_COLOR = "#E6E6E6" # Красный для кнопки закрыть
    
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
    FLOAT_BUTTON_COLOR = "#252526" # Синий для плавающих кнопок
    CLOSE_BUTTON_COLOR = "#252526" # Красный для кнопки закрыть
    
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
                'warning': cls.WARNING_COLOR,
                'float_button': cls.FLOAT_BUTTON_COLOR,
                'close_button': cls.CLOSE_BUTTON_COLOR
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
                'warning': cls.LIGHT_WARNING_COLOR,
                'float_button': cls.FLOAT_BUTTON_COLOR,
                'close_button': cls.CLOSE_BUTTON_COLOR
            }
    
    @classmethod
    def get_window_style(cls, is_dark_theme=True):
        """Генерирует стиль для основного окна приложения"""
        colors = cls._get_theme_colors(is_dark_theme)

        # Вычисляем цвета для эффектов
        hover_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.1)"
        focus_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.2)"

        # Определяем фон/цвет для кнопок док-виджета
        if is_dark_theme:
            # Темная тема: фон кнопок светлый, рамка темная
            dock_button_bg = "#7A7A7A" # Светло-серый фон (#E6E6E6)
            dock_button_border = cls.SECONDARY_DARK    # Очень темная рамка (#252526)
            dock_button_hover_bg = cls.LIGHT_BORDER_COLOR # Еще светлее при наведении (#CCCCCC)
            dock_button_pressed_bg = cls.LIGHT_PANEL_COLOR # Почти белый при нажатии (#F9F9F9)
        else:
            # Светлая тема: фон кнопок темный, рамка светлая
            dock_button_bg = cls.LIGHT_SECONDARY_DARK        # Темно-серый фон (#555555)
            dock_button_border = cls.LIGHT_BORDER_COLOR # Светлая рамка (#CCCCCC)
            dock_button_hover_bg = cls.LIGHT_BORDER_COLOR # Еще темнее при наведении (#333333)
            dock_button_pressed_bg = cls.SECONDARY_DARK  # Почти черный при нажатии (#252526)

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
                padding: 4px 8px;
                min-height: 24px;
            }}
            QLineEdit:hover, QTextEdit:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 4px 8px;
                padding-right: 20px;
                min-height: 24px;
                min-width: 80px;
                selection-background-color: {colors['primary']};
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
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
                padding: 3px; 
                padding-right: 50px; 
                text-align: left;
                spacing: 4px;
            }}
            /* Стили для кнопок БЕЗ кастомных иконок */
            QDockWidget::close-button, QDockWidget::float-button {{
                background-color: {dock_button_bg}; /* Контрастный фон */
                border: 1px solid {dock_button_border}; /* Контрастная рамка */
                border-radius: 2px;
                width: 16px; 
                height: 16px;
            }}
            /* Позиционирование оставляем */
            QDockWidget::close-button {{
                subcontrol-position: top right;
                subcontrol-origin: margin;
                position: absolute; 
                top: 2px; 
                right: 5px; 
                bottom: 2px;
            }}
            QDockWidget::float-button {{
                subcontrol-position: top right;
                subcontrol-origin: margin;
                position: absolute; 
                top: 2px; 
                right: 25px;
                bottom: 2px;
            }}

            /* Общие стили hover/pressed */
            QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
                background-color: {dock_button_hover_bg}; 
            }}
            QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {{
                background-color: {dock_button_pressed_bg};
                border-color: {dock_button_border}; /* Оставляем ту же рамку при нажатии */
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
        
        # Вычисляем цвета для эффектов
        hover_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.1)"
        focus_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.2)"
        
        return f"""
            QWidget {{
                background-color: {colors['panel']};
                color: {colors['text']};
            }}
            QLabel {{
                color: {colors['text']};
                padding: 2px;
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 4px 8px;
                padding-right: 20px;
                min-height: 24px;
                min-width: 80px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
            }}
            QLineEdit {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 4px 8px;
                min-height: 24px;
            }}
            QLineEdit:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QLineEdit:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
            }}
            QPushButton {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {colors['primary_dark']};
            }}
            QComboBox {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 4px 8px;
                min-height: 24px;
            }}
            QComboBox:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QComboBox:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url(resources/icons/dropdown_arrow.png);
                width: 12px;
                height: 12px;
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
    """
    
    @classmethod
    def get_theme_switch_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопки переключения темы"""
        colors = cls._get_theme_colors(is_dark_theme)
        return f"""
            QPushButton {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 15px;
                padding: 5px;
                font-size: 16px;
                min-width: 30px;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
            }}
        """
        
    @classmethod
    def get_scale_button_style(cls, is_dark_theme=True):
        """Генерирует стиль для кнопок масштабирования"""
        colors = cls._get_theme_colors(is_dark_theme)
        button_bg = "#4a4a4a" if is_dark_theme else "#e0e0e0"
        border_color = colors['border']
        hover_bg = "#555555" if is_dark_theme else "#d0d0d0"
        pressed_bg = "#333333" if is_dark_theme else "#c0c0c0"
        disabled_bg = "#3a3a3a" if is_dark_theme else "#f0f0f0"
        
        return f"""
            QToolButton {{
                background-color: {button_bg};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
                min-width: 30px;
                min-height: 30px;
                font-size: 16px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QToolButton:hover {{
                background-color: {hover_bg};
            }}
            QToolButton:pressed {{
                background-color: {pressed_bg};
            }}
            QToolButton:disabled {{
                color: gray;
                background-color: {disabled_bg};
            }}
        """
        
    @classmethod
    def get_scale_display_style(cls, is_dark_theme=True):
        """Генерирует стиль для поля отображения текущего масштаба"""
        colors = cls._get_theme_colors(is_dark_theme)
        field_bg = "#2d2d2d" if is_dark_theme else "#f5f5f5"
        border_color = colors['border']
        
        return f"""
            QLineEdit {{
                background-color: {field_bg};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
                min-height: 30px;
                font-size: 14px;
                font-weight: bold;
                color: {colors['text']};
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