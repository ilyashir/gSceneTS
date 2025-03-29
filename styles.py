class ButtonStyles:
    # Цветовая схема Cursor IDE
    PRIMARY_COLOR = "#007ACC"  # Синий как в Cursor
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
    
    # Стили для основных кнопок (Наблюдатель, Рисование, Редактирование)
    MODE_BUTTON = f"""
        QPushButton {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 120px;
        }}
        
        QPushButton:hover {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
        }}
        
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
            border: 1px solid {PRIMARY_COLOR};
        }}
        
        QPushButton:checked, QPushButton:flat {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
            border: 1px solid {PRIMARY_DARK};
        }}
    """
    
    DRAWING_BUTTON = f"""
        QToolButton {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            padding: 5px;
            min-width: 50px;
            min-height: 50px;
        }}
        QToolButton:hover {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
        }}
        QToolButton:checked {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
            border: 2px solid {PRIMARY_DARK};
        }}
        QToolButton:disabled {{
            background-color: {SECONDARY_DARK};
            color: {BORDER_COLOR};
        }}
    """

    STATUS_LABEL = f"""
        QLabel {{
            padding: 5px;
            border-radius: 3px;
            font-weight: bold;
            color: {TEXT_COLOR};
        }}
    """

    COORDS_LABEL = f"""
        QLabel {{
            font-size: 14px;
            color: white;
            background-color: {SECONDARY_COLOR};
            padding: 5px;
            border-radius: 3px;
        }}
    """
    
    # Основной стиль для главного окна приложения в Cursor-стиле
    CURSOR_MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
        QWidget {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
        QGraphicsView {{
            background-color: white;
            border: 1px solid {BORDER_COLOR};
        }}
        QPushButton {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 5px 10px;
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
        }}
        QLineEdit, QTextEdit {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 5px;
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 2px 5px;
            padding-right: 20px;
            min-height: 22px;
            min-width: 65px;
            selection-background-color: {PRIMARY_COLOR}; 
        }}
    """
    
    # Стиль для окна свойств
    CURSOR_PROPERTIES_WINDOW = f"""
        QWidget {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
        }}
        QLabel {{
            color: {TEXT_COLOR};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 1px;
            padding: 1px 2px;
            padding-right: 20px;
            min-height: 22px;
            min-width: 50px;
            selection-background-color: {PRIMARY_COLOR}; 
        }}
        
        /* Подсветка при наведении */
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
            background-color: {PRIMARY_COLOR};
        }}
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {PRIMARY_COLOR};
        }}
        QGroupBox {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            margin-top: 10px;
            color: {TEXT_COLOR};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
        }}
        QLineEdit {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 3px;
            selection-background-color: {PRIMARY_COLOR};
        }}
    """
    
    # Стиль для координат в стиле Cursor
    CURSOR_COORDS_LABEL = f"""
        QLabel {{
            font-size: 14px;
            color: {TEXT_COLOR};
            background-color: {SECONDARY_COLOR};
            padding: 5px;
            border-radius: 3px;
            border: 1px solid {BORDER_COLOR};
        }}
    """
    
    # Стиль для кнопки переключения свойств в Cursor-стиле
    CURSOR_TOGGLE_BUTTON = f"""
        QToolButton {{
            background-color: {PANEL_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 2px;
            color: {TEXT_COLOR};
        }}
        QToolButton:hover {{
            background-color: {SECONDARY_DARK};
        }}
        QToolButton:checked {{
            background-color: {PRIMARY_COLOR};
            border: 2px solid {PRIMARY_DARK};
        }}
    """
    
    # Основной стиль для главного окна приложения
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
        QWidget {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
        QPushButton {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 5px 10px;
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
        }}
        QLineEdit, QTextEdit {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 5px;
            cursor: text;
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 2px 5px;
            padding-right: 20px;
            min-height: 22px;
            min-width: 65px;
            selection-background-color: {PRIMARY_COLOR}; 
            cursor: text;
        }}
        QToolBar {{
            background-color: {PANEL_COLOR};
            border: none;
        }}
        QDockWidget {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
        }}
        QDockWidget::title {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
            padding: 5px;
        }}
        QCheckBox {{
            color: {TEXT_COLOR};
        }}
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR};
        }}
    """
    
    # Стиль для окна свойств
    PROPERTIES_WINDOW = f"""
        QWidget {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
        }}
        QLabel {{
            color: {TEXT_COLOR};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {SECONDARY_DARK};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            padding: 3px;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            height: 11px;
            border-left: 1px solid {BORDER_COLOR};
            border-top-right-radius: 3px;
            background-color: {PANEL_COLOR};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            height: 11px;
            border-left: 1px solid {BORDER_COLOR};
            border-bottom-right-radius: 3px;
            background-color: {PANEL_COLOR};
        }}
    """
    
    # Стиль для диалоговых окон
    DIALOG = f"""
        QDialog {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
        QMessageBox {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
        }}
    """
    
    # Стиль для элементов сцены в Cursor-стиле, но с белым фоном для самой сцены
    CURSOR_SCENE_STYLE = f"""
        QGraphicsView {{
            background-color: white;
            border: 1px solid {BORDER_COLOR};
        }}
    """
    
    # Стили для кнопок инструментов (Стена, Регион)
    TOOL_BUTTON = f"""
        QPushButton {{
            background-color: {PANEL_COLOR};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 6px 12px;
            margin: 2px;
            font-weight: normal;
        }}
        
        QPushButton:hover {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
        }}
        
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
            border: 1px solid {PRIMARY_COLOR};
        }}
        
        QPushButton:checked, QPushButton:flat {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
            border: 1px solid {PRIMARY_DARK};
        }}
        
        QPushButton:disabled {{
            background-color: {SECONDARY_DARK};
            color: {BORDER_COLOR};
            border: 1px solid {BORDER_COLOR};
            opacity: 0.7;
        }}
    """
    
    # Акцентированная кнопка для важных действий
    ACCENT_BUTTON = f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: {TEXT_HIGHLIGHT};
            border: 1px solid {PRIMARY_DARK};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: #0088E0;
            border: 1px solid {PRIMARY_COLOR};
        }}
        
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
        }}
    """
    
    # Стиль для чекбоксов
    CHECKBOX_STYLE = f"""
        QCheckBox {{
            color: {TEXT_COLOR};
            spacing: 8px;
            padding: 8px 0;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            background-color: {SECONDARY_DARK};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR};
            image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 16 16'><path fill='white' d='M13 4L6 11 3 8 2 9 6 13 14 5 13 4z'/></svg>");
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {PRIMARY_COLOR};
        }}
    """ 