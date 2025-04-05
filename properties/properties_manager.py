"""
Менеджер свойств объектов.

Предоставляет централизованный интерфейс для управления свойствами
различных объектов (робот, стена, регион).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLayout
from PyQt6.QtCore import Qt, pyqtSignal
import logging

from robot import Robot
from wall import Wall
from region import Region

from properties.robot_properties_widget import RobotPropertiesWidget
from properties.wall_properties_widget import WallPropertiesWidget
from properties.region_properties_widget import RegionPropertiesWidget

logger = logging.getLogger(__name__)

class PropertiesManager(QWidget):
    """
    Менеджер свойств объектов.
    
    Управляет отображением и изменением свойств различных объектов 
    (робот, стена, регион) через соответствующие виджеты.
    """
    # Сигналы для изменения свойств робота
    robot_position_changed = pyqtSignal(int, int)  # x, y
    robot_rotation_changed = pyqtSignal(int)  # rotation

    # Сигналы для изменения свойств стены
    wall_position_point1_changed = pyqtSignal(int, int)  # x1, y1
    wall_position_point2_changed = pyqtSignal(int, int)  # x2, y2
    wall_width_changed = pyqtSignal(int)  # width
    wall_id_changed = pyqtSignal(str)  # id

    # Сигналы для изменения свойств региона
    region_position_changed = pyqtSignal(int, int)  # x, y
    region_size_changed = pyqtSignal(int, int)  # width, height
    region_color_changed = pyqtSignal(str)  # color
    region_id_changed = pyqtSignal(str)  # id
    
    def __init__(self, parent=None, is_dark_theme=True):
        """
        Инициализация менеджера свойств.
        
        Args:
            parent: Родительский виджет
            is_dark_theme: Флаг темной темы
        """
        super().__init__(parent)
        self.is_dark_theme = is_dark_theme
        
        # Создаем и настраиваем виджеты свойств
        self._setup_widgets()
        
        # Создаем и настраиваем layout
        self._setup_layout()
        
        # Текущий виджет свойств
        self.current_widget = None
        
        # Ссылка на field_widget для проверки привязки к сетке
        self.field_widget = None
        
    def _setup_widgets(self):
        """Создание и настройка виджетов свойств."""
        # Создаем виджеты свойств
        self.robot_widget = RobotPropertiesWidget(self, self.is_dark_theme)
        self.wall_widget = WallPropertiesWidget(self, self.is_dark_theme)
        self.region_widget = RegionPropertiesWidget(self, self.is_dark_theme)
        
        # Скрываем все виджеты по умолчанию
        self.robot_widget.hide()
        self.wall_widget.hide()
        self.region_widget.hide()
        
        # Подключаем сигналы от виджетов свойств
        self._connect_signals()
        
    def _setup_layout(self):
        """Создание и настройка компоновки."""
        # Создаем scroll area для возможности прокрутки, если свойств много
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Создаем контейнер для виджетов свойств
        container = QWidget(scroll_area)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        
        # Добавляем виджеты свойств в контейнер
        layout.addWidget(self.robot_widget)
        layout.addWidget(self.wall_widget)
        layout.addWidget(self.region_widget)
        
        # Добавляем растягивающийся элемент в конец
        layout.addStretch()
        
        # Устанавливаем контейнер как виджет для прокрутки
        scroll_area.setWidget(container)
        
        # Создаем основной layout и добавляем в него scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
    def _connect_signals(self):
        """Подключение сигналов от виджетов свойств."""
        # Робот
        self.robot_widget.position_changed.connect(self.robot_position_changed)
        self.robot_widget.rotation_changed.connect(self.robot_rotation_changed)
        
        # Стена
        self.wall_widget.position_point1_changed.connect(self.wall_position_point1_changed)
        self.wall_widget.position_point2_changed.connect(self.wall_position_point2_changed)
        self.wall_widget.width_changed.connect(self.wall_width_changed)
        self.wall_widget.id_changed.connect(self.wall_id_changed)
        
        # Регион
        self.region_widget.position_changed.connect(self.region_position_changed)
        self.region_widget.size_changed.connect(self.region_size_changed)
        self.region_widget.color_changed.connect(self.region_color_changed)
        self.region_widget.id_changed.connect(self.region_id_changed)
        
    def update_properties(self, item):
        """
        Обновление свойств элемента.
        
        Args:
            item: Элемент для отображения свойств
        """
        # Скрываем все виджеты свойств
        self.hide_all_widgets()

        # Восстанавливаем field_widget в виджетах
        if self.field_widget:
            self.robot_widget.field_widget = self.field_widget
            self.wall_widget.field_widget = self.field_widget
            self.region_widget.field_widget = self.field_widget

        # Определяем тип элемента и показываем соответствующий виджет
        if isinstance(item, Robot):
            self.robot_widget.update_properties(item)
            self.robot_widget.show()
            self.current_widget = self.robot_widget
        elif isinstance(item, Wall):
            self.wall_widget.update_properties(item)
            self.wall_widget.show()
            self.current_widget = self.wall_widget
        elif isinstance(item, Region):
            self.region_widget.update_properties(item)
            self.region_widget.show()
            self.current_widget = self.region_widget
        else:
            logger.warning(f"Неизвестный тип элемента: {type(item)}")
            self.current_widget = None
            
    def clear_properties(self):
        """Очистка свойств."""
        # Скрываем все виджеты свойств
        self.hide_all_widgets()
        self.current_widget = None
        
    def hide_all_widgets(self):
        """Скрывает все виджеты свойств."""
        self.robot_widget.hide()
        self.wall_widget.hide()
        self.region_widget.hide()
        
    def set_theme(self, is_dark_theme):
        """
        Установка темы оформления.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        self.is_dark_theme = is_dark_theme
        
        # Обновляем тему для всех виджетов
        self.robot_widget.set_theme(is_dark_theme)
        self.wall_widget.set_theme(is_dark_theme)
        self.region_widget.set_theme(is_dark_theme)
        
    def on_grid_snap_changed(self, enabled):
        """
        Обработчик изменения привязки к сетке.
        
        Args:
            enabled: Статус привязки
        """
        # Обновляем информацию о привязке к сетке во всех виджетах
        self.robot_widget.on_grid_snap_changed(enabled)
        self.wall_widget.on_grid_snap_changed(enabled)
        self.region_widget.on_grid_snap_changed(enabled)
        
    def connect_to_field_widget(self, field_widget):
        """
        Подключение к виджету поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.field_widget = field_widget
        
        # Передаем виджет поля всем виджетам свойств
        self.robot_widget.connect_to_field_widget(field_widget)
        self.wall_widget.connect_to_field_widget(field_widget)
        self.region_widget.connect_to_field_widget(field_widget) 