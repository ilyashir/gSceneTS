"""
Виджет свойств робота.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QFormLayout, QSlider, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import snap_to_grid, snap_rotation_to_grid, is_snap_enabled
from utils.signal_utils import SignalBlock

logger = logging.getLogger(__name__)

class RobotPropertiesWidget(BasePropertiesWidget):
    """
    Виджет для отображения и редактирования свойств робота.
    """
    # Сигналы
    position_changed = pyqtSignal(int, int)  # x, y
    rotation_changed = pyqtSignal(int)  # rotation
    
    def __init__(self, parent=None, is_dark_theme=False):
        """
        Инициализация виджета свойств робота.
        
        Args:
            parent: Родительский виджет
            is_dark_theme: Флаг темной темы
        """
        super().__init__("Свойства робота", parent)
        self.apply_theme(is_dark_theme)
        self._initialize_ui()
        self._connect_signals()
        self.setup_cursors()
        
    def _initialize_ui(self):
        """Инициализация интерфейса виджета."""
        layout = QVBoxLayout()
        
        # ID робота (неизменяемый)
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.robot_id_label = QLabel("trikKitRobot")
        self.apply_field_style(self.robot_id_label)
        id_layout.addWidget(self.robot_id_label)
        layout.addLayout(id_layout)
        
        # Используем FormLayout для организации полей
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Координата X с ползунком
        x_layout = QHBoxLayout()
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setMinimumWidth(70)
        
        # Ползунок X
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-10000, 10000)
        
        x_layout.addWidget(self.x_spinbox)
        x_layout.addWidget(self.x_slider)
        form_layout.addRow("X:", x_layout)
        
        # Координата Y с ползунком
        y_layout = QHBoxLayout()
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setMinimumWidth(70)
        
        # Ползунок Y
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-10000, 10000)
        
        y_layout.addWidget(self.y_spinbox)
        y_layout.addWidget(self.y_slider)
        form_layout.addRow("Y:", y_layout)
        
        # Поворот с ползунком
        rotation_layout = QHBoxLayout()
        self.rotation_spinbox = QSpinBox()
        self.rotation_spinbox.setRange(-180, 180)
        self.rotation_spinbox.setMinimumWidth(70)
        
        # Ползунок для поворота
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        
        rotation_layout.addWidget(self.rotation_spinbox)
        rotation_layout.addWidget(self.rotation_slider)
        form_layout.addRow("Поворот:", rotation_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.properties_layout.addLayout(layout)
        
    def _connect_signals(self):
        """Подключение сигналов и слотов."""
        # Связываем слайдеры и спинбоксы
        self.x_spinbox.valueChanged.connect(self.x_slider.setValue)
        self.x_slider.valueChanged.connect(self.on_x_slider_changed)
        
        self.y_spinbox.valueChanged.connect(self.y_slider.setValue)
        self.y_slider.valueChanged.connect(self.on_y_slider_changed)
        
        self.rotation_spinbox.valueChanged.connect(self.rotation_slider.setValue)
        self.rotation_slider.valueChanged.connect(self.on_rotation_slider_changed)
        
        # Подключаем сигналы редактирования
        self.x_spinbox.editingFinished.connect(self.on_x_editing_finished)
        self.y_spinbox.editingFinished.connect(self.on_y_editing_finished)
        self.rotation_spinbox.editingFinished.connect(self.on_rotation_editing_finished)
        
        # Подключаем кнопку сброса
        self.reset_button.clicked.connect(self.reset_properties)
        
    def set_properties(self, x, y, rotation, robot_id=None):
        """
        Установка свойств робота.
        
        Args:
            x: X-координата
            y: Y-координата
            rotation: Угол поворота
            robot_id: ID робота (опционально)
        """
        try:
            # Запоминаем начальные значения для возможности сброса
            self.initial_values = {
                'x': x,
                'y': y,
                'rotation': rotation
            }
            
            # Блокируем сигналы на время обновления
            with SignalBlock(self.x_spinbox), SignalBlock(self.x_slider), \
                 SignalBlock(self.y_spinbox), SignalBlock(self.y_slider), \
                 SignalBlock(self.rotation_spinbox), SignalBlock(self.rotation_slider):
                
                self.x_spinbox.setValue(x)
                self.x_slider.setValue(x)
                
                self.y_spinbox.setValue(y)
                self.y_slider.setValue(y)
                
                self.rotation_spinbox.setValue(rotation)
                self.rotation_slider.setValue(rotation)
                
                # Обновляем ID если он предоставлен
                if robot_id:
                    self.robot_id_label.setText(robot_id)
        except Exception as e:
            logger.error(f"Ошибка при установке свойств робота: {e}")
            
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
            # Обновляем диапазоны для X
            self.x_spinbox.setRange(min_x, max_x)
            self.x_slider.setRange(min_x, max_x)
            
            # Обновляем диапазоны для Y
            self.y_spinbox.setRange(min_y, max_y)
            self.y_slider.setRange(min_y, max_y)
        except Exception as e:
            logger.error(f"Ошибка при обновлении диапазонов: {e}")
            
    def reset_properties(self):
        """Сброс свойств робота к начальным значениям."""
        if not self.initial_values:
            return
            
        try:
            # Устанавливаем начальные значения
            self.set_properties(
                self.initial_values.get('x', 0),
                self.initial_values.get('y', 0),
                self.initial_values.get('rotation', 0)
            )
            
            # Оповещаем об изменениях
            self.position_changed.emit(
                self.initial_values.get('x', 0),
                self.initial_values.get('y', 0)
            )
            self.rotation_changed.emit(self.initial_values.get('rotation', 0))
        except Exception as e:
            logger.error(f"Ошибка при сбросе свойств робота: {e}")
            
    def update_step_sizes(self, step_size=1):
        """
        Обновление шага изменения для спинбоксов.
        
        Args:
            step_size: Размер шага
        """
        try:
            self.x_spinbox.setSingleStep(step_size)
            self.y_spinbox.setSingleStep(step_size)
            
            # Для поворота используем шаг 45 градусов если включен snap_to_grid
            if is_snap_enabled(self.field_widget):
                self.rotation_spinbox.setSingleStep(45)
            else:
                self.rotation_spinbox.setSingleStep(1)
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага спинбоксов: {e}")
    
    # Обработчики событий
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
            
    def on_rotation_slider_changed(self, value):
        """
        Обработчик изменения слайдера поворота.
        
        Args:
            value: Новое значение поворота
        """
        try:
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                value = snap_rotation_to_grid(value, 45)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.rotation_spinbox):
                self.rotation_spinbox.setValue(value)
                
            # Оповещаем об изменении поворота
            self.rotation_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при изменении поворота: {e}")
            
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
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y: {e}")
            
    def on_rotation_editing_finished(self):
        """Обработчик завершения редактирования поворота."""
        try:
            value = self.rotation_spinbox.value()
            
            # Привязка к сетке если необходимо
            if is_snap_enabled(self.field_widget):
                value = snap_rotation_to_grid(value, 45)
                
                # Обновляем значение в спинбоксе если оно изменилось
                if value != self.rotation_spinbox.value():
                    with SignalBlock(self.rotation_spinbox):
                        self.rotation_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.rotation_slider):
                self.rotation_slider.setValue(value)
                
            # Оповещаем об изменении поворота
            self.rotation_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования поворота: {e}")
            
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
    
    def update_properties(self, robot):
        """
        Обновление свойств виджета на основе объекта робота.
        
        Args:
            robot: Объект робота
        """
        if self.field_widget:
            self.update_ranges(
                int(self.field_widget.scene().sceneRect().left()),
                int(self.field_widget.scene().sceneRect().right()),
                int(self.field_widget.scene().sceneRect().top()),
                int(self.field_widget.scene().sceneRect().bottom())
            )
        
        self.set_properties(
            int(robot.x()),
            int(robot.y()),
            int(robot.rotation()),
            "trikKitRobot"
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