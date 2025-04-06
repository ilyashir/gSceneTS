"""
Виджет свойств региона.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QFormLayout, QSlider, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import logging
from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import snap_to_grid, is_snap_enabled
from utils.signal_utils import SignalBlock
from custom_widgets import EditableLineEdit, ColorPickerButton, CustomSpinBox

logger = logging.getLogger(__name__)

class RegionPropertiesWidget(BasePropertiesWidget):
    """
    Виджет для отображения и редактирования свойств региона.
    """
    # Сигналы
    position_changed = pyqtSignal(int, int)  # x, y
    size_changed = pyqtSignal(int, int)  # width, height
    color_changed = pyqtSignal(str)  # color
    id_changed = pyqtSignal(str)  # id
    
    def __init__(self, parent=None, is_dark_theme=False):
        """
        Инициализация виджета свойств региона.
        
        Args:
            parent: Родительский виджет
            is_dark_theme: Флаг темной темы
        """
        super().__init__("Свойства региона", parent)
        self.apply_theme(is_dark_theme)
        self.field_widget = None
        self.initial_values = {}
        self._initialize_ui()
        self._connect_signals()
        self.setup_cursors()
        
    def _initialize_ui(self):
        """Инициализация интерфейса виджета."""
        layout = QVBoxLayout()
        
        # ID региона (редактируемый)
        id_layout = QHBoxLayout()
        id_label = QLabel("ID:")
        self.apply_field_style(id_label)
        id_layout.addWidget(id_label)
        self.id_edit = EditableLineEdit()
        self.apply_field_style(self.id_edit)
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)
        
        # Используем FormLayout для организации полей
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Позиция
        position_label = QLabel("<b>Позиция</b>")
        self.apply_field_style(position_label)
        form_layout.addRow(position_label)
        
        # X с ползунком
        x_layout = QHBoxLayout()
        self.x_spinbox = CustomSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setMinimumWidth(70)
        
        # Ползунок X
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-10000, 10000)
        
        x_layout.addWidget(self.x_spinbox)
        x_layout.addWidget(self.x_slider)
        
        x_label = QLabel("X:")
        self.apply_field_style(x_label)
        form_layout.addRow(x_label, x_layout)
        
        # Y с ползунком
        y_layout = QHBoxLayout()
        self.y_spinbox = CustomSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setMinimumWidth(70)
        
        # Ползунок Y
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-10000, 10000)
        
        y_layout.addWidget(self.y_spinbox)
        y_layout.addWidget(self.y_slider)
        
        y_label = QLabel("Y:")
        self.apply_field_style(y_label)
        form_layout.addRow(y_label, y_layout)
        
        # Размер
        size_label = QLabel("<b>Размер</b>")
        self.apply_field_style(size_label)
        form_layout.addRow(size_label)
        
        # Ширина с ползунком
        width_layout = QHBoxLayout()
        self.width_spinbox = CustomSpinBox()
        self.width_spinbox.setRange(1, 1000)
        self.width_spinbox.setMinimumWidth(70)
        
        # Ползунок ширины
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 1000)
        
        width_layout.addWidget(self.width_spinbox)
        width_layout.addWidget(self.width_slider)
        
        width_label = QLabel("Ширина:")
        self.apply_field_style(width_label)
        form_layout.addRow(width_label, width_layout)
        
        # Высота с ползунком
        height_layout = QHBoxLayout()
        self.height_spinbox = CustomSpinBox()
        self.height_spinbox.setRange(1, 1000)
        self.height_spinbox.setMinimumWidth(70)
        
        # Ползунок высоты
        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setRange(1, 1000)
        
        height_layout.addWidget(self.height_spinbox)
        height_layout.addWidget(self.height_slider)
        
        height_label = QLabel("Высота:")
        self.apply_field_style(height_label)
        form_layout.addRow(height_label, height_layout)
        
        # Цвет
        color_layout = QHBoxLayout()
        color_label = QLabel("Цвет:")
        self.apply_field_style(color_label)
        color_layout.addWidget(color_label)
        self.color_button = ColorPickerButton(is_dark_theme=self.is_dark_theme)
        color_layout.addWidget(self.color_button)
        form_layout.addRow(color_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        if self.field_widget:
            self.update_ranges(
                int(self.field_widget.scene().sceneRect().left()),
                int(self.field_widget.scene().sceneRect().right()),
                int(self.field_widget.scene().sceneRect().top()),
                int(self.field_widget.scene().sceneRect().bottom())
            )

        self.properties_layout.addLayout(layout)
        
        # Сохраняем ссылки на метки для дальнейшего обновления тем
        self.id_label = id_label
        self.position_label = position_label
        self.x_label = x_label
        self.y_label = y_label
        self.size_label = size_label
        self.width_label = width_label
        self.height_label = height_label
        self.color_label = color_label
        
    def _connect_signals(self):
        """Подключение сигналов и слотов."""
        # Связываем слайдеры и спинбоксы для позиции
        self.x_spinbox.buttonValueChanged.connect(self.x_slider.setValue)
        self.x_spinbox.buttonValueChanged.connect(self.on_x_spinbox_value_changed)
        self.x_slider.valueChanged.connect(self.on_x_slider_changed)
        
        self.y_spinbox.buttonValueChanged.connect(self.y_slider.setValue)
        self.y_spinbox.buttonValueChanged.connect(self.on_y_spinbox_value_changed)
        self.y_slider.valueChanged.connect(self.on_y_slider_changed)
        
        # Связываем слайдеры и спинбоксы для размера
        self.width_spinbox.buttonValueChanged.connect(self.width_slider.setValue)
        self.width_spinbox.buttonValueChanged.connect(self.on_width_spinbox_value_changed)
        self.width_slider.valueChanged.connect(self.on_width_slider_changed)
        
        self.height_spinbox.buttonValueChanged.connect(self.height_slider.setValue)
        self.height_spinbox.buttonValueChanged.connect(self.on_height_spinbox_value_changed)
        self.height_slider.valueChanged.connect(self.on_height_slider_changed)
        
        # Подключаем сигналы редактирования
        self.x_spinbox.editingFinished.connect(self.on_x_editing_finished)
        self.y_spinbox.editingFinished.connect(self.on_y_editing_finished)
        self.width_spinbox.editingFinished.connect(self.on_width_editing_finished)
        self.height_spinbox.editingFinished.connect(self.on_height_editing_finished)
        
        # Подключаем изменение цвета
        self.color_button.colorChanged.connect(self.on_color_changed)
        
        # Подключаем изменение ID
        self.id_edit.valueChanged.connect(self.on_id_changed)
        
        # Подключаем кнопку сброса
        self.reset_button.clicked.connect(self.reset_properties)
        
    def set_properties(self, x, y, width, height, color, region_id=None):
        """
        Установка свойств региона.
        
        Args:
            x: X-координата
            y: Y-координата
            width: Ширина
            height: Высота
            color: Цвет (hex-строка)
            region_id: ID региона (опционально)
        """
        try:
            # Запоминаем начальные значения для возможности сброса
            self.initial_values = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'color': color,
                'id': region_id or ''
            }
            
            # Блокируем сигналы на время обновления
            with SignalBlock(self.x_spinbox), SignalBlock(self.x_slider), \
                 SignalBlock(self.y_spinbox), SignalBlock(self.y_slider), \
                 SignalBlock(self.width_spinbox), SignalBlock(self.width_slider), \
                 SignalBlock(self.height_spinbox), SignalBlock(self.height_slider), \
                 SignalBlock(self.color_button), SignalBlock(self.id_edit):
                
                self.x_spinbox.setValue(x)
                self.x_slider.setValue(x)
                
                self.y_spinbox.setValue(y)
                self.y_slider.setValue(y)
                
                self.width_spinbox.setValue(width)
                self.width_slider.setValue(width)
                
                self.height_spinbox.setValue(height)
                self.height_slider.setValue(height)
                
                # Устанавливаем цвет
                if isinstance(color, str):
                    self.color_button.setColor(QColor(color))
                else:
                    self.color_button.setColor(color)
                
                # Обновляем ID если он предоставлен
                if region_id:
                    self.id_edit.setValue(region_id)
        except Exception as e:
            logger.error(f"Ошибка при установке свойств региона: {e}")
            
    def update_ranges(self, min_x=-10000, max_x=10000, min_y=-10000, max_y=10000):
        """
        Обновление диапазонов значений для спинбоксов и слайдеров.
        
        Args:
            min_x: Минимальное значение X
            max_x: Максимальное значение X
            min_y: Минимальное значение Y
            max_y: Максимальное значение Y
        """
        try:
            logger.debug(f"Обновление диапазонов: min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}")
            # Получаем текущие размеры региона
            current_width = self.width_spinbox.value()
            current_height = self.height_spinbox.value()
            logger.debug(f"Текущие размеры региона: current_width={current_width}, current_height={current_height}")
            # Обновляем диапазоны для позиции
            self.x_spinbox.setRange(min_x, max_x-current_width)
            self.x_slider.setRange(min_x, max_x-current_width)
            self.y_spinbox.setRange(min_y, max_y-current_height)
            self.y_slider.setRange(min_y, max_y-current_height)
            
            # Обновляем диапазоны для размера
            # Максимальная ширина/высота зависит от текущей позиции
            current_x = self.x_spinbox.value()
            current_y = self.y_spinbox.value()
            max_width = max_x - current_x
            max_height = max_y - current_y
            self.width_spinbox.setRange(1, max_width)
            self.width_slider.setRange(1, max_width)
            self.height_spinbox.setRange(1, max_height)
            self.height_slider.setRange(1, max_height)
        except Exception as e:
            logger.error(f"Ошибка при обновлении диапазонов: {e}")
            
    def reset_properties(self):
        """Сброс свойств региона к начальным значениям."""
        if not self.initial_values:
            return
            
        try:
            # Устанавливаем начальные значения
            self.set_properties(
                self.initial_values.get('x', 0),
                self.initial_values.get('y', 0),
                self.initial_values.get('width', 100),
                self.initial_values.get('height', 100),
                self.initial_values.get('color', '#00FF00'),
                self.initial_values.get('id', '')
            )
            
            # Оповещаем об изменениях
            self.position_changed.emit(
                self.initial_values.get('x', 0),
                self.initial_values.get('y', 0)
            )
            self.size_changed.emit(
                self.initial_values.get('width', 100),
                self.initial_values.get('height', 100)
            )
            self.color_changed.emit(self.initial_values.get('color', '#00FF00'))
            if self.initial_values.get('id'):
                self.id_changed.emit(self.initial_values.get('id', ''))
        except Exception as e:
            logger.error(f"Ошибка при сбросе свойств региона: {e}")
            
    def update_step_sizes(self, step_size=1):
        """
        Обновление шага изменения для спинбоксов.
        
        Args:
            step_size: Размер шага
        """
        try:
            self.x_spinbox.setSingleStep(step_size)
            self.y_spinbox.setSingleStep(step_size)
            self.width_spinbox.setSingleStep(step_size)
            self.height_spinbox.setSingleStep(step_size)
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага спинбоксов: {e}")
    
    # Обработчики событий для слайдеров
    def on_x_slider_changed(self, value):
        """
        Обработчик изменения слайдера X.
        
        Args:
            value: Новое значение X
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.x_spinbox):
                self.x_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты: {e}")
            
    def on_y_slider_changed(self, value):
        """
        Обработчик изменения слайдера Y.
        
        Args:
            value: Новое значение Y
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.y_spinbox):
                self.y_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты: {e}")
            
    def on_width_slider_changed(self, value):
        """
        Обработчик изменения слайдера ширины.
        
        Args:
            value: Новое значение ширины
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.width_spinbox):
                self.width_spinbox.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(value, self.height_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении ширины: {e}")
            
    def on_height_slider_changed(self, value):
        """
        Обработчик изменения слайдера высоты.
        
        Args:
            value: Новое значение высоты
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.height_spinbox):
                self.height_spinbox.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении высоты: {e}")
            
    # Новые обработчики для спинбоксов
    def on_x_spinbox_value_changed(self, value):
        """Обработчик изменения значения X в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.x_spinbox):
                    self.x_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты через спинбокс: {e}")

    def on_y_spinbox_value_changed(self, value):
        """Обработчик изменения значения Y в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.y_spinbox):
                    self.y_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты через спинбокс: {e}")

    def on_width_spinbox_value_changed(self, value):
        """Обработчик изменения значения ширины в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.width_spinbox):
                    self.width_spinbox.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(value, self.height_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении ширины через спинбокс: {e}")

    def on_height_spinbox_value_changed(self, value):
        """Обработчик изменения значения высоты в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.height_spinbox):
                    self.height_spinbox.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении высоты через спинбокс: {e}")
            
    def on_color_changed(self, color):
        """
        Обработчик изменения цвета.
        
        Args:
            color: Новый цвет
        """
        try:
            # Преобразуем цвет в hex-строку
            if isinstance(color, QColor):
                color_str = color.name()
            else:
                color_str = color
                
            # Оповещаем об изменении цвета
            self.color_changed.emit(color_str)
        except Exception as e:
            logger.error(f"Ошибка при изменении цвета: {e}")
            
    def on_id_changed(self, new_id, item=None):
        """
        Обработчик изменения ID региона.
        
        Args:
            new_id: Новый ID
            item: Элемент региона (опционально)
        """
        try:
            self.id_changed.emit(new_id)
        except Exception as e:
            logger.error(f"Ошибка при изменении ID региона: {e}")
            
    def set_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
        self.update_step_sizes() 

    def set_theme(self, is_dark_theme):
        """
        Установка темы оформления.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.apply_theme(is_dark_theme)
        
        # Обновляем стиль для EditableLineEdit с ID региона
        self.apply_field_style(self.id_edit)
        
        # Обновляем тему для кнопки выбора цвета
        self.color_button.set_theme(is_dark_theme)
        
        # Обновляем тему для всех статических QLabel
        self.apply_field_style(self.id_label)
        self.apply_field_style(self.position_label)
        self.apply_field_style(self.x_label)
        self.apply_field_style(self.y_label)
        self.apply_field_style(self.size_label)
        self.apply_field_style(self.width_label)
        self.apply_field_style(self.height_label)
        self.apply_field_style(self.color_label)
    
    def update_properties(self, region):
        """
        Обновление свойств виджета на основе объекта региона.
        
        Args:
            region: Объект региона
        """
        logger.debug(f"Обновление свойств региона: {region}")
        if self.field_widget:
            self.update_ranges(
                int(self.field_widget.scene().sceneRect().left()),
                int(self.field_widget.scene().sceneRect().right()),
                int(self.field_widget.scene().sceneRect().top()),
                int(self.field_widget.scene().sceneRect().bottom())
            )
            logger.debug(f"Обновлены диапазоны: min_x={self.x_spinbox.minimum()}, max_x={self.x_spinbox.maximum()}, min_y={self.y_spinbox.minimum()}, max_y={self.y_spinbox.maximum()}")

        self.set_properties(
            int(region.pos().x()), 
            int(region.pos().y()),
            int(region.rect().width()), 
            int(region.rect().height()),
            region.brush().color(),
            region.region_id
        )
        logger.debug(f"Установлены свойства региона: {region.pos().x()}, {region.pos().y()}, {region.rect().width()}, {region.rect().height()}, {region.brush().color()}, {region.region_id}")
    
    def connect_to_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
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

    # Обработчики завершения редактирования
    def on_x_editing_finished(self):
        """Обработчик завершения редактирования X-координаты."""
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
        
            # Пересчитываем доступные диапазоны размеров
            if self.field_widget:
                scene_rect = self.field_widget.scene().sceneRect()
                min_x = int(scene_rect.left())
                max_x = int(scene_rect.right())
                min_y = int(scene_rect.top())
                max_y = int(scene_rect.bottom())
                self.update_ranges(min_x, max_x, min_y, max_y)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X: {e}")

    def on_y_editing_finished(self):
        """Обработчик завершения редактирования Y-координаты."""
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

            if self.field_widget:
                scene_rect = self.field_widget.scene().sceneRect()
                min_x = int(scene_rect.left())
                max_x = int(scene_rect.right())
                min_y = int(scene_rect.top())
                max_y = int(scene_rect.bottom())
                self.update_ranges(min_x, max_x, min_y, max_y)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y: {e}")

    def on_width_editing_finished(self):
        """Обработчик завершения редактирования ширины."""
        try:
            value = self.width_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.width_spinbox.value():
                    with SignalBlock(self.width_spinbox):
                        self.width_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.width_slider):
                self.width_slider.setValue(value)
            
            if self.field_widget:
                scene_rect = self.field_widget.scene().sceneRect()
                min_x = int(scene_rect.left())
                max_x = int(scene_rect.right())
                min_y = int(scene_rect.top())
                max_y = int(scene_rect.bottom())
                self.update_ranges(min_x, max_x, min_y, max_y)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(value, self.height_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования ширины: {e}")

    def on_height_editing_finished(self):
        """Обработчик завершения редактирования высоты."""
        try:
            value = self.height_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.height_spinbox.value():
                    with SignalBlock(self.height_spinbox):
                        self.height_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.height_slider):
                self.height_slider.setValue(value)

            if self.field_widget:
                scene_rect = self.field_widget.scene().sceneRect()
                min_x = int(scene_rect.left())
                max_x = int(scene_rect.right())
                min_y = int(scene_rect.top())
                max_y = int(scene_rect.bottom())
                self.update_ranges(min_x, max_x, min_y, max_y)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования высоты: {e}") 