"""
Базовый класс для всех виджетов свойств.
Содержит общие методы и функциональность для работы со свойствами элементов.
"""

from abc import abstractmethod
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QSlider, QPushButton, QSizePolicy, QSpacerItem, QGroupBox, QApplication, QStyle,
    QCheckBox, QStyleOptionSpinBox, QStyleOptionSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QCursor
from styles import AppStyles
import logging

logger = logging.getLogger(__name__)

class BasePropertiesWidget(QGroupBox):
    """
    Базовый класс для виджетов свойств элементов.
    
    Все виджеты свойств должны наследоваться от этого класса.
    """
    
    def __init__(self, title="Properties", parent=None, field_widget=None):
        """
        Инициализация базового виджета свойств.
        
        Args:
            title: Заголовок группы свойств
            parent: Родительский виджет
            field_widget: Виджет поля
        """
        super().__init__(title, parent)
        self.field_widget = field_widget
        self.initial_values = {}
        self.is_dark_theme = False  # По умолчанию светлая тема
        
        # Создаем основной вертикальный Layout
        self.properties_layout = QVBoxLayout()
        self.setLayout(self.properties_layout)
        
        # Применяем базовый стиль
        self.apply_theme()
        
        # Инициализируем интерфейс
        self.create_widgets()
        self.create_layouts()
        self.setup_connections()
        self.setup_cursors()
        self._setup_interactive_cursors()
        
    @abstractmethod
    def create_widgets(self):
        """Создает все виджеты. Должен быть реализован в дочерних классах."""
        pass
        
    @abstractmethod
    def create_layouts(self):
        """Создает и настраивает компоновку. Должен быть реализован в дочерних классах."""
        pass
        
    @abstractmethod
    def setup_connections(self):
        """Подключает сигналы и слоты. Должен быть реализован в дочерних классах."""
        pass

    def apply_theme(self, is_dark_theme=True):
        """
        Применение темы оформления к виджету.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.is_dark_theme = is_dark_theme
        if is_dark_theme:
            self.setStyleSheet(AppStyles.DARK_PROPERTIES_WINDOW)
        else:
            self.setStyleSheet(AppStyles.LIGHT_PROPERTIES_WINDOW)
        
    def apply_field_style(self, widget):
        """
        Применение стиля поля ввода.
        
        Args:
            widget: Виджет для стилизации
        """
        # Используем цвета фона в зависимости от темы
        bg_color = AppStyles.SECONDARY_DARK if self.is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
        text_color = AppStyles.TEXT_COLOR if self.is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
        border_color = AppStyles.BORDER_COLOR if self.is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        
        widget.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        
    def setup_cursors(self):
        """
        Установка курсоров для всех интерактивных элементов виджета.
        """
        # Устанавливаем курсоры для всех кнопок
        for button in self.findChildren(QPushButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Устанавливаем курсоры для чекбоксов
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Устанавливаем курсоры для SpinBox
        for spinbox in self.findChildren(QSpinBox) + self.findChildren(QDoubleSpinBox):
            # Получаем кнопки внутри спинбокса
            for child in spinbox.findChildren(QWidget):
                if 'Button' in child.__class__.__name__:
                    child.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _setup_interactive_cursors(self):
        """Настраивает курсоры для сложных виджетов (SpinBox, Slider)."""
        spin_boxes = self.findChildren(QSpinBox) + self.findChildren(QDoubleSpinBox)
        sliders = self.findChildren(QSlider)

        for widget in spin_boxes + sliders:
            widget.setMouseTracking(True)
            widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Обработка событий для SpinBox и Slider
        if isinstance(obj, (QSpinBox, QDoubleSpinBox)):
            if event.type() == QEvent.Type.MouseMove:
                pos = event.pos()
                opt = QStyleOptionSpinBox()
                obj.initStyleOption(opt)
                
                # Проверка попадания в кнопки
                up_rect = obj.style().subControlRect(QStyle.ComplexControl.CC_SpinBox, opt, QStyle.SubControl.SC_SpinBoxUp)
                down_rect = obj.style().subControlRect(QStyle.ComplexControl.CC_SpinBox, opt, QStyle.SubControl.SC_SpinBoxDown)

                if up_rect.contains(pos) or down_rect.contains(pos):
                    obj.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    obj.unsetCursor()
            elif event.type() == QEvent.Type.Leave:
                obj.unsetCursor()
        
        elif isinstance(obj, QSlider):
            if event.type() == QEvent.Type.MouseMove:
                pos = event.pos()
                opt = QStyleOptionSlider()
                obj.initStyleOption(opt)

                # Проверка попадания в ползунок
                handle_rect = obj.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle)

                if handle_rect.contains(pos):
                    obj.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    obj.unsetCursor()
            elif event.type() == QEvent.Type.Leave:
                obj.unsetCursor()

        # Вызов стандартного обработчика
        return super().eventFilter(obj, event)
    
    def set_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
    
    def update_step_sizes(self, step_size=1):
        """
        Обновление шага изменения для спинбоксов.
        
        Args:
            step_size: Размер шага
        """
        # Должен быть переопределен в дочерних классах
        pass
    
    def update_ranges(self, min_x=-10000, max_x=10000, min_y=-10000, max_y=10000):
        """
        Обновление диапазонов значений для спинбоксов и слайдеров.
        
        Args:
            min_x: Минимальное значение X
            max_x: Максимальное значение X
            min_y: Минимальное значение Y
            max_y: Максимальное значение Y
        """
        # Должен быть переопределен в дочерних классах
        pass
    
    def set_properties(self, **kwargs):
        """
        Установка свойств элемента.
        
        Args:
            **kwargs: Словарь свойств элемента
        """
        # Должен быть переопределен в дочерних классах
        pass
    
    def reset_properties(self):
        """
        Сброс свойств элемента к начальным значениям.
        """
        # Должен быть переопределен в дочерних классах
        pass
    
    def create_coordinate_control(self, name, min_value, max_value, callback):
        """Создает стандартный контрол для координаты"""
        layout = QHBoxLayout()
        
        # Создаем спинбокс
        spinbox = QSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setMinimumWidth(70)
        
        # Создаем слайдер
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.valueChanged.connect(callback)
        
        # Соединяем спинбокс и слайдер
        spinbox.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(spinbox.setValue)
        
        # Добавляем метку
        label = QLabel(f"{name}:")
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        layout.addWidget(slider)
        
        return layout, spinbox, slider
    
    def handle_value_change(self, value, widget, slider, signal_emit, snap_to_grid=True):
        """Общий обработчик изменения значений"""
        if not self.field_widget:
            return
            
        try:
            # Проверяем привязку к сетке
            if snap_to_grid and self.field_widget.scene():
                field_widget = self.field_widget.scene().parent()
                if hasattr(field_widget, 'snap_to_grid_enabled') and field_widget.snap_to_grid_enabled:
                    value = round(value / field_widget.grid_size) * field_widget.grid_size
            
            # Обновляем значение только если оно изменилось
            if value != widget.value():
                widget.blockSignals(True)
                widget.setValue(value)
                widget.blockSignals(False)
                
                # Обновляем слайдер
                slider.setValue(value)
                
                # Отправляем сигнал
                signal_emit(value)
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении значения: {e}")
    
    def show_properties(self, *args, **kwargs):
        """Базовый метод показа свойств"""
        raise NotImplementedError("Метод должен быть реализован в дочернем классе")
    
    def hide(self):
        """Скрывает виджет"""
        super().hide()
        