"""
Виджет свойств стены.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QFormLayout, QSlider, QPushButton,
    QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
import logging
from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import snap_to_grid, is_snap_enabled
from utils.signal_utils import SignalBlock
from custom_widgets import EditableLineEdit, CustomSpinBox

logger = logging.getLogger(__name__)

class WallPropertiesWidget(BasePropertiesWidget):
    """
    Виджет для отображения и редактирования свойств стены.
    """
    # Сигналы
    position_point1_changed = pyqtSignal(int, int)  # x1, y1
    position_point2_changed = pyqtSignal(int, int)  # x2, y2
    width_changed = pyqtSignal(int)  # width
    id_changed = pyqtSignal(str)  # id
    
    def __init__(self, parent=None, is_dark_theme=False):
        """
        Инициализация виджета свойств стены.
        
        Args:
            parent: Родительский виджет
            is_dark_theme: Флаг темной темы
        """
        super().__init__("Свойства стены", parent)
        self.apply_theme(is_dark_theme)
        self.field_widget = None
        self.initial_values = {}
        self._initialize_ui()
        self._connect_signals()
        self.setup_cursors()
        
    def _initialize_ui(self):
        """Инициализация интерфейса виджета."""
        layout = QVBoxLayout()
        
        # ID стены (редактируемый)
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
        
        # Координаты
        coords_label = QLabel("<b>Координаты</b>")
        self.apply_field_style(coords_label)
        form_layout.addRow(coords_label)
        
        # X1 с ползунком
        x1_layout = QHBoxLayout()
        self.x1_spinbox = CustomSpinBox()
        self.x1_spinbox.setRange(-10000, 10000)
        self.x1_spinbox.setMinimumWidth(70)
        
        # Ползунок X1
        self.x1_slider = QSlider(Qt.Orientation.Horizontal)
        self.x1_slider.setRange(-10000, 10000)
        
        x1_layout.addWidget(self.x1_spinbox)
        x1_layout.addWidget(self.x1_slider)
        
        x1_label = QLabel("X1:")
        self.apply_field_style(x1_label)
        form_layout.addRow(x1_label, x1_layout)
        
        # Y1 с ползунком
        y1_layout = QHBoxLayout()
        self.y1_spinbox = CustomSpinBox()
        self.y1_spinbox.setRange(-10000, 10000)
        self.y1_spinbox.setMinimumWidth(70)
        
        # Ползунок Y1
        self.y1_slider = QSlider(Qt.Orientation.Horizontal)
        self.y1_slider.setRange(-10000, 10000)
        
        y1_layout.addWidget(self.y1_spinbox)
        y1_layout.addWidget(self.y1_slider)
        
        y1_label = QLabel("Y1:")
        self.apply_field_style(y1_label)
        form_layout.addRow(y1_label, y1_layout)
        
        # X2 с ползунком
        x2_layout = QHBoxLayout()
        self.x2_spinbox = CustomSpinBox()
        self.x2_spinbox.setRange(-10000, 10000)
        self.x2_spinbox.setMinimumWidth(70)
        
        # Ползунок X2
        self.x2_slider = QSlider(Qt.Orientation.Horizontal)
        self.x2_slider.setRange(-10000, 10000)
        
        x2_layout.addWidget(self.x2_spinbox)
        x2_layout.addWidget(self.x2_slider)
        
        x2_label = QLabel("X2:")
        self.apply_field_style(x2_label)
        form_layout.addRow(x2_label, x2_layout)
        
        # Y2 с ползунком
        y2_layout = QHBoxLayout()
        self.y2_spinbox = CustomSpinBox()
        self.y2_spinbox.setRange(-10000, 10000)
        self.y2_spinbox.setMinimumWidth(70)
        
        # Ползунок Y2
        self.y2_slider = QSlider(Qt.Orientation.Horizontal)
        self.y2_slider.setRange(-10000, 10000)
        
        y2_layout.addWidget(self.y2_spinbox)
        y2_layout.addWidget(self.y2_slider)
        
        y2_label = QLabel("Y2:")
        self.apply_field_style(y2_label)
        form_layout.addRow(y2_label, y2_layout)
        
        # Ширина стены
        width_layout = QHBoxLayout()
        self.wall_width_spinbox = CustomSpinBox()
        self.wall_width_spinbox.setRange(1, 50)
        self.wall_width_spinbox.setMinimumWidth(70)
        
        # Ползунок ширины
        self.wall_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_width_slider.setRange(1, 50)
        
        width_layout.addWidget(self.wall_width_spinbox)
        width_layout.addWidget(self.wall_width_slider)
        
        width_label = QLabel("Ширина:")
        self.apply_field_style(width_label)
        form_layout.addRow(width_label, width_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.properties_layout.addLayout(layout)
        
        # Сохраняем ссылки на метки для дальнейшего обновления тем
        self.id_label = id_label
        self.coords_label = coords_label
        self.x1_label = x1_label
        self.y1_label = y1_label
        self.x2_label = x2_label
        self.y2_label = y2_label
        self.width_label = width_label
        
    def _connect_signals(self):
        """Подключение сигналов и слотов."""
        # Связываем слайдеры и спинбоксы для координат
        self.x1_spinbox.buttonValueChanged.connect(self.x1_slider.setValue)
        self.x1_spinbox.buttonValueChanged.connect(self.on_x1_changed)
        self.x1_slider.valueChanged.connect(self.on_x1_slider_changed)
        
        self.y1_spinbox.buttonValueChanged.connect(self.y1_slider.setValue)
        self.y1_spinbox.buttonValueChanged.connect(self.on_y1_changed)
        self.y1_slider.valueChanged.connect(self.on_y1_slider_changed)
        
        self.x2_spinbox.buttonValueChanged.connect(self.x2_slider.setValue)
        self.x2_spinbox.buttonValueChanged.connect(self.on_x2_changed)
        self.x2_slider.valueChanged.connect(self.on_x2_slider_changed)
        
        self.y2_spinbox.buttonValueChanged.connect(self.y2_slider.setValue)
        self.y2_spinbox.buttonValueChanged.connect(self.on_y2_changed)
        self.y2_slider.valueChanged.connect(self.on_y2_slider_changed)
        
        # Связываем слайдер и спинбокс для ширины
        self.wall_width_spinbox.buttonValueChanged.connect(self.wall_width_slider.setValue)
        self.wall_width_spinbox.buttonValueChanged.connect(self.on_width_changed)
        self.wall_width_slider.valueChanged.connect(self.on_width_slider_changed)
        
        # Подключаем сигналы редактирования
        self.x1_spinbox.editingFinished.connect(self.on_x1_editing_finished)
        self.y1_spinbox.editingFinished.connect(self.on_y1_editing_finished)
        self.x2_spinbox.editingFinished.connect(self.on_x2_editing_finished)
        self.y2_spinbox.editingFinished.connect(self.on_y2_editing_finished)
        self.wall_width_spinbox.editingFinished.connect(self.on_width_editing_finished)
        
        # Редактирование ID
        self.id_edit.valueChanged.connect(self.on_id_changed)
        
        # Кнопка сброса
        self.reset_button.clicked.connect(self.reset_properties)
        
    def set_properties(self, x1, y1, x2, y2, width, wall_id=None):
        """
        Установка свойств стены.
        
        Args:
            x1: X-координата первой точки
            y1: Y-координата первой точки
            x2: X-координата второй точки
            y2: Y-координата второй точки
            width: Ширина стены
            wall_id: ID стены (опционально)
        """
        try:
            # Запоминаем начальные значения для возможности сброса
            self.initial_values = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'width': width,
                'id': wall_id or ''
            }
            
            # Блокируем сигналы на время обновления
            with SignalBlock(self.x1_spinbox), SignalBlock(self.x1_slider), \
                 SignalBlock(self.y1_spinbox), SignalBlock(self.y1_slider), \
                 SignalBlock(self.x2_spinbox), SignalBlock(self.x2_slider), \
                 SignalBlock(self.y2_spinbox), SignalBlock(self.y2_slider), \
                 SignalBlock(self.wall_width_spinbox), SignalBlock(self.wall_width_slider), \
                 SignalBlock(self.id_edit):
                
                self.x1_spinbox.setValue(x1)
                self.x1_slider.setValue(x1)
                
                self.y1_spinbox.setValue(y1)
                self.y1_slider.setValue(y1)
                
                self.x2_spinbox.setValue(x2)
                self.x2_slider.setValue(x2)
                
                self.y2_spinbox.setValue(y2)
                self.y2_slider.setValue(y2)
                
                self.wall_width_spinbox.setValue(width)
                self.wall_width_slider.setValue(width)
                
                # Обновляем ID если он предоставлен
                if wall_id:
                    self.id_edit.setValue(wall_id)
        except Exception as e:
            logger.error(f"Ошибка при установке свойств стены: {e}")
            
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
            # Обновляем диапазоны для X1, Y1
            self.x1_spinbox.setRange(min_x, max_x)
            self.x1_slider.setRange(min_x, max_x)
            self.y1_spinbox.setRange(min_y, max_y)
            self.y1_slider.setRange(min_y, max_y)
            
            # Обновляем диапазоны для X2, Y2
            self.x2_spinbox.setRange(min_x, max_x)
            self.x2_slider.setRange(min_x, max_x)
            self.y2_spinbox.setRange(min_y, max_y)
            self.y2_slider.setRange(min_y, max_y)
        except Exception as e:
            logger.error(f"Ошибка при обновлении диапазонов: {e}")
            
    def reset_properties(self):
        """Сброс свойств стены к начальным значениям."""
        if not self.initial_values:
            return
            
        try:
            # Устанавливаем начальные значения
            self.set_properties(
                self.initial_values.get('x1', 0),
                self.initial_values.get('y1', 0),
                self.initial_values.get('x2', 0),
                self.initial_values.get('y2', 0),
                self.initial_values.get('width', 1),
                self.initial_values.get('id', '')
            )
            
            # Оповещаем об изменениях
            self.position_point1_changed.emit(
                self.initial_values.get('x1', 0),
                self.initial_values.get('y1', 0)
            )
            self.position_point2_changed.emit(
                self.initial_values.get('x2', 0),
                self.initial_values.get('y2', 0)
            )
            self.width_changed.emit(self.initial_values.get('width', 1))
            if self.initial_values.get('id'):
                self.id_changed.emit(self.initial_values.get('id', ''))
        except Exception as e:
            logger.error(f"Ошибка при сбросе свойств стены: {e}")
            
    def update_step_sizes(self, step_size=1):
        """
        Обновление шага изменения для спинбоксов.
        
        Args:
            step_size: Размер шага
        """
        try:
            self.x1_spinbox.setSingleStep(step_size)
            self.y1_spinbox.setSingleStep(step_size)
            self.x2_spinbox.setSingleStep(step_size)
            self.y2_spinbox.setSingleStep(step_size)
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага спинбоксов: {e}")
    
    # Обработчики событий для слайдеров
    def on_x1_slider_changed(self, value):
        """
        Обработчик изменения слайдера X1.
        
        Args:
            value: Новое значение X1
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.x1_spinbox):
                self.x1_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции точки 1
            self.position_point1_changed.emit(value, self.y1_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X1-координаты: {e}")
            
    def on_y1_slider_changed(self, value):
        """
        Обработчик изменения слайдера Y1.
        
        Args:
            value: Новое значение Y1
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.y1_spinbox):
                self.y1_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции точки 1
            self.position_point1_changed.emit(self.x1_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y1-координаты: {e}")
            
    def on_x2_slider_changed(self, value):
        """
        Обработчик изменения слайдера X2.
        
        Args:
            value: Новое значение X2
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.x2_spinbox):
                self.x2_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции точки 2
            self.position_point2_changed.emit(value, self.y2_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X2-координаты: {e}")
            
    def on_y2_slider_changed(self, value):
        """
        Обработчик изменения слайдера Y2.
        
        Args:
            value: Новое значение Y2
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.y2_spinbox):
                self.y2_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции точки 2
            self.position_point2_changed.emit(self.x2_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y2-координаты: {e}")
            
    def on_width_slider_changed(self, value):
        """
        Обработчик изменения слайдера ширины.
        
        Args:
            value: Новое значение ширины
        """
        try:
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.wall_width_spinbox):
                self.wall_width_spinbox.setValue(value)
                
            # Оповещаем об изменении ширины
            self.width_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при изменении ширины: {e}")
            
    def on_id_changed(self, new_id, item=None):
        """
        Обработчик изменения ID стены.
        
        Args:
            new_id: Новый ID
            item: Элемент стены (опционально)
        """
        try:
            self.id_changed.emit(new_id)
        except Exception as e:
            logger.error(f"Ошибка при изменении ID стены: {e}")
            
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
        
        # Обновляем стиль для EditableLineEdit с ID стены
        self.apply_field_style(self.id_edit)
        
        # Обновляем стили всех статических меток
        self.apply_field_style(self.id_label)
        self.apply_field_style(self.coords_label)
        self.apply_field_style(self.x1_label)
        self.apply_field_style(self.y1_label)
        self.apply_field_style(self.x2_label)
        self.apply_field_style(self.y2_label)
        self.apply_field_style(self.width_label)
        
    def update_properties(self, wall):
        """
        Обновление свойств виджета на основе объекта стены.
        
        Args:
            wall: Объект стены
        """
        if self.field_widget:
            self.update_ranges(
                int(self.field_widget.scene().sceneRect().left()),
                int(self.field_widget.scene().sceneRect().right()),
                int(self.field_widget.scene().sceneRect().top()),
                int(self.field_widget.scene().sceneRect().bottom())
            )
        
        line = wall.line()
        self.set_properties(
            int(line.x1()), 
            int(line.y1()),
            int(line.x2()), 
            int(line.y2()),
            wall.pen().width(),
            wall.wall_id
        )
    
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

    def on_x1_changed(self, value):
        """Обработчик изменения значения X1 в спинбоксе."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.x1_spinbox):
                    self.x1_spinbox.setValue(value)
                
            # Оповещаем об изменении координат
            self.position_point1_changed.emit(value, self.y1_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X1 через спинбокс: {e}")
            
    def on_y1_changed(self, value):
        """Обработчик изменения значения Y1 в спинбоксе."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.y1_spinbox):
                    self.y1_spinbox.setValue(value)
                
            # Оповещаем об изменении координат
            self.position_point1_changed.emit(self.x1_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y1 через спинбокс: {e}")
            
    def on_x2_changed(self, value):
        """Обработчик изменения значения X2 в спинбоксе."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.x2_spinbox):
                    self.x2_spinbox.setValue(value)
                
            # Оповещаем об изменении координат
            self.position_point2_changed.emit(value, self.y2_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X2 через спинбокс: {e}")
            
    def on_y2_changed(self, value):
        """Обработчик изменения значения Y2 в спинбоксе."""
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.y2_spinbox):
                    self.y2_spinbox.setValue(value)
                
            # Оповещаем об изменении координат
            self.position_point2_changed.emit(self.x2_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y2 через спинбокс: {e}")
            
    def on_width_changed(self, value):
        """Обработчик изменения значения ширины в спинбоксе."""
        try:                
            # Оповещаем об изменении ширины
            self.width_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при изменении ширины через спинбокс: {e}")

    # Обработчики завершения редактирования
    def on_x1_editing_finished(self):
        """Обработчик завершения редактирования X1-координаты."""
        try:
            value = self.x1_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.x1_spinbox.value():
                    with SignalBlock(self.x1_spinbox):
                        self.x1_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.x1_slider):
                self.x1_slider.setValue(value)
                
            # Оповещаем об изменении позиции точки 1
            self.position_point1_changed.emit(value, self.y1_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X1: {e}")
            
    def on_y1_editing_finished(self):
        """Обработчик завершения редактирования Y1-координаты."""
        try:
            value = self.y1_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.y1_spinbox.value():
                    with SignalBlock(self.y1_spinbox):
                        self.y1_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.y1_slider):
                self.y1_slider.setValue(value)
                
            # Оповещаем об изменении позиции точки 1
            self.position_point1_changed.emit(self.x1_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y1: {e}")
            
    def on_x2_editing_finished(self):
        """Обработчик завершения редактирования X2-координаты."""
        try:
            value = self.x2_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.x2_spinbox.value():
                    with SignalBlock(self.x2_spinbox):
                        self.x2_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.x2_slider):
                self.x2_slider.setValue(value)
                
            # Оповещаем об изменении позиции точки 2
            self.position_point2_changed.emit(value, self.y2_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X2: {e}")
            
    def on_y2_editing_finished(self):
        """Обработчик завершения редактирования Y2-координаты."""
        try:
            value = self.y2_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                grid_size = getattr(self.field_widget, 'grid_size', 10)
                value = snap_to_grid(value, grid_size)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.y2_spinbox.value():
                    with SignalBlock(self.y2_spinbox):
                        self.y2_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.y2_slider):
                self.y2_slider.setValue(value)
                
            # Оповещаем об изменении позиции точки 2
            self.position_point2_changed.emit(self.x2_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y2: {e}")
            
    def on_width_editing_finished(self):
        """Обработчик завершения редактирования ширины."""
        try:
            value = self.wall_width_spinbox.value()
            
            # Обновляем слайдер
            with SignalBlock(self.wall_width_slider):
                self.wall_width_slider.setValue(value)
                
            # Оповещаем об изменении ширины
            self.width_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования ширины: {e}") 