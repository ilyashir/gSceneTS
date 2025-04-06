from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, 
    QSlider, QCheckBox, QGroupBox, QSpinBox, QColorDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIntValidator

from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import is_snap_enabled, snap_to_grid, get_grid_size
from utils.signal_utils import SignalBlock

import logging

logger = logging.getLogger(__name__)

class StartPositionPropertiesWidget(BasePropertiesWidget):
    """
    Класс для отображения и редактирования свойств стартовой позиции.
    Наследуется от BasePropertiesWidget.
    """
    
    # Сигналы
    position_changed = pyqtSignal(float, float)  # x, y
    direction_changed = pyqtSignal(float)  # direction
    
    def __init__(self, parent=None, is_dark_theme=False):
        """
        Инициализация виджета свойств стартовой позиции.
        
        Args:
            parent: Родительский виджет
            is_dark_theme: Флаг темной темы
        """
        super().__init__("Стартовая позиция", parent)
        
        # Применяем тему
        self.apply_theme(is_dark_theme)
        
        # Создаем все элементы интерфейса
        self.create_widgets()
        self.create_layouts()
        self.setup_connections()
        
        # По умолчанию виджет скрыт
        self.hide()
    
    def create_widgets(self):
        """Создает виджеты для отображения свойств стартовой позиции."""
        # Идентификатор
        self.id_label = QLabel("ID:")
        self.id_value = QLineEdit("startPosition")
        self.id_value.setReadOnly(True)  # ID всегда фиксирован
        
        # Координаты X
        self.x_label = QLabel("X:")
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setValue(25)  # Значение по умолчанию
        self.x_spinbox.setSingleStep(1)
        
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-1000, 1000)
        self.x_slider.setValue(25)  # Значение по умолчанию
        
        # Координаты Y
        self.y_label = QLabel("Y:")
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setValue(25)  # Значение по умолчанию
        self.y_spinbox.setSingleStep(1)
        
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-1000, 1000)
        self.y_slider.setValue(25)  # Значение по умолчанию
        
        # Направление
        self.direction_label = QLabel("Направление:")
        self.direction_spinbox = QSpinBox()
        self.direction_spinbox.setRange(0, 359)
        self.direction_spinbox.setValue(0)  # Значение по умолчанию
        self.direction_spinbox.setSingleStep(5)
        
        self.direction_slider = QSlider(Qt.Orientation.Horizontal)
        self.direction_slider.setRange(0, 359)
        self.direction_slider.setValue(0)  # Значение по умолчанию
    
    def create_layouts(self):
        """Создает компоновку виджетов."""
        # Основной лейаут
        main_layout = QVBoxLayout()
        
        # ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_label)
        id_layout.addWidget(self.id_value)
        main_layout.addLayout(id_layout)
        
        # Координаты X
        x_layout = QHBoxLayout()
        x_layout.addWidget(self.x_label)
        x_layout.addWidget(self.x_spinbox)
        main_layout.addLayout(x_layout)
        main_layout.addWidget(self.x_slider)
        
        # Координаты Y
        y_layout = QHBoxLayout()
        y_layout.addWidget(self.y_label)
        y_layout.addWidget(self.y_spinbox)
        main_layout.addLayout(y_layout)
        main_layout.addWidget(self.y_slider)
        
        # Направление
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(self.direction_label)
        direction_layout.addWidget(self.direction_spinbox)
        main_layout.addLayout(direction_layout)
        main_layout.addWidget(self.direction_slider)
        
        # Очищаем текущий лейаут, если он есть
        # и добавляем все виджеты в новый лейаут
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Добавляем все элементы из main_layout в properties_layout
        for i in range(main_layout.count()):
            item = main_layout.takeAt(0)
            if item.widget():
                self.properties_layout.addWidget(item.widget())
            elif item.layout():
                self.properties_layout.addLayout(item.layout())
    
    def setup_connections(self):
        """Устанавливает соединения для сигналов и слотов."""
        # X координата
        self.x_spinbox.editingFinished.connect(self.on_x_editing_finished)
        self.x_slider.valueChanged.connect(self.on_x_slider_value_changed)
        
        # Y координата
        self.y_spinbox.editingFinished.connect(self.on_y_editing_finished)
        self.y_slider.valueChanged.connect(self.on_y_slider_value_changed)
        
        # Направление
        self.direction_spinbox.editingFinished.connect(self.on_direction_editing_finished)
        self.direction_slider.valueChanged.connect(self.on_direction_slider_value_changed)
    
    def update_ranges(self, min_x, max_x, min_y, max_y):
        """
        Обновляет допустимые диапазоны значений для элементов.
        
        Args:
            min_x: Минимальное значение X
            max_x: Максимальное значение X
            min_y: Минимальное значение Y
            max_y: Максимальное значение Y
        """
        # Обновляем диапазоны спинбоксов
        self.x_spinbox.setRange(min_x, max_x)
        self.y_spinbox.setRange(min_y, max_y)
        
        # Обновляем диапазоны слайдеров
        self.x_slider.setRange(min_x, max_x)
        self.y_slider.setRange(min_y, max_y)
    
    def update_step_sizes(self, step_size):
        """
        Обновляет шаг изменения значений для элементов.
        
        Args:
            step_size: Размер шага
        """
        # Обновляем шаг для спинбоксов
        self.x_spinbox.setSingleStep(step_size)
        self.y_spinbox.setSingleStep(step_size)
        self.direction_spinbox.setSingleStep(step_size if step_size < 15 else 15)
    
    def set_properties(self, x, y, direction):
        """
        Устанавливает свойства стартовой позиции.
        
        Args:
            x: Координата X
            y: Координата Y
            direction: Направление в градусах
        """
        # Блокируем сигналы, чтобы избежать рекурсивных вызовов
        with SignalBlock(self.x_spinbox, self.x_slider, 
                        self.y_spinbox, self.y_slider,
                        self.direction_spinbox, self.direction_slider):
            # Устанавливаем значения для спинбоксов и слайдеров
            self.x_spinbox.setValue(x)
            self.x_slider.setValue(x)
            self.y_spinbox.setValue(y)
            self.y_slider.setValue(y)
            self.direction_spinbox.setValue(direction)
            self.direction_slider.setValue(direction)
    
    def show_properties(self, start_position):
        """
        Отображает свойства стартовой позиции.
        
        Args:
            start_position: Объект стартовой позиции
        """
        if not start_position:
            logger.warning("Отсутствует объект стартовой позиции для отображения свойств")
            self.hide()
            return
            
        logger.debug(f"Показываем свойства стартовой позиции: {start_position}")
        
        # Обновляем диапазоны значений, если у нас есть ссылка на поле
        if self.field_widget:
            scene_rect = self.field_widget.scene().sceneRect()
            min_x = int(scene_rect.left())
            max_x = int(scene_rect.right())
            min_y = int(scene_rect.top())
            max_y = int(scene_rect.bottom())
            self.update_ranges(min_x, max_x, min_y, max_y)
        
        # Устанавливаем значения свойств
        self.set_properties(
            int(start_position.x()),
            int(start_position.y()),
            int(start_position.direction())
        )
        
        # Отображаем виджет
        self.show()
    
    def update_properties(self, start_position):
        """
        Обновляет отображаемые свойства стартовой позиции.
        
        Args:
            start_position: Объект стартовой позиции
        """
        self.show_properties(start_position)
    
    def connect_to_field_widget(self, field_widget):
        """
        Устанавливает ссылку на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
        self.update_step_sizes(field_widget.grid_size if hasattr(field_widget, 'grid_size') else 1)
    
    def on_grid_snap_changed(self, enabled):
        """
        Обработчик изменения привязки к сетке.
        
        Args:
            enabled: Статус привязки
        """
        if self.field_widget:
            step_size = self.field_widget.grid_size if enabled else 1
            self.update_step_sizes(step_size)
    
    # Обработчики изменения значений X
    def on_x_editing_finished(self):
        """Обработчик завершения редактирования координаты X."""
        try:
            value = self.x_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.x_spinbox.value():
                    with SignalBlock(self.x_spinbox):
                        self.x_spinbox.setValue(value)
            
            # Обновляем слайдер
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)
            
            # Обновляем координаты стартовой позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при редактировании X: {e}")
    
    def on_x_slider_value_changed(self, value):
        """
        Обработчик изменения значения слайдера X.
        
        Args:
            value: Новое значение
        """
        # Обрабатываем изменение значения в общем методе
        self.handle_value_change(
            value, 
            self.x_spinbox, 
            self.x_slider, 
            lambda v: self.position_changed.emit(v, self.y_spinbox.value())
        )
    
    # Обработчики изменения значений Y
    def on_y_editing_finished(self):
        """Обработчик завершения редактирования координаты Y."""
        try:
            value = self.y_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.y_spinbox.value():
                    with SignalBlock(self.y_spinbox):
                        self.y_spinbox.setValue(value)
            
            # Обновляем слайдер
            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)
            
            # Обновляем координаты стартовой позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при редактировании Y: {e}")
    
    def on_y_slider_value_changed(self, value):
        """
        Обработчик изменения значения слайдера Y.
        
        Args:
            value: Новое значение
        """
        # Обрабатываем изменение значения в общем методе
        self.handle_value_change(
            value, 
            self.y_spinbox, 
            self.y_slider, 
            lambda v: self.position_changed.emit(self.x_spinbox.value(), v)
        )
    
    # Обработчики изменения значения направления
    def on_direction_editing_finished(self):
        """Обработчик завершения редактирования направления."""
        try:
            value = self.direction_spinbox.value()
            
            # Обновляем слайдер
            with SignalBlock(self.direction_slider):
                self.direction_slider.setValue(value)
            
            # Обновляем направление стартовой позиции
            self.direction_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при редактировании направления: {e}")
    
    def on_direction_slider_value_changed(self, value):
        """
        Обработчик изменения значения слайдера направления.
        
        Args:
            value: Новое значение
        """
        # Обрабатываем изменение значения в общем методе
        self.handle_value_change(
            value, 
            self.direction_spinbox, 
            self.direction_slider, 
            self.direction_changed.emit,
            snap_to_grid=False  # Для направления не используем привязку к сетке
        )
    
    def set_theme(self, is_dark_theme):
        """
        Применяет тему оформления к виджету.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.apply_theme(is_dark_theme) 