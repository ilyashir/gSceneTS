from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from robot import Robot
from wall import Wall
from region import Region

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
    
    def create_robot_properties(self):
        group = QGroupBox("Свойства робота")
        layout = QVBoxLayout()
        
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
        self.region_color = QLineEdit()
        self.region_color.textChanged.connect(self.region_color_changed.emit)
        color_layout.addWidget(self.region_color)
        layout.addLayout(color_layout)
        
        group.setLayout(layout)
        return group
    
    def hide_all_groups(self):
        """Скрывает все группы свойств."""
        self.robot_group.hide()
        self.wall_group.hide()
        self.region_group.hide()
    
    def show_robot_properties(self, x, y, rotation):
        """Показывает свойства робота."""
        self.hide_all_groups()
        self.robot_group.show()
        self.robot_x.setValue(x)
        self.robot_y.setValue(y)
        self.robot_rotation.setValue(rotation)
    
    def show_wall_properties(self, x1, y1, x2, y2, width):
        """Показывает свойства стены."""
        self.hide_all_groups()
        self.wall_group.show()
        self.wall_x1.setValue(x1)
        self.wall_y1.setValue(y1)
        self.wall_x2.setValue(x2)
        self.wall_y2.setValue(y2)
        self.wall_width.setValue(width)
    
    def show_region_properties(self, x, y, width, height, color):
        """Показывает свойства региона."""
        self.hide_all_groups()
        self.region_group.show()
        self.region_x.setValue(x)
        self.region_y.setValue(y)
        self.region_width.setValue(width)
        self.region_height.setValue(height)
        self.region_color.setText(color)

    def update_properties(self, item):
        """Обновляет свойства в зависимости от выбранного элемента."""
        if item is None:
            self.hide_all_groups()
            return
            
        if isinstance(item, Robot):
            pos = item.pos()
            self.show_robot_properties(
                int(pos.x()),
                int(pos.y()),
                int(item.rotation())
            )
        elif isinstance(item, Wall):
            line = item.line()
            self.show_wall_properties(
                int(line.x1()),
                int(line.y1()),
                int(line.x2()),
                int(line.y2()),
                item.pen().width()
            )
        elif isinstance(item, Region):
            rect = item.rect()
            pos = item.pos()
            self.show_region_properties(
                int(pos.x()),
                int(pos.y()),
                int(rect.width()),
                int(rect.height()),
                item.color
            )

    def clear_properties(self):
        """Очищает все свойства."""
        self.hide_all_groups()
        
        # Сбрасываем значения всех полей
        self.robot_x.setValue(0)
        self.robot_y.setValue(0)
        self.robot_rotation.setValue(0)
        
        self.wall_x1.setValue(0)
        self.wall_y1.setValue(0)
        self.wall_x2.setValue(0)
        self.wall_y2.setValue(0)
        self.wall_width.setValue(1)
        
        self.region_x.setValue(0)
        self.region_y.setValue(0)
        self.region_width.setValue(1)
        self.region_height.setValue(1)
        self.region_color.setText("")