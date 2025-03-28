from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QSpinBox, QDoubleSpinBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from robot import Robot
from wall import Wall
from region import Region
from custom_widgets import EditableLineEdit

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства")
        self.setMinimumWidth(320)
        
        # Создаем основной layout
        layout = QVBoxLayout()
        
        # Создаем группы свойств
        self.robot_group = self.create_robot_properties()
        self.wall_group = self.create_wall_properties()
        self.region_group = self.create_region_properties()
        
        # Добавляем группы в layout
        layout.addWidget(self.robot_group)
        layout.addWidget(self.wall_group)
        layout.addWidget(self.region_group)
        
        # Добавляем растяжку в конец
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Скрываем группы по умолчанию
        self.hide_all_groups()
        
        # Текущий выбранный элемент
        self.current_item = None
    
    def create_robot_properties(self):
        group = QGroupBox("Свойства робота")
        layout = QVBoxLayout()
        
        # ID (только для чтения)
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID:"))
        self.robot_id = EditableLineEdit()
        self.robot_id.setReadOnly(True)  # Только для чтения
        self.robot_id.setStyleSheet("background-color: #f0f0f0;")  # Серый фон для визуального отличия
        id_layout.addWidget(self.robot_id)
        layout.addLayout(id_layout)
        
        # Позиция
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.robot_x = QSpinBox()
        self.robot_x.setRange(-1000, 1000)
        self.robot_x.valueChanged.connect(lambda x: self.robot_position_changed.emit(x, self.robot_y.value()))
        pos_layout.addWidget(self.robot_x)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.robot_y = QSpinBox()
        self.robot_y.setRange(-1000, 1000)
        self.robot_y.valueChanged.connect(lambda y: self.robot_position_changed.emit(self.robot_x.value(), y))
        pos_layout.addWidget(self.robot_y)
        layout.addLayout(pos_layout)
        
        # Поворот
        rot_layout = QHBoxLayout()
        rot_layout.addWidget(QLabel("Поворот:"))
        self.robot_rotation = QSpinBox()
        self.robot_rotation.setRange(-180, 180)
        self.robot_rotation.valueChanged.connect(self.robot_rotation_changed.emit)
        rot_layout.addWidget(self.robot_rotation)
        layout.addLayout(rot_layout)
        
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
        id_layout.addWidget(self.wall_id)
        layout.addLayout(id_layout)
        
        # Точка 1
        point1_layout = QHBoxLayout()
        point1_layout.addWidget(QLabel("Точка 1:"))
        point1_layout.addWidget(QLabel("X:"))
        self.wall_x1 = QSpinBox()
        self.wall_x1.setRange(-1000, 1000)
        self.wall_x1.valueChanged.connect(lambda x: self.wall_position_point1_changed.emit(x, self.wall_y1.value()))
        point1_layout.addWidget(self.wall_x1)
        
        point1_layout.addWidget(QLabel("Y:"))
        self.wall_y1 = QSpinBox()
        self.wall_y1.setRange(-1000, 1000)
        self.wall_y1.valueChanged.connect(lambda y: self.wall_position_point1_changed.emit(self.wall_x1.value(), y))
        point1_layout.addWidget(self.wall_y1)
        layout.addLayout(point1_layout)
        
        # Точка 2
        point2_layout = QHBoxLayout()
        point2_layout.addWidget(QLabel("Точка 2:"))
        point2_layout.addWidget(QLabel("X:"))
        self.wall_x2 = QSpinBox()
        self.wall_x2.setRange(-1000, 1000)
        self.wall_x2.valueChanged.connect(lambda x: self.wall_position_point2_changed.emit(x, self.wall_y2.value()))
        point2_layout.addWidget(self.wall_x2)
        
        point2_layout.addWidget(QLabel("Y:"))
        self.wall_y2 = QSpinBox()
        self.wall_y2.setRange(-1000, 1000)
        self.wall_y2.valueChanged.connect(lambda y: self.wall_position_point2_changed.emit(self.wall_x2.value(), y))
        point2_layout.addWidget(self.wall_y2)
        layout.addLayout(point2_layout)
        
        # Толщина
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Толщина:"))
        self.wall_width = QSpinBox()
        self.wall_width.setRange(1, 100)
        self.wall_width.valueChanged.connect(self.wall_size_changed.emit)
        width_layout.addWidget(self.wall_width)
        layout.addLayout(width_layout)
        
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
        id_layout.addWidget(self.region_id)
        layout.addLayout(id_layout)
        
        # Позиция
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.region_x = QSpinBox()
        self.region_x.setRange(-1000, 1000)
        self.region_x.valueChanged.connect(lambda x: self.region_position_changed.emit(x, self.region_y.value()))
        pos_layout.addWidget(self.region_x)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.region_y = QSpinBox()
        self.region_y.setRange(-1000, 1000)
        self.region_y.valueChanged.connect(lambda y: self.region_position_changed.emit(self.region_x.value(), y))
        pos_layout.addWidget(self.region_y)
        layout.addLayout(pos_layout)
        
        # Размер
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Ширина:"))
        self.region_width = QSpinBox()
        self.region_width.setRange(1, 1000)
        self.region_width.valueChanged.connect(lambda w: self.region_size_changed.emit(w, self.region_height.value()))
        size_layout.addWidget(self.region_width)
        
        size_layout.addWidget(QLabel("Высота:"))
        self.region_height = QSpinBox()
        self.region_height.setRange(1, 1000)
        self.region_height.valueChanged.connect(lambda h: self.region_size_changed.emit(self.region_width.value(), h))
        size_layout.addWidget(self.region_height)
        layout.addLayout(size_layout)
        
        # Цвет
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет:"))
        self.region_color = EditableLineEdit()
        self.region_color.valueChanged.connect(lambda text, obj: self.region_color_changed.emit(text))
        color_layout.addWidget(self.region_color)
        layout.addLayout(color_layout)
        
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
    
    def show_duplicate_id_warning(self, id_value):
        """Показывает предупреждение о дублировании ID"""
        QMessageBox.warning(
            self,
            "Ошибка",
            f"ID '{id_value}' уже используется. Пожалуйста, выберите другой ID.",
            QMessageBox.StandardButton.Ok
        )
    
    def get_walls_from_parent(self):
        """Получает список всех стен из родительского виджета"""
        if hasattr(self.parent(), 'walls'):
            return self.parent().walls
        return []
    
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
        self.hide_groups()
        self.robot_group.show()
        self.robot_id.setText(robot_id)
        self.robot_x.setValue(x)
        self.robot_y.setValue(y)
        self.robot_rotation.setValue(rotation)
    
    def show_wall_properties(self, x1, y1, x2, y2, width, wall_id):
        """Показывает свойства стены."""
        # Блокируем сигналы
        self.wall_x1.blockSignals(True)
        self.wall_y1.blockSignals(True)
        self.wall_x2.blockSignals(True)
        self.wall_y2.blockSignals(True)
        self.wall_width.blockSignals(True)
        
        # Сохраняем локальную ссылку на текущий объект
        wall_item = self.current_item
        logger.debug(f"In show_wall_properties, current_item is: {self.current_item}")
        
        self.hide_groups()
        self.wall_group.show()
        self.wall_id.setText(wall_id)
        
        # Связываем объект с полем ID, используя локальную копию
        logger.debug(f"Setting linked object to: {wall_item}")
        self.wall_id.setLinkedObject(wall_item)
        
        self.wall_x1.setValue(x1)
        self.wall_y1.setValue(y1)
        self.wall_x2.setValue(x2)
        self.wall_y2.setValue(y2)
        self.wall_width.setValue(width)
        
        # Разблокируем сигналы
        self.wall_x1.blockSignals(False)
        self.wall_y1.blockSignals(False)
        self.wall_x2.blockSignals(False)
        self.wall_y2.blockSignals(False)
        self.wall_width.blockSignals(False)
    
    def show_region_properties(self, x, y, width, height, color, region_id):
        """Показывает свойства региона."""
        # Блокируем сигналы
        self.region_x.blockSignals(True)
        self.region_y.blockSignals(True)
        self.region_width.blockSignals(True)
        self.region_height.blockSignals(True)
        
        # Сохраняем локальную ссылку на текущий объект
        region_item = self.current_item
        logger.debug(f"In show_region_properties, current_item is: {self.current_item}")
        
        self.hide_groups()
        self.region_group.show()
        self.region_id.setText(region_id)
        
        # Связываем объект с полем ID, используя локальную копию
        logger.debug(f"Setting linked object to: {region_item}")
        self.region_id.setLinkedObject(region_item)
        
        self.region_x.setValue(x)
        self.region_y.setValue(y)
        self.region_width.setValue(width)
        self.region_height.setValue(height)
        self.region_color.setText(color)
        
        # Связываем объект с полем цвета
        self.region_color.setLinkedObject(region_item)
        
        # Разблокируем сигналы
        self.region_x.blockSignals(False)
        self.region_y.blockSignals(False)
        self.region_width.blockSignals(False)
        self.region_height.blockSignals(False)

    def update_properties(self, item):
        """Обновляет свойства в зависимости от выбранного элемента."""
        if item is None:
            self.hide_all_groups()
            return

        logger.debug(f"update_properties called with item: {item}")
        self.current_item = item
        logger.debug(f"self.current_item set to: {self.current_item}")

        if isinstance(item, Robot):
            pos = item.pos()
            self.show_robot_properties(
                int(pos.x()),
                int(pos.y()),
                int(item.rotation()),
                item.id
            )

        elif isinstance(item, Wall):
            line = item.line()
            logger.debug(f"Calling show_wall_properties for item: {item}")
            self.show_wall_properties(
                int(line.x1()),
                int(line.y1()),
                int(line.x2()),
                int(line.y2()),
                item.stroke_width,
                item.id
            )

        elif isinstance(item, Region):
            rect = item.rect()
            pos = item.pos()
            logger.debug(f"Calling show_region_properties for item: {item}")
            self.show_region_properties(
                int(pos.x()),
                int(pos.y()),
                int(rect.width()),
                int(rect.height()),
                item.color,
                item.id
            )

    def clear_properties(self):
        """Очищает все поля свойств."""
        self.hide_all_groups()