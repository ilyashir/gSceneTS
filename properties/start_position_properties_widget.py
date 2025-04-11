from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, 
    QSlider, QCheckBox, QGroupBox, QColorDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QIntValidator

from properties.base_properties_widget import BasePropertiesWidget
from properties.utils.grid_snap_utils import (
    is_snap_enabled, snap_to_grid, get_grid_size, snap_rotation_to_grid
)
from utils.signal_utils import SignalBlock
from custom_widgets import CustomSpinBox

import logging

logger = logging.getLogger(__name__)

class StartPositionPropertiesWidget(BasePropertiesWidget):
    """
    Класс для отображения и редактирования свойств стартовой позиции.
    Наследуется от BasePropertiesWidget.
    """
    
    # Сигналы - разделяем на отдельные X и Y
    position_changed = pyqtSignal(int, int)  # x и y
    direction_changed = pyqtSignal(int)  # direction
    
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
        
        # По умолчанию виджет скрыт
        self.hide()
        
        # Добавляем атрибуты для хранения состояния
        self._snap_enabled = True
        self._step_size = 25  # Значение шага по умолчанию для спинбоксов и слайдеров (половина размера сетки)
        self._rotation_step = 45  # Шаг для поворота по умолчанию
    
    def create_widgets(self):
        """Создает виджеты для отображения свойств стартовой позиции."""
        # Идентификатор
        self.id_label = QLabel("ID:")
        self.id_value = QLineEdit("startPosition")
        self.id_value.setReadOnly(True)  # ID всегда фиксирован
        
        # Координаты X
        self.x_label = QLabel("X:")
        self.x_spinbox = CustomSpinBox()
        self.x_spinbox.setRange(-10000, 10000)
        self.x_spinbox.setValue(25)  # Значение по умолчанию
        self.x_spinbox.setSingleStep(1)
        self.x_spinbox.setMinimumWidth(70)
        
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-1000, 1000)
        self.x_slider.setValue(25)  # Значение по умолчанию
        
        # Координаты Y
        self.y_label = QLabel("Y:")
        self.y_spinbox = CustomSpinBox()
        self.y_spinbox.setRange(-10000, 10000)
        self.y_spinbox.setValue(25)  # Значение по умолчанию
        self.y_spinbox.setMinimumWidth(70)
        
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-1000, 1000)
        self.y_slider.setValue(25)  # Значение по умолчанию
        
        # Направление
        self.direction_label = QLabel("Направление:")
        self.direction_spinbox = CustomSpinBox()
        self.direction_spinbox.setRange(0, 360)
        self.direction_spinbox.setValue(0)  # Значение по умолчанию
        self.direction_spinbox.setMinimumWidth(70)
        
        self.direction_slider = QSlider(Qt.Orientation.Horizontal)
        self.direction_slider.setRange(0, 360)
        self.direction_slider.setValue(0)  # Значение по умолчанию
    
        # Кнопка сброса параметров
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_snap_step_size(True)
    
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

        # Кнопка сброса параметров
        main_layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
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
        """Подключение сигналов к слотам."""
        # Связываем слайдеры и спинбоксы
        self.x_spinbox.buttonValueChanged.connect(self.on_x_spinbox_value_changed)
        self.x_slider.valueChanged.connect(self.on_x_slider_value_changed)
        
        self.y_spinbox.buttonValueChanged.connect(self.on_y_spinbox_value_changed)
        self.y_slider.valueChanged.connect(self.on_y_slider_value_changed)
        
        self.direction_spinbox.buttonValueChanged.connect(self.on_direction_spinbox_value_changed)
        self.direction_slider.valueChanged.connect(self.on_direction_slider_value_changed)
        
        # Подключаем сигналы редактирования
        self.x_spinbox.editingFinished.connect(self.on_x_editing_finished)
        self.y_spinbox.editingFinished.connect(self.on_y_editing_finished)
        self.direction_spinbox.editingFinished.connect(self.on_direction_editing_finished)
        
        # Подключаем кнопку сброса
        self.reset_button.clicked.connect(self.reset_properties) 
    
    def update_ranges(self, min_x, max_x, min_y, max_y):
        """
        Обновляет допустимые диапазоны значений для элементов.
        
        Args:
            min_x: Минимальное значение X
            max_x: Максимальное значение X
            min_y: Минимальное значение Y
            max_y: Максимальное значение Y
        """
        try:
            logger.debug(f"Обновление диапазонов стартовой позиции: min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}")
            
            # Обновляем диапазоны спинбоксов
            self.x_spinbox.setRange(min_x, max_x)
            self.y_spinbox.setRange(min_y, max_y)
            
            # Обновляем диапазоны слайдеров
            self.x_slider.setRange(min_x, max_x)
            self.y_slider.setRange(min_y, max_y)
            
            logger.debug(f"Установлены диапазоны X: [{min_x}, {max_x}], Y: [{min_y}, {max_y}] с шагом {self._step_size}, поворот с шагом {self._rotation_step}°")
        except Exception as e:
            logger.error(f"Ошибка при обновлении диапазонов стартовой позиции: {e}")   
    
    def set_properties(self, x, y, direction):
        """
        Устанавливает свойства стартовой позиции (координаты центра).

        Args:
            x: Координата X центра
            y: Координата Y центра
            direction: Направление в градусах
        """
        # Блокируем сигналы на время обновления
        with SignalBlock(self.x_spinbox, self.x_slider,
                        self.y_spinbox, self.y_slider,
                        self.direction_spinbox, self.direction_slider):
            # Устанавливаем значения для спинбоксов и слайдеров
            # Используем переданные координаты центра как есть
            self.x_spinbox.setValue(int(x))
            self.x_slider.setValue(int(x))
            self.y_spinbox.setValue(int(y))
            self.y_slider.setValue(int(y))
            self.direction_spinbox.setValue(int(direction))
            self.direction_slider.setValue(int(direction))

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
            # Диапазоны для КООРДИНАТ ЦЕНТРА
            half_item = start_position.ITEM_SIZE / 2
            min_x = int(scene_rect.left() + half_item)
            max_x = int(scene_rect.right() - half_item)
            min_y = int(scene_rect.top() + half_item)
            max_y = int(scene_rect.bottom() - half_item)
            self.update_ranges(min_x, max_x, min_y, max_y)

        # Получаем координаты ВЕРХНЕГО ЛЕВОГО угла
        item_x = start_position.x()
        item_y = start_position.y()
        # Добавляем смещение для получения КООРДИНАТ ЦЕНТРА
        center_offset = start_position.ITEM_SIZE / 2
        center_x = item_x + center_offset
        center_y = item_y + center_offset

        # Устанавливаем значения свойств (координаты центра)
        self.set_properties(
            int(center_x),
            int(center_y),
            int(start_position.rotation()) # Используем rotation() вместо direction()
        )

        # Отображаем виджет
        self.show()

    def update_properties(self, item):
        """
        Обновляет отображаемые свойства стартовой позиции.

        Args:
            item: Объект стартовой позиции
        """
        try:
            if item is None:
                self.clear_properties()
                return

            # Обновляем диапазоны в первую очередь
            if self.field_widget:
                scene_rect = self.field_widget.scene().sceneRect()
                # Учитываем центр для StartPosition
                half_item = 25 # StartPosition.ITEM_SIZE / 2
                sp_min_x = int(scene_rect.left() + half_item)
                sp_max_x = int(scene_rect.right() - half_item)
                sp_min_y = int(scene_rect.top() + half_item)
                sp_max_y = int(scene_rect.bottom() - half_item)
                self.update_ranges(sp_min_x, sp_max_x, sp_min_y, sp_max_y)

            self.set_properties(
                int(item.x()),
                int(item.y()),
                int(item.rotation())
            )

            logger.debug(f"Свойства стартовой позиции (центр) обновлены в виджете: x={int(center_x)}, y={int(center_y)}, direction={rot_val}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении свойств стартовой позиции: {e}")
    
    def connect_to_field_widget(self, field_widget):
        """
        Установка ссылки на виджет поля.
        """
        self.field_widget = field_widget
        
        logger.debug(f"StartPositionPropertiesWidget подключен к field_widget")
    

    @pyqtSlot(bool)
    def on_grid_snap_changed(self, enabled):
        """
        Обработчик сигнала изменения режима привязки к сетке.
        
        Args:
            enabled: True - привязка включена, False - выключена
        """
        # Просто вызываем метод set_snap_enabled с полученным параметром
        self.set_snap_enabled(enabled)
    
    # Обработчики изменения значений X
    def on_x_spinbox_value_changed(self, value):
        """Обработчик изменения значения X в спинбоксе (кнопками)."""
        try:            
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)
                with SignalBlock(self.x_spinbox):
                    self.x_spinbox.setValue(value) 
                logger.debug(f"Привязка к сетке X: {value} (шаг {self._step_size})")

            # Обновляем слайдер в любом случае для синхронизации
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)

            # Эмитируем сигнал только если значение реально изменилось
            logger.debug(f"Эмитируем position_x_changed({value}) из on_x_spinbox_value_changed.")
            self.position_changed.emit(value, self.y_spinbox.value())

        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты через спинбокс: {e}")

    def on_x_slider_value_changed(self, value):
        """
        Обработчик изменения слайдера X.

        Args:
            value: Новое значение X
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)  
                logger.debug(f"Привязка к сетке X: {value} (шаг {self._step_size})")

            # Устанавливаем значение в спинбокс без эмиссии сигнала, только если изменилось
            with SignalBlock(self.x_spinbox):
                self.x_spinbox.setValue(value)

            # Оповещаем об изменении позиции, только если значение изменилось
            logger.debug(f"Эмитируем position_x_changed({value}) из on_x_slider_value_changed.")
            self.position_changed.emit(value, self.y_spinbox.value())

        except Exception as e:
            logger.error(f"Ошибка при изменении X-координаты слайдером: {e}")

    def on_x_editing_finished(self):
        """Обработчик завершения редактирования X-координаты."""
        try:
            value = self.x_spinbox.value()

            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)  
                logger.debug(f"Привязка к сетке X: {value} (шаг {self._step_size})")

            # Обновляем слайдер в любом случае для синхронизации
            with SignalBlock(self.x_slider):
                self.x_slider.setValue(value)

            logger.debug(f"Эмитируем position_x_changed({value}) из on_x_editing_finished.")
            self.position_changed.emit(value, self.y_spinbox.value())
            
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования X: {e}")

    # Обработчики изменения значений Y
    def on_y_spinbox_value_changed(self, value):
        """Обработчик изменения значения Y в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)  
                with SignalBlock(self.y_spinbox):
                    self.y_spinbox.setValue(value) 
                logger.debug(f"Привязка к сетке Y: {value} (шаг {self._step_size})")

            with SignalBlock(self.y_slider):
                 self.y_slider.setValue(value)

            logger.debug(f"Эмитируем position_y_changed({value}) из on_y_spinbox_value_changed.")
            self.position_changed.emit(self.x_spinbox.value(), value)

        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты через спинбокс: {e}")

    def on_y_slider_value_changed(self, value):
        """
        Обработчик изменения слайдера Y.

        Args:
            value: Новое значение Y
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)  
                logger.debug(f"Привязка к сетке Y: {value} (шаг {self._step_size})")

            with SignalBlock(self.y_spinbox):
                self.y_spinbox.setValue(value)
            
            logger.debug(f"Эмитируем position_y_changed({value}) из on_y_slider_value_changed.")
            self.position_changed.emit(self.x_spinbox.value(), value)
            
        except Exception as e:
            logger.error(f"Ошибка при изменении Y-координаты слайдером: {e}")

    def on_y_editing_finished(self):
        """Обработчик завершения редактирования Y-координаты."""
        try:
            value = self.y_spinbox.value()

            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_to_grid(value, self._step_size)  
                logger.debug(f"Привязка к сетке Y: {value} (шаг {self._step_size})")

            with SignalBlock(self.y_slider):
                self.y_slider.setValue(value)

            logger.debug(f"Эмитируем position_y_changed({value}) из on_y_editing_finished.")
            self.position_changed.emit(self.x_spinbox.value(), value)

        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования Y: {e}")

    # Обработчики изменения значения направления
    def on_direction_spinbox_value_changed(self, value):
        """Обработчик изменения значения направления в спинбоксе (кнопками)."""
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_rotation_to_grid(value, self._rotation_step)  
                with SignalBlock(self.direction_spinbox):
                    self.direction_spinbox.setValue(value) 
                logger.debug(f"Привязка к сетке направления: {value} (шаг {self._rotation_step}°)")

            with SignalBlock(self.direction_slider):
                self.direction_slider.setValue(value)

            # Оповещаем об изменении направления
            self.direction_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при изменении направления через спинбокс: {e}")

    def on_direction_slider_value_changed(self, value):
        """
        Обработчик изменения слайдера направления.
        
        Args:
            value: Новое значение направления
        """
        try:
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_rotation_to_grid(value, self._rotation_step)  
                logger.debug(f"Привязка к сетке направления: {value} (шаг {self._rotation_step}°)")

            # Устанавливаем значение в спинбокс без эмиссии сигнала
            with SignalBlock(self.direction_spinbox):
                self.direction_spinbox.setValue(value)
                
            # Оповещаем об изменении направления
            self.direction_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при изменении направления: {e}")

    def on_direction_editing_finished(self):
        """Обработчик завершения редактирования направления."""
        try:
            value = self.direction_spinbox.value()
  
            # Привязка к сетке если необходимо
            if hasattr(self, '_snap_enabled') and self._snap_enabled:                
                value = snap_rotation_to_grid(value, self._rotation_step)  
                logger.debug(f"Привязка к сетке направления: {value} (шаг {self._rotation_step}°)")

            # Обновляем слайдер
            with SignalBlock(self.direction_slider):
                self.direction_slider.setValue(value)
                
            # Оповещаем об изменении направления
            self.direction_changed.emit(value)
        except Exception as e:
            logger.error(f"Ошибка при завершении редактирования направления: {e}")
    
    def set_theme(self, is_dark_theme):
        """
        Применяет тему оформления к виджету.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.apply_theme(is_dark_theme) 

    def update_snap_step_size(self, enabled):
        """Устанавливает шаг спинбоксов и слайдеров в зависимости от состояния привязки к сетке."""
        try:
            if enabled:
                step_size = 25  # Шаг полсетки для старта
                rotation_step = 45
                logger.debug(f"Установка шага для старта (привязка вкл.): коорд={step_size}, поворот={rotation_step}")
            else:
                step_size = 1
                rotation_step = 1
                logger.debug("Установка шага для старта (привязка выкл.): 1")

            # Сохраняем шаги как атрибуты для возможного использования
            self._step_size = step_size
            self._rotation_step = rotation_step
            logger.debug(f"[USSS] start_position шаг={self._step_size}, поворот={self._rotation_step}")

            # Координаты X, Y
            self.x_spinbox.setSingleStep(step_size)
            self.y_spinbox.setSingleStep(step_size)
            self.x_slider.setSingleStep(step_size)
            self.y_slider.setSingleStep(step_size)

            # Направление
            self.direction_spinbox.setSingleStep(rotation_step)
            self.direction_slider.setSingleStep(rotation_step)

        except Exception as e:
            logger.error(f"Ошибка при установке шага привязки для старта: {e}")

    def set_snap_enabled(self, enabled):
        """
        Установка состояния привязки к сетке.
        
        Args:
            enabled: True для включения привязки, False для отключения
        """
        try:
            logger.debug(f"StartPositionPropertiesWidget: set_snap_enabled вызван с параметром {enabled}")
            if self._snap_enabled != enabled:
                self._snap_enabled = enabled
                self.update_snap_step_size(enabled)
            
        except Exception as e:
            logger.error(f"Ошибка при установке привязки к сетке для стартовой позиции: {e}")