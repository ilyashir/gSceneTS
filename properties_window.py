from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QSpinBox, QDoubleSpinBox,
    QMessageBox, QToolButton, QFormLayout, QColorDialog, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import logging
from robot import Robot
from wall import Wall
from region import Region
from custom_widgets import EditableLineEdit, ColorPickerButton
from styles import AppStyles
from math import degrees, radians

logger = logging.getLogger(__name__)

class PropertiesWindow(QWidget):
    # Сигналы для изменения свойств
    robot_position_changed = pyqtSignal(int, int)  # x, y
    robot_rotation_changed = pyqtSignal(int)  # rotation
    wall_position_point1_changed = pyqtSignal(int, int)  # x1, y1
    wall_position_point2_changed = pyqtSignal(int, int)  # x2, y2
    wall_size_changed = pyqtSignal(int)  # width, height
    region_position_changed = pyqtSignal(int, int)  # x, y
    region_size_changed = pyqtSignal(int, int)  # width, height
    region_color_changed = pyqtSignal(str)  # color
    wall_id_changed = pyqtSignal(str)  # id for walls
    region_id_changed = pyqtSignal(str)  # id for regions
    
    # Константы
    MAX_SLIDER_VALUE = 9999  # Максимальное значение для ползунков
    
    def __init__(self, parent=None, is_dark_theme=True):
        """Инициализация панели свойств."""
        super().__init__(parent)
        self.setWindowTitle("Свойства")
        self.setMinimumWidth(380)
        
        # Инициализация переменных
        self.current_item = None
        self.is_dark_theme = is_dark_theme
        
        # Применяем стиль в зависимости от темы
        self.setStyleSheet(AppStyles.DARK_PROPERTIES_WINDOW if is_dark_theme else AppStyles.LIGHT_PROPERTIES_WINDOW)
        
        # Словарь для хранения исходных значений свойств объектов
        self.initial_values = {}
        
        layout = QVBoxLayout()
        
        # Создаем группу для свойств робота
        self.robot_group = self.create_robot_properties()
        layout.addWidget(self.robot_group)
        
        # Создаем группу для свойств стены
        self.wall_group = self.create_wall_properties()
        layout.addWidget(self.wall_group)
        
        # Создаем группу для свойств региона
        self.region_group = self.create_region_properties()
        layout.addWidget(self.region_group)
        
        # Изначально скрываем все группы
        self.hide_groups()
        
        # Добавляем растягивающийся элемент
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Устанавливаем курсоры для элементов управления
        self.setup_cursors()
    
    def setup_cursors(self):
        """Устанавливает курсоры для всех элементов интерфейса в окне свойств"""
        # Устанавливаем курсоры для всех кнопок
        for button in self.findChildren(QPushButton) + self.findChildren(QToolButton):
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
    
    def create_robot_properties(self):
        group = QGroupBox("Свойства робота")
        layout = QVBoxLayout()
        
        # ID (только для чтения)
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.robot_id = EditableLineEdit()
        self.robot_id.setReadOnly(True)  # Только для чтения
        # Используем цвета фона в зависимости от темы
        bg_color = AppStyles.SECONDARY_DARK if self.is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
        text_color = AppStyles.TEXT_COLOR if self.is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
        border_color = AppStyles.BORDER_COLOR if self.is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        self.robot_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        id_layout.addWidget(self.robot_id)
        layout.addLayout(id_layout)
        
        # Позиция и поворот - используем FormLayout для лучшей организации
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Координата X с ползунком
        x_layout = QHBoxLayout()
        self.robot_x = QSpinBox()
        self.robot_x.setRange(-1000, 1000)
        self.robot_x.valueChanged.connect(lambda x: self.robot_position_changed.emit(x, self.robot_y.value()))
        self.robot_x.setMinimumWidth(70)
        
        # Ползунок для X
        self.robot_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.robot_x_slider.setRange(-1000, 1000)
        self.robot_x_slider.valueChanged.connect(self.robot_x.setValue)
        self.robot_x.valueChanged.connect(self.robot_x_slider.setValue)
        
        x_layout.addWidget(self.robot_x)
        x_layout.addWidget(self.robot_x_slider)
        form_layout.addRow("X:", x_layout)
        
        # Координата Y с ползунком
        y_layout = QHBoxLayout()
        self.robot_y = QSpinBox()
        self.robot_y.setRange(-1000, 1000)
        self.robot_y.valueChanged.connect(lambda y: self.robot_position_changed.emit(self.robot_x.value(), y))
        self.robot_y.setMinimumWidth(70)
        
        # Ползунок для Y
        self.robot_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.robot_y_slider.setRange(-1000, 1000)
        self.robot_y_slider.valueChanged.connect(self.robot_y.setValue)
        self.robot_y.valueChanged.connect(self.robot_y_slider.setValue)
        
        y_layout.addWidget(self.robot_y)
        y_layout.addWidget(self.robot_y_slider)
        form_layout.addRow("Y:", y_layout)
        
        # Поворот с ползунком
        rotation_layout = QHBoxLayout()
        self.robot_rotation = QSpinBox()
        self.robot_rotation.setRange(-180, 180)
        self.robot_rotation.valueChanged.connect(self.robot_rotation_changed.emit)
        self.robot_rotation.setMinimumWidth(70)
        
        # Ползунок для поворота
        self.robot_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.robot_rotation_slider.setRange(-180, 180)
        self.robot_rotation_slider.valueChanged.connect(self.robot_rotation.setValue)
        self.robot_rotation.valueChanged.connect(self.robot_rotation_slider.setValue)
        
        rotation_layout.addWidget(self.robot_rotation)
        rotation_layout.addWidget(self.robot_rotation_slider)
        form_layout.addRow("Поворот:", rotation_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопка сброса параметров
        reset_button = self.create_reset_button(self.reset_robot_properties)
        layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        group.setLayout(layout)
        return group
    
    def create_wall_properties(self):
        group = QGroupBox("Свойства стены")
        layout = QVBoxLayout()
        
        # ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.wall_id = EditableLineEdit()
        self.wall_id.valueChanged.connect(lambda text, obj: self.on_wall_id_changed(text, obj))
        # Используем цвета фона в зависимости от темы
        bg_color = AppStyles.SECONDARY_DARK if self.is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
        text_color = AppStyles.TEXT_COLOR if self.is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
        border_color = AppStyles.BORDER_COLOR if self.is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        self.wall_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        id_layout.addWidget(self.wall_id)
        layout.addLayout(id_layout)
        
        # Используем FormLayout для улучшения организации
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Точка 1
        # X1 с ползунком
        x1_layout = QHBoxLayout()
        self.wall_x1 = QSpinBox()
        self.wall_x1.setRange(-1000, 1000)
        self.wall_x1.valueChanged.connect(lambda x: self.wall_position_point1_changed.emit(x, self.wall_y1.value()))
        self.wall_x1.setMinimumWidth(70)
        
        self.wall_x1_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_x1_slider.setRange(-1000, 1000)
        self.wall_x1_slider.valueChanged.connect(self.wall_x1.setValue)
        self.wall_x1.valueChanged.connect(self.wall_x1_slider.setValue)
        
        x1_layout.addWidget(self.wall_x1)
        x1_layout.addWidget(self.wall_x1_slider)
        
        # Y1 с ползунком
        y1_layout = QHBoxLayout()
        self.wall_y1 = QSpinBox()
        self.wall_y1.setRange(-1000, 1000)
        self.wall_y1.valueChanged.connect(lambda y: self.wall_position_point1_changed.emit(self.wall_x1.value(), y))
        self.wall_y1.setMinimumWidth(70)
        
        self.wall_y1_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_y1_slider.setRange(-1000, 1000)
        self.wall_y1_slider.valueChanged.connect(self.wall_y1.setValue)
        self.wall_y1.valueChanged.connect(self.wall_y1_slider.setValue)
        
        y1_layout.addWidget(self.wall_y1)
        y1_layout.addWidget(self.wall_y1_slider)
        
        # Добавляем точку 1 в форму
        point1_group = QGroupBox("Точка 1")
        point1_layout = QVBoxLayout()
        point1_layout.addLayout(x1_layout)
        point1_layout.addLayout(y1_layout)
        point1_group.setLayout(point1_layout)
        
        # Точка 2
        # X2 с ползунком
        x2_layout = QHBoxLayout()
        self.wall_x2 = QSpinBox()
        self.wall_x2.setRange(-1000, 1000)
        self.wall_x2.valueChanged.connect(lambda x: self.wall_position_point2_changed.emit(x, self.wall_y2.value()))
        self.wall_x2.setMinimumWidth(70)
        
        self.wall_x2_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_x2_slider.setRange(-1000, 1000)
        self.wall_x2_slider.valueChanged.connect(self.wall_x2.setValue)
        self.wall_x2.valueChanged.connect(self.wall_x2_slider.setValue)
        
        x2_layout.addWidget(self.wall_x2)
        x2_layout.addWidget(self.wall_x2_slider)
        
        # Y2 с ползунком
        y2_layout = QHBoxLayout()
        self.wall_y2 = QSpinBox()
        self.wall_y2.setRange(-1000, 1000)
        self.wall_y2.valueChanged.connect(lambda y: self.wall_position_point2_changed.emit(self.wall_x2.value(), y))
        self.wall_y2.setMinimumWidth(70)
        
        self.wall_y2_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_y2_slider.setRange(-1000, 1000)
        self.wall_y2_slider.valueChanged.connect(self.wall_y2.setValue)
        self.wall_y2.valueChanged.connect(self.wall_y2_slider.setValue)
        
        y2_layout.addWidget(self.wall_y2)
        y2_layout.addWidget(self.wall_y2_slider)
        
        # Добавляем точку 2 в форму
        point2_group = QGroupBox("Точка 2")
        point2_layout = QVBoxLayout()
        point2_layout.addLayout(x2_layout)
        point2_layout.addLayout(y2_layout)
        point2_group.setLayout(point2_layout)
        
        # Добавляем группы точек в основной макет
        layout.addWidget(point1_group)
        layout.addWidget(point2_group)
        
        # Толщина стены с ползунком
        width_layout = QHBoxLayout()
        self.wall_width = QSpinBox()
        self.wall_width.setRange(1, 100)
        self.wall_width.valueChanged.connect(self.wall_size_changed.emit)
        self.wall_width.setMinimumWidth(70)
        
        self.wall_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.wall_width_slider.setRange(1, 100)
        self.wall_width_slider.valueChanged.connect(self.wall_width.setValue)
        self.wall_width.valueChanged.connect(self.wall_width_slider.setValue)
        
        width_form = QFormLayout()
        width_form.addRow("Толщина:", width_layout)
        width_layout.addWidget(self.wall_width)
        width_layout.addWidget(self.wall_width_slider)
        layout.addLayout(width_form)
        
        # Кнопка сброса параметров
        reset_button = self.create_reset_button(self.reset_wall_properties)
        layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        group.setLayout(layout)
        return group
    
    def create_region_properties(self):
        group = QGroupBox("Свойства региона")
        layout = QVBoxLayout()
        
        # ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.region_id = EditableLineEdit()
        self.region_id.valueChanged.connect(lambda text, obj: self.on_region_id_changed(text, obj))
        # Используем цвета фона в зависимости от темы
        bg_color = AppStyles.SECONDARY_DARK if self.is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
        text_color = AppStyles.TEXT_COLOR if self.is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
        border_color = AppStyles.BORDER_COLOR if self.is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        self.region_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        id_layout.addWidget(self.region_id)
        layout.addLayout(id_layout)
        
        # Позиция
        pos_form = QFormLayout()
        pos_form.setSpacing(10)
        
        # Координата X с ползунком
        x_layout = QHBoxLayout()
        self.region_x = QSpinBox()
        self.region_x.setRange(-1000, 1000)
        self.region_x.setMinimumWidth(70)
        
        # Ползунок для X
        self.region_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.region_x_slider.setRange(-1000, 1000)
        self.region_x_slider.valueChanged.connect(self.region_x.setValue)
        
        x_layout.addWidget(self.region_x)
        x_layout.addWidget(self.region_x_slider)
        pos_form.addRow("X:", x_layout)
        
        # Координата Y с ползунком
        y_layout = QHBoxLayout()
        self.region_y = QSpinBox()
        self.region_y.setRange(-1000, 1000)
        self.region_y.setMinimumWidth(70)
        
        # Ползунок для Y
        self.region_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.region_y_slider.setRange(-1000, 1000)
        self.region_y_slider.valueChanged.connect(self.region_y.setValue)
        
        y_layout.addWidget(self.region_y)
        y_layout.addWidget(self.region_y_slider)
        pos_form.addRow("Y:", y_layout)
        
        layout.addLayout(pos_form)
        
        # Размер
        size_form = QFormLayout()
        size_form.setSpacing(10)
        
        # Ширина с ползунком
        width_layout = QHBoxLayout()
        self.region_width = QSpinBox()
        self.region_width.setRange(1, 9999)
        self.region_width.setMinimumWidth(70)
        
        # Ползунок для ширины
        self.region_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.region_width_slider.setRange(1, self.MAX_SLIDER_VALUE)
        self.region_width_slider.valueChanged.connect(self.region_width.setValue)
        
        width_layout.addWidget(self.region_width)
        width_layout.addWidget(self.region_width_slider)
        size_form.addRow("Ширина:", width_layout)
        
        # Высота с ползунком
        height_layout = QHBoxLayout()
        self.region_height = QSpinBox()
        self.region_height.setRange(1, 9999)
        self.region_height.setMinimumWidth(70)
        
        # Ползунок для высоты
        self.region_height_slider = QSlider(Qt.Orientation.Horizontal)
        self.region_height_slider.setRange(1, self.MAX_SLIDER_VALUE)
        self.region_height_slider.valueChanged.connect(self.region_height.setValue)
        
        height_layout.addWidget(self.region_height)
        height_layout.addWidget(self.region_height_slider)
        size_form.addRow("Высота:", height_layout)
        
        layout.addLayout(size_form)
        
        # Цвет
        color_layout = QHBoxLayout()
        color_label = QLabel("Цвет:")
        self.region_color_button = ColorPickerButton(color="#800000ff", is_dark_theme=self.is_dark_theme)
        self.region_color_button.colorChanged.connect(self.region_color_changed.emit)
        
        # Для обратной совместимости сохраняем текстовое поле, но скрываем
        self.region_color = EditableLineEdit()
        self.region_color.hide()  # Скрываем старое поле
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.region_color_button)
        layout.addLayout(color_layout)
        
        # Кнопка сброса параметров
        reset_button = self.create_reset_button(self.reset_region_properties)
        layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        group.setLayout(layout)
        return group
    
    def on_wall_id_changed(self, new_id, wall_item):
        """Обработчик изменения ID стены"""
        logger.debug(f"on_wall_id_changed called with new_id: {new_id}, item: {wall_item}")
        
        if not wall_item or not isinstance(wall_item, Wall):
            logger.warning("No wall item passed or item is not a wall")
            return
            
        # Отправляем сигнал на изменение ID
        logger.debug(f"Emitting wall_id_changed signal with ID: {new_id}")
        # Теперь используем только сигнал вместо прямого вызова метода
        self.wall_id_changed.emit(new_id)
    
    def on_region_id_changed(self, new_id, region_item):
        """Обработчик изменения ID региона"""
        logger.debug(f"on_region_id_changed called with new_id: {new_id}, item: {region_item}")
        
        if not region_item or not isinstance(region_item, Region):
            logger.warning("No region item passed or item is not a region")
            return
            
        # Отправляем сигнал на изменение ID
        logger.debug(f"Emitting region_id_changed signal with ID: {new_id}")
        # Теперь используем только сигнал вместо прямого вызова метода
        self.region_id_changed.emit(new_id)
    
    def hide_all_groups(self):
        """Скрывает все группы свойств и сбрасывает текущий элемент."""
        self.robot_group.hide()
        self.wall_group.hide()
        self.region_group.hide()
        self.current_item = None
    
    def hide_groups(self):
        """Скрывает все группы свойств без сброса текущего элемента."""
        self.robot_group.hide()
        self.wall_group.hide()
        self.region_group.hide()
    
    def show_robot_properties(self, x, y, rotation, robot_id):
        """Показывает свойства робота."""
        # Блокируем сигналы
        self.robot_x.blockSignals(True)
        self.robot_y.blockSignals(True)
        self.robot_rotation.blockSignals(True)
        self.robot_x_slider.blockSignals(True)
        self.robot_y_slider.blockSignals(True)
        self.robot_rotation_slider.blockSignals(True)
        
        self.hide_groups()
        self.robot_group.show()
        self.robot_id.setText(str(robot_id))  # Преобразуем robot_id в строку
        
        # Устанавливаем шаг спинбоксов в зависимости от режима привязки к сетке
        self.update_spinbox_step_sizes()
        
        self.robot_x.setValue(x)
        self.robot_y.setValue(y)
        self.robot_rotation.setValue(rotation)
    
        # Устанавливаем значения слайдеров
        self.robot_x_slider.setValue(x)
        self.robot_y_slider.setValue(y)
        self.robot_rotation_slider.setValue(rotation)
        
        # Разблокируем сигналы
        self.robot_x.blockSignals(False)
        self.robot_y.blockSignals(False)
        self.robot_rotation.blockSignals(False)
        self.robot_x_slider.blockSignals(False)
        self.robot_y_slider.blockSignals(False)
        self.robot_rotation_slider.blockSignals(False)
    
    def show_wall_properties(self, x1, y1, x2, y2, width, wall_id):
        """Показывает свойства стены."""
        # Блокируем сигналы
        self.wall_x1.blockSignals(True)
        self.wall_y1.blockSignals(True)
        self.wall_x2.blockSignals(True)
        self.wall_y2.blockSignals(True)
        self.wall_width.blockSignals(True)
        self.wall_x1_slider.blockSignals(True)
        self.wall_y1_slider.blockSignals(True)
        self.wall_x2_slider.blockSignals(True)
        self.wall_y2_slider.blockSignals(True)
        self.wall_width_slider.blockSignals(True)
        
        # Сохраняем локальную ссылку на текущий объект
        wall_item = self.current_item
        logger.debug(f"In show_wall_properties, current_item is: {self.current_item}")
        
        self.hide_groups()
        self.wall_group.show()
        self.wall_id.setText(str(wall_id))  # Преобразуем wall_id в строку
        
        # Связываем объект с полем ID, используя локальную копию
        logger.debug(f"Setting linked object to: {wall_item}")
        self.wall_id.setLinkedObject(wall_item)
        
        # Устанавливаем шаг спинбоксов в зависимости от режима привязки к сетке
        self.update_spinbox_step_sizes()
        
        self.wall_x1.setValue(x1)
        self.wall_y1.setValue(y1)
        self.wall_x2.setValue(x2)
        self.wall_y2.setValue(y2)
        self.wall_width.setValue(width)
        
        # Устанавливаем значения слайдеров
        self.wall_x1_slider.setValue(x1)
        self.wall_y1_slider.setValue(y1)
        self.wall_x2_slider.setValue(x2)
        self.wall_y2_slider.setValue(y2)
        self.wall_width_slider.setValue(width)
        
        # Разблокируем сигналы
        self.wall_x1.blockSignals(False)
        self.wall_y1.blockSignals(False)
        self.wall_x2.blockSignals(False)
        self.wall_y2.blockSignals(False)
        self.wall_width.blockSignals(False)
        self.wall_x1_slider.blockSignals(False)
        self.wall_y1_slider.blockSignals(False)
        self.wall_x2_slider.blockSignals(False)
        self.wall_y2_slider.blockSignals(False)
        self.wall_width_slider.blockSignals(False)
    
    def show_region_properties(self, x, y, width, height, color, region_id):
        """Показывает свойства региона."""
        # Блокируем сигналы
        self.region_x.blockSignals(True)
        self.region_y.blockSignals(True)
        self.region_width.blockSignals(True)
        self.region_height.blockSignals(True)
        self.region_x_slider.blockSignals(True)  # Блокируем слайдеры
        self.region_y_slider.blockSignals(True)
        self.region_width_slider.blockSignals(True)
        self.region_height_slider.blockSignals(True)
        
        # Сохраняем локальную ссылку на текущий объект
        region_item = self.current_item
        logger.debug(f"In show_region_properties, current_item is: {self.current_item}")
        
        self.hide_groups()
        self.region_group.show()
        self.region_id.setText(str(region_id))  # Преобразуем region_id в строку
        
        # Связываем объект с полем ID, используя локальную копию
        logger.debug(f"Setting linked object to: {region_item}")
        self.region_id.setLinkedObject(region_item)
        
        # Сохраняем исходные значения для сброса
        if isinstance(region_item, Region) and region_id not in self.initial_values:
            self.initial_values[region_id] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'color': color
            }
            logger.debug(f"Saved initial values for region {region_id}: {self.initial_values[region_id]}")
        
        # Устанавливаем шаг спинбоксов в зависимости от режима привязки к сетке
        self.update_spinbox_step_sizes()
        
        # Рассчитываем ограничения для ползунков в зависимости от текущего положения и размеров сцены
        self.update_region_ranges(x, y, width, height)
        
        # Безопасно отключаем наши обработчики перед повторным подключением
        try:
            self.region_width_slider.valueChanged.disconnect(self.on_region_width_slider_changed)
            self.region_height_slider.valueChanged.disconnect(self.on_region_height_slider_changed)
            self.region_x.valueChanged.disconnect()
            self.region_y.valueChanged.disconnect()
            self.region_width.editingFinished.disconnect()
            self.region_height.editingFinished.disconnect()
            self.region_x.editingFinished.disconnect()
            self.region_y.editingFinished.disconnect()
        except:
            # Эти соединения могут еще не существовать при первом вызове
            pass
        
        # Добавляем обработчики для изменения размера и позиции региона на сцене
        self.region_width_slider.valueChanged.connect(self.on_region_width_slider_changed)
        self.region_height_slider.valueChanged.connect(self.on_region_height_slider_changed)
        
        # Подключаем сигналы для обработки изменения позиции через слайдеры
        self.region_x_slider.valueChanged.connect(self.on_region_position_x_changed)
        self.region_y_slider.valueChanged.connect(self.on_region_position_y_changed)
        
        # Подключаем сигналы editingFinished для обработки окончания редактирования
        self.region_width.editingFinished.connect(self.on_region_width_editing_finished)
        self.region_height.editingFinished.connect(self.on_region_height_editing_finished)
        self.region_x.editingFinished.connect(self.on_region_position_x_editing_finished)
        self.region_y.editingFinished.connect(self.on_region_position_y_editing_finished)
        
        # Устанавливаем текущие значения в спинбоксы
        self.region_x.setValue(x)
        self.region_y.setValue(y)
        self.region_width.setValue(width)
        self.region_height.setValue(height)
        
        # Устанавливаем значения слайдеров (они уже ограничены диапазоном, установленным выше)
        self.region_x_slider.setValue(x)
        self.region_y_slider.setValue(y)
        self.region_width_slider.setValue(width)
        self.region_height_slider.setValue(height)
        
        # Обновляем цвет кнопки
        self.region_color_button.setColor(color)
        
        # Для обратной совместимости
        self.region_color.setText(color)
        self.region_color.setLinkedObject(region_item)
        
        # Включаем подсветку региона
        if isinstance(region_item, Region):
            region_item.set_highlight(True)
        
        # Разблокируем сигналы
        self.region_x.blockSignals(False)
        self.region_y.blockSignals(False)
        self.region_width.blockSignals(False)
        self.region_height.blockSignals(False)
        self.region_x_slider.blockSignals(False)
        self.region_y_slider.blockSignals(False)
        self.region_width_slider.blockSignals(False)
        self.region_height_slider.blockSignals(False)
    
    def update_region_ranges(self, x, y, width=None, height=None):
        """Обновляет диапазоны для спинбоксов и слайдеров региона."""
        if not self.current_item or not isinstance(self.current_item, Region) or not self.current_item.scene():
            return
            
        scene_rect = self.current_item.scene().sceneRect()
        
        # Если ширина и высота не указаны, используем текущие значения
        if width is None:
            width = self.region_width.value()
        if height is None:
            height = self.region_height.value()
            
        # Ограничения для X
        min_x = int(scene_rect.left())
        max_x = int(scene_rect.right() - width)
        self.region_x.setRange(min_x, max_x)
        self.region_x_slider.setRange(min_x, max_x)
        
        # Ограничения для Y
        min_y = int(scene_rect.top())
        max_y = int(scene_rect.bottom() - height)
        self.region_y.setRange(min_y, max_y)
        self.region_y_slider.setRange(min_y, max_y)
        
        # Ограничения для ширины и высоты
        max_width = int(scene_rect.right() - x)  # Макс. ширина от текущей позиции X до правой границы
        max_height = int(scene_rect.bottom() - y)  # Макс. высота от текущей позиции Y до нижней границы
        logger.debug(f"max_width: {max_width}, max_height: {max_height}")
        
        # Устанавливаем диапазоны для спинбоксов и слайдеров
        self.region_width.setRange(1, max_width)
        self.region_height.setRange(1, max_height)
        
        # Устанавливаем диапазоны для слайдеров с учетом константы
        self.region_width_slider.setRange(1, min(self.MAX_SLIDER_VALUE, max_width))
        self.region_height_slider.setRange(1, min(self.MAX_SLIDER_VALUE, max_height))
    
    def on_region_position_x_changed(self, x):
        """Обработчик изменения позиции X региона."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем значение к сетке
                x = round(x / field_widget.grid_size) * field_widget.grid_size
                # Обновляем слайдер, только если значение отличается
                if x != self.region_x_slider.value():
                    self.region_x_slider.blockSignals(True)
                    self.region_x_slider.setValue(x)
                    self.region_x_slider.blockSignals(False)
                # Обновляем спинбокс
                if x != self.region_x.value():
                    self.region_x.setValue(x)
        
        # Обновляем диапазоны для ширины и высоты
        self.update_region_ranges(x, self.region_y.value())
        
        # Применяем привязку к сетке при необходимости и обновляем позицию
        self.update_region_position_x(x)
    
    def on_region_position_y_changed(self, y):
        """Обработчик изменения позиции Y региона."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем значение к сетке
                y = round(y / field_widget.grid_size) * field_widget.grid_size
                # Обновляем слайдер, только если значение отличается
                if y != self.region_y_slider.value():
                    self.region_y_slider.blockSignals(True)
                    self.region_y_slider.setValue(y)
                    self.region_y_slider.blockSignals(False)
                # Обновляем спинбокс
                if y != self.region_y.value():
                    self.region_y.setValue(y)
        
        # Обновляем диапазоны для ширины и высоты
        self.update_region_ranges(self.region_x.value(), y)
        
        # Применяем привязку к сетке при необходимости и обновляем позицию
        self.update_region_position_y(y)

    def update_properties(self, item):
        """Обновляет свойства в зависимости от выбранного элемента."""
        # Убираем подсветку у предыдущего региона, если был выбран
        if hasattr(self, '_last_region') and self._last_region and self._last_region != item:
            try:
                logger.debug(f"Отключаем подсветку у предыдущего региона: {self._last_region}")
                self._last_region.set_highlight(False)
            except:
                pass
            self._last_region = None
        
        self.current_item = item
        logger.debug(f"Updating properties for item: {item}")
        
        # Скрываем все группы свойств
        self.hide_groups()

        if isinstance(item, Robot):
            pos = item.pos()
            x = int(pos.x())
            y = int(pos.y())
            rotation = int(degrees(item.rotation()))
            self.show_robot_properties(x, y, rotation, item.id)
        elif isinstance(item, Wall):
            line = item.line()
            x1 = int(line.x1())
            y1 = int(line.y1())
            x2 = int(line.x2())
            y2 = int(line.y2())
            pen_width = int(item.pen().width())
            self.show_wall_properties(x1, y1, x2, y2, pen_width, item.id)
        elif isinstance(item, Region):
            rect = item.path().boundingRect()
            x = int(item.pos().x())
            y = int(item.pos().y())
            width = int(rect.width())
            height = int(rect.height())
            
            # Включаем подсветку региона перед показом свойств
            logger.debug(f"Включаем подсветку для региона: {item}")
            item.set_highlight(True)
            
            self.show_region_properties(x, y, width, height, item.color, item.id)
            # Сохраняем ссылку на текущий регион
            self._last_region = item
        else:
            self.clear_properties()

    def clear_properties(self):
        """Очищает все поля свойств."""
        # Убираем подсветку у предыдущего региона, если был выбран
        if hasattr(self, '_last_region') and self._last_region:
            try:
                logger.debug(f"Отключаем подсветку при очистке свойств: {self._last_region}")
                self._last_region.set_highlight(False)
                self._last_region = None
            except:
                pass
                
        self.hide_groups()
    def set_theme(self, is_dark_theme):
        """Устанавливает тему для окна свойств."""
        self.is_dark_theme = is_dark_theme
        
        # Обновляем стиль всего окна свойств
        self.setStyleSheet(AppStyles.DARK_PROPERTIES_WINDOW if is_dark_theme else AppStyles.LIGHT_PROPERTIES_WINDOW)
        
        # Обновляем тему для ColorPickerButton
        if hasattr(self, 'region_color_button'):
            self.region_color_button.set_theme(is_dark_theme)
        
        # Обновляем стили для полей ID
        if hasattr(self, 'robot_id'):
            bg_color = AppStyles.SECONDARY_DARK if is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
            text_color = AppStyles.TEXT_COLOR if is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
            border_color = AppStyles.BORDER_COLOR if is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
            self.robot_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        
        if hasattr(self, 'wall_id'):
            bg_color = AppStyles.SECONDARY_DARK if is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
            text_color = AppStyles.TEXT_COLOR if is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
            border_color = AppStyles.BORDER_COLOR if is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
            self.wall_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        
        if hasattr(self, 'region_id'):
            bg_color = AppStyles.SECONDARY_DARK if is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
            text_color = AppStyles.TEXT_COLOR if is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
            border_color = AppStyles.BORDER_COLOR if is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
            self.region_id.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 3px; padding: 3px;")
        
        # Обновляем тему для других виджетов
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'set_theme'):
                widget.set_theme(is_dark_theme)

    def update_region_size(self, width, height):
        """Обновляет размеры региона."""
        logger.debug(f"[PropertiesWindow] ===== НАЧАЛО update_region_size: width={width}, height={height} =====")
        
        if not self.current_item or not isinstance(self.current_item, Region):
            logger.debug(f"[PropertiesWindow] Нет выбранного региона, выход из update_region_size")
            return
            
        # Применяем привязку к сетке, если она включена
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем размеры к сетке
                width = round(width / field_widget.grid_size) * field_widget.grid_size
                height = round(height / field_widget.grid_size) * field_widget.grid_size
                # Обновляем значения в спинбоксах и слайдерах, если они отличаются
                if width != self.region_width.value():
                    self.region_width.setValue(width)
                    self.region_width_slider.setValue(width)
                if height != self.region_height.value():
                    self.region_height.setValue(height)
                    self.region_height_slider.setValue(height)
            
        logger.debug(f"[PropertiesWindow] Отправляем сигнал region_size_changed ({width}, {height})")
        self.region_size_changed.emit(width, height)
        
        logger.debug(f"[PropertiesWindow] ===== КОНЕЦ update_region_size =====")
    
    def on_region_size_editing_finished(self):
        """Обработчик события завершения редактирования размеров региона."""
        width = self.region_width.value()
        height = self.region_height.value()
        logger.debug(f"[PropertiesWindow] ===== ВЫЗВАН on_region_size_editing_finished: width={width}, height={height} =====")
        
        # Проверяем, изменились ли размеры
        if self.current_item and isinstance(self.current_item, Region):
            current_width = int(self.current_item.path().boundingRect().width())
            current_height = int(self.current_item.path().boundingRect().height())
            
            if width != current_width or height != current_height:
                logger.debug(f"[PropertiesWindow] Размеры изменились: {current_width}x{current_height} -> {width}x{height}")
                # Вызываем метод update_region_size
                self.update_region_size(width, height)
            else:
                logger.debug(f"[PropertiesWindow] Размеры не изменились: {width}x{height}, пропускаем обновление")
        else:
            logger.debug(f"[PropertiesWindow] Нет текущего региона или объект не региона")
    
    def update_region_position_x(self, x):
        """Обновляет X-координату региона."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        # Если привязка к сетке включена и текущий элемент находится в сцене
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Применяем привязку к сетке
                x = round(x / field_widget.grid_size) * field_widget.grid_size
        
        # Получаем актуальное значение Y из спинбокса, а не из текущей позиции региона
        y = self.region_y.value()
        self.region_position_changed.emit(x, y)

    def update_region_position_y(self, y):
        """Обновляет Y-координату региона."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        # Если привязка к сетке включена и текущий элемент находится в сцене
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Применяем привязку к сетке
                y = round(y / field_widget.grid_size) * field_widget.grid_size
        
        # Получаем актуальное значение X из спинбокса, а не из текущей позиции региона
        x = self.region_x.value()
        self.region_position_changed.emit(x, y)

    def create_reset_button(self, callback):
        """Создает кнопку для сброса значений свойств"""
        reset_button = QPushButton("Сбросить")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyles.ERROR_COLOR};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FF3333;
            }}
        """)
        reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_button.clicked.connect(callback)
        return reset_button

    def reset_robot_properties(self):
        """Сбрасывает свойства робота в начальное положение"""
        if not self.current_item or not isinstance(self.current_item, Robot):
            return
        
        # Сохраняем ID
        robot_id = self.robot_id.text()
        
        # Сбрасываем позицию и поворот
        self.robot_position_changed.emit(0, 0)
        self.robot_rotation_changed.emit(0)
        
        # Обновляем отображение в окне свойств
        self.show_robot_properties(0, 0, 0, robot_id)
        
        # Показываем уведомление
        QMessageBox.information(self, "Сброс свойств", "Свойства робота сброшены к начальным значениям")
    def reset_wall_properties(self):
        """Сбрасывает свойства стены в начальное положение"""
        if not self.current_item or not isinstance(self.current_item, Wall):
            return
        
        # Сохраняем ID
        wall_id = self.wall_id.text()
        
        # Получаем текущую позицию стены
        line = self.current_item.line()
        x1 = int(line.x1())
        y1 = int(line.y1())
        
        # Сбрасываем на стену размером 100x5
        self.wall_position_point1_changed.emit(x1, y1)
        self.wall_position_point2_changed.emit(x1 + 100, y1)
        self.wall_size_changed.emit(5)
        
        # Обновляем отображение в окне свойств
        self.show_wall_properties(x1, y1, x1 + 100, y1, 5, wall_id)
        
        # Показываем уведомление
        QMessageBox.information(self, "Сброс свойств", "Свойства стены частично сброшены")

    def reset_region_properties(self):
        """Сбрасывает свойства региона в исходное положение"""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        # Сохраняем ID
        region_id = self.current_item.id
        
        # Проверяем, есть ли сохраненные исходные значения
        if region_id in self.initial_values:
            # Получаем исходные значения
            initial = self.initial_values[region_id]
            
            # Сохраняем ссылку на текущий элемент
            current_item = self.current_item
            
            # Изменяем размер и позицию через эмиссию сигналов
            logger.debug(f"Сбрасываем размер региона на ({initial['width']}, {initial['height']})")
            self.region_size_changed.emit(initial['width'], initial['height'])
            
            logger.debug(f"Сбрасываем позицию региона на ({initial['x']}, {initial['y']})")
            self.region_position_changed.emit(initial['x'], initial['y'])
            
            logger.debug(f"Сбрасываем цвет региона на {initial['color']}")
            self.region_color_changed.emit(initial['color'])
            
            # Обновляем отображение в окне свойств
            # Используем временную блокировку сигналов только для UI-элементов
            self.region_width.blockSignals(True)
            self.region_height.blockSignals(True)
            self.region_x.blockSignals(True)
            self.region_y.blockSignals(True)
            self.region_width_slider.blockSignals(True)
            self.region_height_slider.blockSignals(True)
            self.region_x_slider.blockSignals(True)
            self.region_y_slider.blockSignals(True)
            
            # Обновляем значения в UI
            self.region_width.setValue(initial['width'])
            self.region_height.setValue(initial['height'])
            self.region_x.setValue(initial['x'])
            self.region_y.setValue(initial['y'])
            
            # Обновляем значения слайдеров
            self.region_width_slider.setValue(initial['width'])
            self.region_height_slider.setValue(initial['height'])
            self.region_x_slider.setValue(initial['x'])
            self.region_y_slider.setValue(initial['y'])
            
            # Обновляем цвет кнопки и поля
            self.region_color_button.setColor(initial['color'])
            self.region_color.setText(initial['color'])
            
            # Разблокируем сигналы UI-элементов
            self.region_width.blockSignals(False)
            self.region_height.blockSignals(False)
            self.region_x.blockSignals(False)
            self.region_y.blockSignals(False)
            self.region_width_slider.blockSignals(False)
            self.region_height_slider.blockSignals(False)
            self.region_x_slider.blockSignals(False)
            self.region_y_slider.blockSignals(False)
            
            # Обновляем диапазоны для спинбоксов и слайдеров
            self.update_region_ranges(initial['x'], initial['y'], initial['width'], initial['height'])
            
            # Показываем уведомление
            QMessageBox.information(self, "Сброс свойств", "Свойства региона сброшены к исходным значениям")
        else:
            # Получаем текущую позицию региона
            pos = self.current_item.pos()
            x = int(pos.x())
            y = int(pos.y())
            
            # Сбрасываем размер региона на 100x100
            logger.debug(f"Сбрасываем размер региона на (100, 100)")
            self.region_size_changed.emit(100, 100)
            
            # Сбрасываем цвет региона на значение по умолчанию
            logger.debug(f"Сбрасываем цвет региона на #800000ff")
            self.region_color_changed.emit("#800000ff")  # Голубой с прозрачностью
            
            # Обновляем отображение в окне свойств
            # Используем временную блокировку сигналов только для UI-элементов
            self.region_width.blockSignals(True)
            self.region_height.blockSignals(True)
            self.region_x.blockSignals(True)
            self.region_y.blockSignals(True)
            self.region_width_slider.blockSignals(True)
            self.region_height_slider.blockSignals(True)
            self.region_x_slider.blockSignals(True)
            self.region_y_slider.blockSignals(True)
            
            # Обновляем значения в UI
            self.region_width.setValue(100)
            self.region_height.setValue(100)
            
            # Обновляем значения слайдеров
            self.region_width_slider.setValue(100)
            self.region_height_slider.setValue(100)
            
            # Обновляем цвет кнопки и поля
            self.region_color_button.setColor("#800000ff")
            self.region_color.setText("#800000ff")
            
            # Разблокируем сигналы UI-элементов
            self.region_width.blockSignals(False)
            self.region_height.blockSignals(False)
            self.region_x.blockSignals(False)
            self.region_y.blockSignals(False)
            self.region_width_slider.blockSignals(False)
            self.region_height_slider.blockSignals(False)
            self.region_x_slider.blockSignals(False)
            self.region_y_slider.blockSignals(False)
            
            # Обновляем диапазоны для спинбоксов и слайдеров
            self.update_region_ranges(x, y, 100, 100)
            
            # Показываем уведомление
            QMessageBox.information(self, "Сброс свойств", "Свойства региона сброшены к значениям по умолчанию")

    def on_region_width_editing_finished(self):
        """Обработчик окончания редактирования ширины региона через QSpinBox."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
            
        width = self.region_width.value()
        height = self.region_height.value()
        logger.debug(f"[PropertiesWindow] Завершено редактирование ширины: {width}x{height}")
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем размер к сетке
                width = round(width / field_widget.grid_size) * field_widget.grid_size
                if width != self.region_width.value():
                    self.region_width.setValue(width)
        
        # Обновляем диапазоны
        self.update_region_ranges(self.region_x.value(), self.region_y.value())
        
        # Обновляем значение слайдера
        self.region_width_slider.setValue(width)
        
        # Обновляем размер региона
        self.update_region_size(width, height)
    
    def on_region_height_editing_finished(self):
        """Обработчик окончания редактирования высоты региона через QSpinBox."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
            
        width = self.region_width.value()
        height = self.region_height.value()
        logger.debug(f"[PropertiesWindow] Завершено редактирование высоты: {width}x{height}")
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем размер к сетке
                height = round(height / field_widget.grid_size) * field_widget.grid_size
                if height != self.region_height.value():
                    self.region_height.setValue(height)
        
        # Обновляем диапазоны
        self.update_region_ranges(self.region_x.value(), self.region_y.value())
        
        # Обновляем значение слайдера
        self.region_height_slider.setValue(height)
        
        # Обновляем размер региона
        self.update_region_size(width, height)

    def on_region_width_slider_changed(self, value):
        """Обработчик изменения ширины региона через ползунок."""
        if self.current_item and isinstance(self.current_item, Region):
            # Получаем значение высоты из соответствующего спинбокса
            height = self.region_height.value()
            logger.debug(f"[PropertiesWindow] Изменение ширины через ползунок: {value}x{height}")
            
            # Проверяем привязку к сетке
            if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
                field_widget = self.current_item.scene().parent()
                if field_widget.snap_to_grid_enabled:
                    # Привязываем значение к сетке
                    value = round(value / field_widget.grid_size) * field_widget.grid_size
                    # Обновляем слайдер, только если значение отличается
                    if value != self.region_width_slider.value():
                        self.region_width_slider.blockSignals(True)
                        self.region_width_slider.setValue(value)
                        self.region_width_slider.blockSignals(False)
                    # Обновляем спинбокс
                    if value != self.region_width.value():
                        self.region_width.setValue(value)
            
            # Обновляем диапазоны
            self.update_region_ranges(self.region_x.value(), self.region_y.value(), value, height)
            
            # Вызываем обновление размера региона
            self.update_region_size(value, height)
    
    def on_region_height_slider_changed(self, value):
        """Обработчик изменения высоты региона через ползунок."""
        if self.current_item and isinstance(self.current_item, Region):
            # Получаем значение ширины из соответствующего спинбокса
            width = self.region_width.value()
            logger.debug(f"[PropertiesWindow] Изменение высоты через ползунок: {width}x{value}")
            
            # Проверяем привязку к сетке
            if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
                field_widget = self.current_item.scene().parent()
                if field_widget.snap_to_grid_enabled:
                    # Привязываем значение к сетке
                    value = round(value / field_widget.grid_size) * field_widget.grid_size
                    # Обновляем слайдер, только если значение отличается
                    if value != self.region_height_slider.value():
                        self.region_height_slider.blockSignals(True)
                        self.region_height_slider.setValue(value)
                        self.region_height_slider.blockSignals(False)
                    # Обновляем спинбокс
                    if value != self.region_height.value():
                        self.region_height.setValue(value)
            
            # Обновляем диапазоны
            self.update_region_ranges(self.region_x.value(), self.region_y.value(), width, value)
            
            # Вызываем обновление размера региона
            self.update_region_size(width, value)

    def on_region_position_x_editing_finished(self):
        """Обработчик окончания редактирования X-координаты региона через QSpinBox."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        x = self.region_x.value()
        y = self.region_y.value()
        logger.debug(f"[PropertiesWindow] Завершено редактирование X-координаты: {x}x{y}")
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем координату к сетке
                x = round(x / field_widget.grid_size) * field_widget.grid_size
                if x != self.region_x.value():
                    self.region_x.setValue(x)
        
        # Обновляем диапазоны
        self.update_region_ranges(x, y)
        
        # Обновляем значение слайдера
        self.region_x_slider.setValue(x)
        
        # Отправляем сигнал об изменении позиции
        self.region_position_changed.emit(x, y)

    def on_region_position_y_editing_finished(self):
        """Обработчик окончания редактирования Y-координаты региона через QSpinBox."""
        if not self.current_item or not isinstance(self.current_item, Region):
            return
        
        x = self.region_x.value()
        y = self.region_y.value()
        logger.debug(f"[PropertiesWindow] Завершено редактирование Y-координаты: {x}x{y}")
        
        # Проверяем привязку к сетке
        if self.current_item.scene() and hasattr(self.current_item.scene().parent(), 'snap_to_grid_enabled'):
            field_widget = self.current_item.scene().parent()
            if field_widget.snap_to_grid_enabled:
                # Привязываем координату к сетке
                y = round(y / field_widget.grid_size) * field_widget.grid_size
                if y != self.region_y.value():
                    self.region_y.setValue(y)
        
        # Обновляем диапазоны
        self.update_region_ranges(x, y)
        
        # Обновляем значение слайдера
        self.region_y_slider.setValue(y)
        
        # Отправляем сигнал об изменении позиции
        self.region_position_changed.emit(x, y)
    def update_spinbox_step_sizes(self):
        """Обновляет шаг спинбоксов в зависимости от режима привязки к сетке."""
        if not self.current_item or not (isinstance(self.current_item, Region) or isinstance(self.current_item, Wall) or isinstance(self.current_item, Robot)):
            logger.debug(f"Нет выбранного элемента, или элемент не поддерживает привязку к сетке")
            return
            
        # Проверяем, есть ли сцена у текущего элемента
        if not self.current_item.scene():
            logger.debug(f"У текущего элемента нет сцены")
            return
            
        # Получаем FieldWidget
        field_widget = self.current_item.scene().parent()
        if not hasattr(field_widget, 'snap_to_grid_enabled'):
            logger.debug(f"FieldWidget не имеет атрибута snap_to_grid_enabled")
            return
            
        # Получаем размер сетки и состояние привязки
        grid_size = field_widget.grid_size
        snap_enabled = field_widget.snap_to_grid_enabled
        
        # Устанавливаем шаг спинбоксов в зависимости от режима привязки
        step = grid_size if snap_enabled else 1
        logger.debug(f"Устанавливаем шаг спинбоксов: {step} (snap_enabled={snap_enabled}, grid_size={grid_size})")
        
        # Обновляем шаг для всех спинбоксов в зависимости от типа текущего элемента
        if isinstance(self.current_item, Region):
            self.region_x.setSingleStep(step)
            self.region_y.setSingleStep(step)
            self.region_width.setSingleStep(step)
            self.region_height.setSingleStep(step)
        elif isinstance(self.current_item, Wall):
            self.wall_x1.setSingleStep(step)
            self.wall_y1.setSingleStep(step)
            self.wall_x2.setSingleStep(step)
            self.wall_y2.setSingleStep(step)
        elif isinstance(self.current_item, Robot):
            self.robot_x.setSingleStep(step)
            self.robot_y.setSingleStep(step)

    def connect_to_field_widget(self, field_widget):
        """Подключает окно свойств к сигналам FieldWidget."""
        if hasattr(field_widget, 'grid_snap_changed'):
            logger.debug(f"Подключаем сигнал grid_snap_changed от FieldWidget к PropertiesWindow")
            field_widget.grid_snap_changed.connect(self.on_grid_snap_changed)
        else:
            logger.warning(f"FieldWidget не имеет сигнала grid_snap_changed")
    
    def on_grid_snap_changed(self, enabled):
        """Обрабатывает изменение режима привязки к сетке."""
        logger.debug(f"Получен сигнал grid_snap_changed: enabled={enabled}")
        self.update_spinbox_step_sizes()


