"""
Виджет свойств региона.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QFormLayout, QSlider, QPushButton, QWidget, QLineEdit, QColorDialog, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIntValidator
import logging
from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import snap_to_grid, is_snap_enabled
from utils.signal_utils import SignalBlock
from custom_widgets import EditableLineEdit, ColorPickerButton, CustomSpinBox
from scene.items.region import Region

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
        self.is_dark_theme = is_dark_theme
        self.apply_theme(self.is_dark_theme)
        self.field_widget = None
        self.initial_values = {}
        
        # Добавляем атрибут для хранения состояния привязки
        self._snap_enabled = True
        self._step_size = 50  # Значение шага по умолчанию для спинбоксов и слайдеров (половина размера сетки)


    def create_widgets(self):
        """Создание всех виджетов."""
        # ID региона
        self.id_label = QLabel("ID:")
        self.id_edit = QLineEdit()
        
        # Позиция
        self.position_label = QLabel("<b>Позиция</b>")
        
        # X с ползунком
        self.x_label = QLabel("X:")
        self.x_spinbox = CustomSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setMinimumWidth(70)
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-10000, 10000)
        
        # Y с ползунком
        self.y_label = QLabel("Y:")
        self.y_spinbox = CustomSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setMinimumWidth(70)
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-10000, 10000)
        
        # Размер
        self.size_label = QLabel("<b>Размер</b>")
        
        # Ширина с ползунком
        self.width_label = QLabel("Ширина:")
        self.width_spinbox = CustomSpinBox()
        self.width_spinbox.setRange(1, 1000)
        self.width_spinbox.setMinimumWidth(70)
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 1000)
        
        # Высота с ползунком
        self.height_label = QLabel("Высота:")
        self.height_spinbox = CustomSpinBox()
        self.height_spinbox.setRange(1, 1000)
        self.height_spinbox.setMinimumWidth(70)
        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setRange(1, 1000)
        
        # Цвет
        self.color_label = QLabel("Цвет:")
        self.color_button = ColorPickerButton(is_dark_theme=self.is_dark_theme)
        
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_snap_step_size(True)
        
    def create_layouts(self):
        """Создание и настройка компоновки."""
        layout = QVBoxLayout()
        
        # ID региона
        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_label)
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)
        
        # Используем FormLayout для организации полей
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Позиция
        form_layout.addRow(self.position_label)
        
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
        
        # Размер
        form_layout.addRow(self.size_label)
        
        # Ширина с ползунком
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_spinbox)
        width_layout.addWidget(self.width_slider)
        form_layout.addRow(self.width_label, width_layout)
        
        # Высота с ползунком
        height_layout = QHBoxLayout()
        height_layout.addWidget(self.height_spinbox)
        height_layout.addWidget(self.height_slider)
        form_layout.addRow(self.height_label, height_layout)
        
        # Цвет
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_button)
        form_layout.addRow(color_layout)
        
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
        # Связываем слайдеры и спинбоксы для позиции
        self.x_spinbox.buttonValueChanged.connect(self.on_x_spinbox_changed)
        self.x_slider.valueChanged.connect(self.on_x_slider_changed)

        self.y_spinbox.buttonValueChanged.connect(self.on_y_spinbox_changed)
        self.y_slider.valueChanged.connect(self.on_y_slider_changed)
        
        # Связываем слайдеры и спинбоксы для размера
        self.width_spinbox.buttonValueChanged.connect(self.on_width_spinbox_changed)
        self.width_slider.valueChanged.connect(self.on_width_slider_changed)
        
        self.height_spinbox.buttonValueChanged.connect(self.on_height_spinbox_changed)
        self.height_slider.valueChanged.connect(self.on_height_slider_changed)
        
        # Подключаем сигналы редактирования
        self.x_spinbox.editingFinished.connect(self.on_x_editing_finished)
        self.y_spinbox.editingFinished.connect(self.on_y_editing_finished)
        self.width_spinbox.editingFinished.connect(self.on_width_editing_finished)
        self.height_spinbox.editingFinished.connect(self.on_height_editing_finished)
        
        # Подключаем изменение цвета
        self.color_button.colorChanged.connect(self.on_color_changed)
        
        # Подключаем изменение ID
        self.id_edit.editingFinished.connect(self.on_id_changed)
        
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
                    self.id_edit.setText(region_id)
        except Exception as e:
            logger.error(f"Ошибка при установке свойств региона: {e}")
            
             
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
            
    def update_step_sizes(self):
        """
        Обновление шага изменения для спинбоксов и слайдеров.
        Использует текущее значение _step_size, которое установлено в set_snap_enabled.
        """
        try:
            # Устанавливаем шаг для спинбоксов
            self.x_spinbox.setSingleStep(self._step_size)
            self.y_spinbox.setSingleStep(self._step_size)
            self.width_spinbox.setSingleStep(self._step_size)
            self.height_spinbox.setSingleStep(self._step_size)
            
            # Устанавливаем шаг для слайдеров
            self.x_slider.setSingleStep(self._step_size)
            self.y_slider.setSingleStep(self._step_size)
            self.width_slider.setSingleStep(self._step_size)
            self.height_slider.setSingleStep(self._step_size)
            
            logger.debug(f"Установлен шаг {self._step_size} для региона")
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага для контролов региона: {e}")
            
    # Обработчики событий для слайдеров
    def on_x_slider_changed(self, value):
        """
        Обработчик изменения слайдера X.
        
        Args:
            value: Новое значение X
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:  
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число

            self.update_ranges()

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
                grid_size = getattr(self.field_widget, 'grid_size', 50)
                value = int(snap_to_grid(value, grid_size))  # Преобразуем в целое число
                logger.debug(f"Привязка координаты Y региона к сетке с шагом {grid_size}: {value}")
                
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
            if self._snap_enabled:
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число


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
            if self._snap_enabled:
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число


            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.height_spinbox):
                self.height_spinbox.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении высоты: {e}")
            
    # Новые обработчики для спинбоксов
    def on_x_spinbox_changed(self, value):
        """
        Обработчик изменения спинбокса X.
        
        Args:
            value: Новое значение X
        """
        try:
            # Привязка к сетке если необходимо
            if self._snap_enabled:
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число
                with SignalBlock(self.x_spinbox):
                    self.x_spinbox.setValue(value)
                    
            self.update_ranges()
            
            # Устанавливаем значение в слайдер без эмиссии сигнала
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты: {e}")
            
    def on_y_spinbox_changed(self, value):
        """
        Обработчик изменения спинбокса Y.
        
        Args:
            value: Новое значение Y
        """
        try:
            # Привязка к сетке если необходимо
            if self._snap_enabled:
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число
                with SignalBlock(self.y_spinbox):
                    self.y_spinbox.setValue(value)
                    
            self.update_ranges()
            
            # Устанавливаем значение в слайдер без эмиссии сигнала
            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты: {e}")
            
    def on_width_spinbox_changed(self, value):
        """
        Обработчик изменения спинбокса ширины.
        
        Args:
            value: Новое значение ширины
        """
        try:
            # Привязка к сетке если необходимо
            if self._snap_enabled:
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число
                with SignalBlock(self.width_spinbox):
                    self.width_spinbox.setValue(value)

            self.update_ranges()
            
            # Устанавливаем значение в слайдер без эмиссии сигнала
            with SignalBlock(self.width_slider):
                self.width_slider.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(value, self.height_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при изменении ширины: {e}")
            
    def on_height_spinbox_changed(self, value):
        """
        Обработчик изменения спинбокса высоты.
        
        Args:
            value: Новое значение высоты
        """
        try:
            # Привязка к сетке если необходимо
            if self._snap_enabled:                
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число
                logger.debug(f"Привязка высоты спинбокса региона к сетке с шагом {self._step_size}: {value}")
                with SignalBlock(self.height_spinbox):
                    self.height_spinbox.setValue(value)

            self.update_ranges()

            # Устанавливаем значение в слайдер без эмиссии сигнала
            with SignalBlock(self.height_slider):
                self.height_slider.setValue(value)
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при изменении высоты: {e}")
            
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
            
    def on_id_changed(self):
        """
        Обработчик изменения ID региона.
        
        Args:
            new_id: Новый ID
        """
        try:
            self.id_changed.emit(self.id_edit.text())
        except Exception as e:
            logger.error(f"Ошибка при изменении ID региона: {e}")
            
    def set_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
    
    def set_theme(self, is_dark_theme):
        """
        Установка темы оформления.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.is_dark_theme = is_dark_theme
        self.apply_theme(self.is_dark_theme)
        # Обновляем тему для кнопки выбора цвета
        self.color_button.set_theme(self.is_dark_theme)
    
    def update_properties(self, item):
        """
        Обновляет отображаемые свойства региона.
        
        Args:
            item: Объект региона
        """
        try:
            if not item:
                logger.warning("Пустой объект региона")
                return
                
            logger.debug(f"Обновление свойств для региона: {item}")
            self.update_ranges()               
            
            self.set_properties(
                int(item.pos().x()), 
                int(item.pos().y()), 
                int(item.width()), 
                int(item.height()), 
                item.color, 
                item.id
                )
            
            logger.debug(f"Свойства региона обновлены: x={item.pos().x()}, y={item.pos().y()}, width={item.width()}, height={item.height()}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении свойств региона: {e}")

    def connect_to_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget

    # Обработчики завершения редактирования
    def on_x_editing_finished(self):
        """Обработчик завершения редактирования X-координаты."""
        try:
            value = self.x_spinbox.value()
            
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:  
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число

                with SignalBlock(self.x_spinbox):
                    self.x_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)        
            
            self.update_ranges()
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(value, self.y_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X: {e}")

    def on_y_editing_finished(self):
        """Обработчик завершения редактирования Y-координаты."""
        try:
            value = self.y_spinbox.value()
            
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:  
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число

                with SignalBlock(self.y_spinbox):
                    self.y_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)

            self.update_ranges()
                
            # Оповещаем об изменении позиции
            self.position_changed.emit(self.x_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y: {e}")

    def on_width_editing_finished(self):
        """Обработчик завершения редактирования ширины."""
        try:
            value = self.width_spinbox.value()
            
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:  
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число

                with SignalBlock(self.width_spinbox):
                    self.width_spinbox.setValue(value)
                
            # Обновляем слайдер
            with SignalBlock(self.width_slider):
                self.width_slider.setValue(value)
            
            self.update_ranges()
                
            # Оповещаем об изменении размера
            self.size_changed.emit(value, self.height_spinbox.value())
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования ширины: {e}")

    def on_height_editing_finished(self):
        """Обработчик завершения редактирования высоты."""
        try:
            value = self.height_spinbox.value()

            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:  
                value = int(snap_to_grid(value, self._step_size))  # Преобразуем в целое число

                with SignalBlock(self.height_spinbox):
                    self.height_spinbox.setValue(value)

            with SignalBlock(self.height_slider):
                self.height_slider.setValue(value)

            self.update_ranges()
                
            # Оповещаем об изменении размера
            self.size_changed.emit(self.width_spinbox.value(), value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования высоты: {e}")

    # --- Добавляем метод set_snap_enabled --- 
    def set_snap_enabled(self, enabled):
        """
        Устанавливает режим привязки к сетке.
        
        Args:
            enabled: флаг, включена ли привязка к сетке
        """
        try:
            self._snap_enabled = enabled
            
            # Устанавливаем шаг в зависимости от того, включена ли привязка
            if self.field_widget and hasattr(self.field_widget, 'grid_size'):
                grid_size = self.field_widget.grid_size
                self._step_size = grid_size if enabled else 1
            else:
                self._step_size = 50 if enabled else 1
                
            # Обновляем шаг для контролов
            self.update_step_sizes()  
            
            logger.debug(f"RegionPropertiesWidget: установлен шаг {self._step_size} (привязка к сетке: {enabled})")
        except Exception as e:
            logger.error(f"Ошибка при установке режима привязки к сетке: {e}") 

    def update_snap_step_size(self, enabled):
        """Устанавливает шаг спинбоксов в зависимости от состояния привязки к сетке."""
        try:
            if enabled:
                step_size = 50  # Шаг сетки для региона
                logger.debug(f"Установка шага для региона (привязка вкл.): {step_size}")
            else:
                step_size = 1
                logger.debug("Установка шага для региона (привязка выкл.): 1")

            # Сохраняем шаг как атрибут
            self._step_size = step_size

            # Координаты X, Y, Ширина, Высота
            self.x_spinbox.setSingleStep(step_size)
            self.y_spinbox.setSingleStep(step_size)
            self.width_spinbox.setSingleStep(step_size)
            self.height_spinbox.setSingleStep(step_size)

            self.x_slider.setSingleStep(step_size)
            self.y_slider.setSingleStep(step_size)
            self.width_slider.setSingleStep(step_size)
            self.height_slider.setSingleStep(step_size)
            
            # Обновляем минимальные значения для размера (должны быть >= шагу)
            # Делаем это здесь, т.к. минимальный размер зависит от шага
            self.width_spinbox.setMinimum(step_size)
            self.height_spinbox.setMinimum(step_size)
            self.width_slider.setMinimum(step_size)
            self.height_slider.setMinimum(step_size)

        except Exception as e:
            logger.error(f"Ошибка при установке шага привязки для региона: {e}")
            
    def update_ranges(self, min_x=-10000, max_x=10000, min_y=-10000, max_y=10000):
        """
        Обновление диапазонов значений.
        Шаг больше не устанавливается здесь, но минимальный размер зависит от _step_size.
        """
        try:
            logger.debug(f"Обновление диапазонов RegionProperties: min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}")
            
            if self.field_widget:
                min_x = int(self.field_widget.scene().sceneRect().left())
                max_x = int(self.field_widget.scene().sceneRect().right()) - self.width_spinbox.value()
                min_y = int(self.field_widget.scene().sceneRect().top())
                max_y = int(self.field_widget.scene().sceneRect().bottom()) - self.height_spinbox.value()
                max_width = int(self.field_widget.scene().sceneRect().right()) - self.x_spinbox.value()
                max_height = int(self.field_widget.scene().sceneRect().bottom()) - self.y_spinbox.value()

            # Обновляем диапазоны для X, Y
            self.x_spinbox.setRange(min_x, max_x)
            self.y_spinbox.setRange(min_y, max_y)
            self.x_slider.setRange(min_x, max_x)
            self.y_slider.setRange(min_y, max_y)
            
            
            min_size = getattr(self, '_step_size', 1) # По умолчанию 1, если атрибут еще не создан
            self.width_spinbox.setRange(min_size, max_width)  
            self.height_spinbox.setRange(min_size, max_height)
            self.width_slider.setRange(min_size, max_width)
            self.height_slider.setRange(min_size, max_height)
            
            logger.debug(f"Установлены диапазоны для X,Y: [{min_x},{max_x}],[{min_y},{max_y}]; W,H: [{min_size},{max_width}],[{min_size},{max_height}]")
        except Exception as e:
            logger.error(f"Ошибка при обновлении диапазонов RegionProperties: {e}")