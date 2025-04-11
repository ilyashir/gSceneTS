"""
Виджет свойств робота.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QFormLayout, QSlider, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import snap_to_grid, snap_rotation_to_grid
from utils.signal_utils import SignalBlock
from custom_widgets import CustomSpinBox

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
        
        # Добавляем атрибут для хранения состояния привязки
        self._snap_enabled = True
        # Добавляем инициализацию _step_size и _rotation_step, чтобы избежать AttributeError
        self._step_size = 50  # Значение шага по умолчанию для спинбоксов и слайдеров (половина размера сетки)
        self._rotation_step = 45
        
    def create_widgets(self):
        """Создание всех виджетов."""
        # ID робота (неизменяемый)
        self.id_label = QLabel("ID:")
        self.robot_id_label = QLineEdit("trikKitRobot")
        self.robot_id_label.setReadOnly(True)
        
        # Координата X с ползунком
        self.x_label = QLabel("X:")
        self.x_spinbox = CustomSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setMinimumWidth(70)
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-10000, 10000)
        
        # Координата Y с ползунком
        self.y_label = QLabel("Y:")
        self.y_spinbox = CustomSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setMinimumWidth(70)
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-10000, 10000)
        
        # Поворот с ползунком
        self.rotation_label = QLabel("Поворот:")
        self.rotation_spinbox = CustomSpinBox()
        self.rotation_spinbox.setRange(-180, 180)
        self.rotation_spinbox.setMinimumWidth(70)
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_snap_step_size(True)
        
    def create_layouts(self):
        """Создание и настройка компоновки."""
        layout = QVBoxLayout()
        
        # ID робота
        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_label)
        id_layout.addWidget(self.robot_id_label)
        layout.addLayout(id_layout)
        
        # Используем FormLayout для организации полей
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # X с ползунком
        x_layout = QHBoxLayout()
        x_layout.addWidget(self.x_spinbox)
        x_layout.addWidget(self.x_slider)
        form_layout.addRow(self.x_label, x_layout)
        
        # Y с ползунком
        y_layout = QHBoxLayout()
        y_layout.addWidget(self.y_spinbox)
        y_layout.addWidget(self.y_slider)
        form_layout.addRow(self.y_label, y_layout)
        
        # Поворот с ползунком
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self.rotation_spinbox)
        rotation_layout.addWidget(self.rotation_slider)
        form_layout.addRow(self.rotation_label, rotation_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопка сброса параметров
        layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Очищаем текущий лейаут и добавляем новый
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                
        self.properties_layout.addLayout(layout)
        
    def setup_connections(self):
        """Подключение сигналов и слотов."""
        # Связываем слайдеры и спинбоксы
        self.x_spinbox.buttonValueChanged.connect(self.on_x_spinbox_value_changed)
        self.x_slider.valueChanged.connect(self.on_x_slider_changed)
        
        self.y_spinbox.buttonValueChanged.connect(self.on_y_spinbox_value_changed)
        self.y_slider.valueChanged.connect(self.on_y_slider_changed)
        
        self.rotation_spinbox.buttonValueChanged.connect(self.on_rotation_spinbox_value_changed)
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
            logger.debug(f"Установка свойств робота: x={x}, y={y}, rotation={rotation}, robot_id={robot_id}")
            
            self.x_spinbox.blockSignals(True)
            self.y_spinbox.blockSignals(True)
            self.rotation_spinbox.blockSignals(True)
            self.x_slider.blockSignals(True) 
            self.y_slider.blockSignals(True)
            self.rotation_slider.blockSignals(True)
            
            self.x_spinbox.setValue(x)
            self.y_spinbox.setValue(y)
            self.rotation_spinbox.setValue(rotation)
            
            self.x_slider.setValue(x)
            self.y_slider.setValue(y)
            self.rotation_slider.setValue(rotation)
            
            self.x_spinbox.blockSignals(False)
            self.y_spinbox.blockSignals(False)
            self.rotation_spinbox.blockSignals(False)
            self.x_slider.blockSignals(False)
            self.y_slider.blockSignals(False)
            self.rotation_slider.blockSignals(False)
                
            # Обновляем ID если он предоставлен
            if robot_id:
                self.robot_id_label.setText(robot_id)
                
            logger.debug(f"Свойства робота установлены: x={x}, y={y}, rotation={rotation}")
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
            logger.debug(f"Обновление диапазонов робота: min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}")
            
            # Размер робота (50x50)
            robot_size = 50
            
            # Обновляем диапазоны для X c учетом размера робота
            self.x_spinbox.setRange(min_x, max_x - robot_size)
            self.x_slider.setRange(min_x, max_x - robot_size)
            
            # Обновляем диапазоны для Y
            self.y_spinbox.setRange(min_y, max_y - robot_size)
            self.y_slider.setRange(min_y, max_y - robot_size)
            
            logger.debug(f"Установлены диапазоны для X: [{min_x}, {max_x - robot_size}], Y: [{min_y}, {max_y - robot_size}]")
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
    
    # Обработчики событий
    def on_x_spinbox_value_changed(self, value):
        """Обработчик изменения значения X в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)
                with SignalBlock(self.x_spinbox):
                    self.x_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
            
            logger.debug(f"X-координата изменена через спинбокс: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты через спинбокс: {e}")

    def on_y_spinbox_value_changed(self, value):
        """Обработчик изменения значения Y в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)
                with SignalBlock(self.y_spinbox):
                    self.y_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
            
            logger.debug(f"Y-координата изменена через спинбокс: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты через спинбокс: {e}")

    def on_rotation_spinbox_value_changed(self, value):
        """Обработчик изменения значения поворота в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:
                value = snap_rotation_to_grid(value, 45)
                
                # Блокируем сигналы при обновлении значения
                with SignalBlock(self.rotation_spinbox):
                    self.rotation_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.rotation_slider):
                self.rotation_slider.setValue(value)
                
            # Оповещаем об изменении поворота
            self.rotation_changed.emit(value)
            
            logger.debug(f"Угол поворота изменен через спинбокс: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении поворота через спинбокс: {e}")

    def on_x_slider_changed(self, value):
        """
        Обработчик изменения слайдера X.
        
        Args:
            value: Новое значение X
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)

            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.x_spinbox):
                self.x_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
            
            logger.debug(f"X-координата изменена через слайдер: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты через слайдер: {e}")
            
    def on_y_slider_changed(self, value):
        """
        Обработчик изменения слайдера Y.
        
        Args:
            value: Новое значение Y
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.y_spinbox):
                self.y_spinbox.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
            
            logger.debug(f"Y-координата изменена через слайдер: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты через слайдер: {e}")
            
    def on_rotation_slider_changed(self, value):
        """
        Обработчик изменения слайдера поворота.
        
        Args:
            value: Новое значение поворота
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:
                value = snap_rotation_to_grid(value, 45)
                
            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.rotation_spinbox):
                self.rotation_spinbox.setValue(value)
                
            # Оповещаем об изменении поворота
            self.rotation_changed.emit(value)
            
            logger.debug(f"Угол поворота изменен через слайдер: {value}")
        except Exception as e:
            logger.error(f"Ошибка при изменении угла поворота через слайдер: {e}")
            
    def on_x_editing_finished(self):
        """Обработчик завершения редактирования X-координаты."""
        try:
            value = self.x_spinbox.value()

            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)

            # Обновляем слайдер
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
            
            logger.debug(f"X-координата робота изменена после окончания редактирования: {value}")
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X: {e}")
            
    def on_y_editing_finished(self):
        """Обработчик завершения редактирования Y-координаты."""
        try:
            value = self.y_spinbox.value()
                
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)

            # Обновляем слайдер
            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
            
            logger.debug(f"Y-координата робота изменена после окончания редактирования: {value}")
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y: {e}")
            
    def on_rotation_editing_finished(self):
        """Обработчик завершения редактирования поворота."""
        try:
            value = self.rotation_spinbox.value()
            
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:
                value = snap_rotation_to_grid(value, 45)
                            
            # Обновляем слайдер
            with SignalBlock(self.rotation_slider):
                self.rotation_slider.setValue(value)
                
            # Оповещаем об изменении поворота
            self.rotation_changed.emit(value)
            
            logger.debug(f"Угол поворота изменен на {value}")
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования поворота: {e}")
            
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
        # Всегда обновляем диапазоны в первую очередь, они должны быть корректны
        # перед установкой значений
        try:
            if self.field_widget:
                # Получаем границы сцены для установки диапазонов
                scene_rect = self.field_widget.scene().sceneRect()
                min_x = int(scene_rect.left())
                max_x = int(scene_rect.right())
                min_y = int(scene_rect.top())
                max_y = int(scene_rect.bottom())
                
                # Вызываем метод обновления диапазонов
                self.update_ranges(min_x, max_x, min_y, max_y)                
            
            self.set_properties(
                int(robot.x()),
                int(robot.y()),
                int(robot.rotation()),
                "trikKitRobot"
            )
        except Exception as e:
            logger.error(f"Ошибка при обновлении свойств робота: {e}")
    
    def connect_to_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
    
    def set_snap_enabled(self, enabled):
        """
        Установка состояния привязки к сетке.
        
        Args:
            enabled: True для включения привязки, False для отключения
        """
        logger.debug(f"RobotPropertiesWidget: set_snap_enabled вызван с параметром {enabled}")
        
        if self._snap_enabled != enabled:
             self._snap_enabled = enabled
             self.update_snap_step_size(enabled)
        
    def update_snap_step_size(self, enabled):
        """Устанавливает шаг спинбоксов в зависимости от состояния привязки к сетке."""
        try:
            if enabled:
                step_size = 50  # Шаг сетки для робота
                rotation_step = 45
                logger.debug(f"Установка шага для робота (привязка вкл.): коорд={step_size}, поворот={rotation_step}")
            else:
                step_size = 1
                rotation_step = 1
                logger.debug("Установка шага для робота (привязка выкл.): 1")

            # Сохраняем шаги как атрибуты
            self._step_size = step_size
            self._rotation_step = rotation_step
            logger.debug(f"[USSS] robot шаг={self._step_size}, поворот={self._rotation_step}")
            
            # Координаты X, Y
            self.x_spinbox.setSingleStep(step_size)
            self.y_spinbox.setSingleStep(step_size)
            self.x_slider.setSingleStep(step_size)
            self.y_slider.setSingleStep(step_size)

            # Поворот
            self.rotation_spinbox.setSingleStep(rotation_step)
            self.rotation_slider.setSingleStep(rotation_step)

        except Exception as e:
            logger.error(f"Ошибка при установке шага привязки для робота: {e}") 