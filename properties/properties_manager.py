"""
Менеджер свойств объектов.

Предоставляет централизованный интерфейс для управления свойствами
различных объектов (робот, стена, регион).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLayout, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot, QRectF
import logging

from .properties_window_adapter import PropertiesWindow
from scene.items import Robot, Wall, Region, StartPosition

from properties.robot_properties_widget import RobotPropertiesWidget
from properties.wall_properties_widget import WallPropertiesWidget
from properties.region_properties_widget import RegionPropertiesWidget
from properties.start_position_properties_widget import StartPositionPropertiesWidget

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
    wall_stroke_width_changed = pyqtSignal(int)  # stroke_width
    wall_id_changed = pyqtSignal(str)  # id

    # Сигналы для изменения свойств региона
    region_position_changed = pyqtSignal(int, int)  # x, y
    region_size_changed = pyqtSignal(int, int)  # width, height
    region_color_changed = pyqtSignal(str)  # color
    region_id_changed = pyqtSignal(str)  # id
    
    # Сигналы для изменения свойств стартовой позиции
    start_position_changed = pyqtSignal(int, int)  # x, y
    start_direction_changed = pyqtSignal(int)  # direction
    
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
        
        # Добавляем атрибут для хранения состояния привязки к сетке
        self._grid_snap_enabled = True # По умолчанию включено
        
        # --- Возвращаем инициализацию field_widget --- 
        self.field_widget = None 
        # ---------------------------------------------
        
    def _setup_widgets(self):
        """Создание и настройка виджетов свойств."""
        # Создаем виджеты свойств
        logger.debug(f"[SETUP_WIDGETS] создаем робота")
        self.robot_widget = RobotPropertiesWidget(self, self.is_dark_theme)
        logger.debug(f"[SETUP_WIDGETS] создаем стену")
        self.wall_widget = WallPropertiesWidget(self, self.is_dark_theme)
        logger.debug(f"[SETUP_WIDGETS] создаем регион")
        self.region_widget = RegionPropertiesWidget(self, self.is_dark_theme)
        logger.debug(f"[SETUP_WIDGETS] создаем стартовую позицию")
        self.start_position_widget = StartPositionPropertiesWidget(self, self.is_dark_theme)

        # Скрываем все виджеты по умолчанию
        self.robot_widget.hide()
        self.wall_widget.hide()
        self.region_widget.hide()
        self.start_position_widget.hide()
        
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
        layout.addWidget(self.start_position_widget)
        
        # Добавляем растягивающийся элемент в конец
        layout.addStretch()
        
        # Устанавливаем контейнер как виджет для прокрутки
        scroll_area.setWidget(container)
        
        # Создаем основной layout и добавляем в него scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
    def _connect_signals(self):
        """Подключает сигналы виджетов свойств к слотам."""

        # Робот
        self.robot_widget.position_changed.connect(self.robot_position_changed)
        self.robot_widget.rotation_changed.connect(self.robot_rotation_changed)
        
        # Стена
        self.wall_widget.position_point1_changed.connect(self.wall_position_point1_changed)
        self.wall_widget.position_point2_changed.connect(self.wall_position_point2_changed)
        self.wall_widget.width_changed.connect(self.wall_stroke_width_changed)
        self.wall_widget.id_changed.connect(self.wall_id_changed)
        
        # Регион
        self.region_widget.position_changed.connect(self.region_position_changed)
        self.region_widget.size_changed.connect(self.region_size_changed)
        self.region_widget.color_changed.connect(self.region_color_changed)
        self.region_widget.id_changed.connect(self.region_id_changed)

        # Стартовая позиция - обновляем на новые сигналы
        self.start_position_widget.position_changed.connect(self.start_position_changed)
        self.start_position_widget.direction_changed.connect(self.start_direction_changed)

    @pyqtSlot(QObject)
    def update_properties(self, item):
        """
        Обновление свойств элемента.
        Показывает нужный виджет и вызывает его метод update_properties.
        Не обновляет диапазоны или шаги - это делается отдельно.

        Args:
            item: Элемент для отображения свойств
        """
        logger.debug(f"PropertiesManager.update_properties вызван для {type(item).__name__}")
        self.hide_all_widgets()

        widget_to_update = None

        if isinstance(item, Robot):
            widget_to_update = self.robot_widget
        elif isinstance(item, Wall):
            widget_to_update = self.wall_widget
        elif isinstance(item, Region):
            widget_to_update = self.region_widget
        elif isinstance(item, StartPosition):
            widget_to_update = self.start_position_widget
        else:
            logger.warning(f"Неизвестный тип элемента: {type(item)}")
            self.current_widget = None
            return

        if widget_to_update:
            logger.debug(f"Вызов {type(widget_to_update).__name__}.update_properties для {item}")
            widget_to_update.update_properties(item) # Только обновление значений
            widget_to_update.show()
            self.current_widget = widget_to_update
            logger.debug(f"Виджет {type(widget_to_update).__name__} обновлен и показан")
        
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
        self.start_position_widget.hide()
        
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
        self.start_position_widget.set_theme(is_dark_theme)
        
    def on_grid_snap_changed(self, enabled):
        """
        Обработчик изменения привязки к сетке.
        Передает состояние всем виджетам свойств.
        
        Args:
            enabled: Статус привязки
        """
        logger.debug(f"PropertiesManager получил сигнал on_grid_snap_changed: {enabled}")
        self._grid_snap_enabled = enabled
        
        # Передаем новое состояние всем виджетам свойств
        widgets_to_update = [
            self.robot_widget,
            self.wall_widget,
            self.region_widget,
            self.start_position_widget
        ]
        
        for widget in widgets_to_update:
            if widget and hasattr(widget, 'set_snap_enabled'):
                try:
                    widget.set_snap_enabled(enabled)
                    logger.debug(f"Передано set_snap_enabled({enabled}) в {type(widget).__name__}")
                except Exception as e:
                    logger.error(f"Ошибка при вызове set_snap_enabled для {type(widget).__name__}: {e}")
        
    def connect_to_field_widget(self, field_widget):
        """
        Подключение к виджету поля.
        
        Args:
            field_widget: Виджет поля
        """
        logger.debug(f"PropertiesManager.connect_to_field_widget вызван с {field_widget}")
        
        # Сохраняем ссылку на field_widget
        self.field_widget = field_widget 
        
        # Передаем field_widget всем виджетам свойств
        logger.debug("Передаем field_widget всем виджетам свойств")
        self.robot_widget.connect_to_field_widget(field_widget)
        self.wall_widget.connect_to_field_widget(field_widget)
        self.region_widget.connect_to_field_widget(field_widget)
        self.start_position_widget.connect_to_field_widget(field_widget)
        
        # Получаем начальное состояние привязки из field_widget
        self._grid_snap_enabled = field_widget.snap_to_grid_enabled
        logger.debug(f"PropertiesManager подключен к FieldWidget, snap_enabled={self._grid_snap_enabled}")
        
    @pyqtSlot(QRectF)
    def on_scene_rect_changed(self, scene_rect):
        """Обновляет диапазоны всех виджетов свойств при изменении размера сцены."""
        logger.info(f"PropertiesManager получил сигнал scene_rect_changed: {scene_rect}")

        min_x = int(scene_rect.left())
        max_x = int(scene_rect.right())
        min_y = int(scene_rect.top())
        max_y = int(scene_rect.bottom())

        # Обновляем диапазоны для всех
        self.robot_widget.update_ranges(min_x, max_x, min_y, max_y)
        self.wall_widget.update_ranges(min_x, max_x, min_y, max_y)
        self.region_widget.update_ranges(min_x, max_x, min_y, max_y)

        # Для StartPosition учитываем центр
        # TODO: Получить ITEM_SIZE более надежно, если start_position_widget еще не инициализирован?
        # Пока берем константу.
        half_item = 25 # StartPosition.ITEM_SIZE / 2
        sp_min_x = int(scene_rect.left() + half_item)
        sp_max_x = int(scene_rect.right() - half_item)
        sp_min_y = int(scene_rect.top() + half_item)
        sp_max_y = int(scene_rect.bottom() - half_item)
        self.start_position_widget.update_ranges(sp_min_x, sp_max_x, sp_min_y, sp_max_y)

        logger.debug("Диапазоны для всех виджетов свойств обновлены.")

    # Слоты для стартовой позиции
    def _on_start_position_x_changed(self, x):
        """Обработчик изменения X-координаты стартовой позиции."""
        logger.debug(f"X-координата стартовой позиции изменена на: {x}")
        self.start_position_x_changed.emit(x)
        
    def _on_start_position_y_changed(self, y):
        """Обработчик изменения Y-координаты стартовой позиции."""
        logger.debug(f"Y-координата стартовой позиции изменена на: {y}")
        self.start_position_y_changed.emit(y)
        
    def _on_start_position_direction_changed(self, direction):
        """Обработчик изменения направления стартовой позиции."""
        logger.debug(f"Направление стартовой позиции изменено на: {direction}")
        self.start_position_direction_changed.emit(direction) 