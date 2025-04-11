"""
Адаптер для окна свойств.

Обеспечивает обратную совместимость с существующим кодом проекта.
Делегирует всю работу со свойствами новому PropertiesManager.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt, QObject
from PyQt6.QtGui import QFont
import logging

# Убираем импорт PropertiesManager, чтобы разорвать цикл
# from properties.properties_manager import PropertiesManager 

# Убираем импорты старых классов, т.к. работаем с новыми из scene.items
# from robot import Robot
# from wall import Wall
# from region import Region
# from start_position import StartPosition
# Убираем старый импорт
# from .properties_window import PropertiesWindow

from scene.items import Robot, Wall, Region, StartPosition
from .robot_properties_widget import RobotPropertiesWidget
from .wall_properties_widget import WallPropertiesWidget
from .region_properties_widget import RegionPropertiesWidget
from .start_position_properties_widget import StartPositionPropertiesWidget

logger = logging.getLogger(__name__)

class PropertiesWindow(QWidget):
    """
    Адаптер для окна свойств.
    
    Сохраняет тот же интерфейс, что и оригинальное окно свойств,
    но использует новый PropertiesManager для реализации функциональности.
    """
    # Сигналы для изменения свойств
    robot_position_changed = pyqtSignal(int, int)  # x, y
    robot_rotation_changed = pyqtSignal(int)  # rotation
    wall_position_point1_changed = pyqtSignal(int, int)  # x1, y1
    wall_position_point2_changed = pyqtSignal(int, int)  # x2, y2
    wall_stroke_width_changed = pyqtSignal(int)  # stroke_width
    region_position_changed = pyqtSignal(int, int)  # x, y
    region_size_changed = pyqtSignal(int, int)  # width, height
    region_color_changed = pyqtSignal(str)  # color
    wall_id_changed = pyqtSignal(str)  # id for walls
    region_id_changed = pyqtSignal(str)  # id for regions
    
    # Сигналы для оповещения об изменении свойств стартовой позиции
    start_position_changed = pyqtSignal(int, int)  # x, y
    start_position_direction_changed = pyqtSignal(int)  # direction
    
    def __init__(self, properties_manager: 'PropertiesManager', is_dark_theme=False):
        """
        Инициализация адаптера.
        
        Args:
            properties_manager: Экземпляр менеджера свойств
            is_dark_theme: Флаг темной темы
        """
        # Вызываем конструктор QWidget без parent, т.к. он будет добавлен в DockWidget
        super().__init__() 
        self.setWindowTitle("Свойства")
        self.setMinimumWidth(380)
        
        # Сохраняем переданный менеджер свойств
        self.properties_manager = properties_manager
        
        # Подключаем сигналы от менеджера свойств к сигналам адаптера
        self._connect_signals()
        
        # Создаем и настраиваем основной layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Создаем метку для отображения, когда нет выбранного элемента
        self.empty_label = QLabel("Выберите элемент на сцене для редактирования свойств")
        bold_font = QFont()
        bold_font.setBold(True)
        self.empty_label.setFont(bold_font)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setMargin(20)
        
        # Добавляем метку в основной layout
        self.main_layout.addWidget(self.empty_label)
        
        # Добавляем менеджер свойств в основной layout
        self.main_layout.addWidget(self.properties_manager)
        
        # Скрываем менеджер свойств по умолчанию
        self.properties_manager.hide()
        
        # Сохраняем ссылку на текущий элемент
        self.current_item = None
        self._last_region = None
        
        # Добавляем прямой доступ к виджетам для совместимости
        self._setup_compatibility_widgets()
        
        # Применяем тему
        self.set_theme(is_dark_theme)
        
    def _setup_compatibility_widgets(self):
        """Настройка прямых ссылок на виджеты для совместимости."""
        # Регион
        self.region_width = self.properties_manager.region_widget.width_spinbox
        self.region_height = self.properties_manager.region_widget.height_spinbox
        self.region_x = self.properties_manager.region_widget.x_spinbox
        self.region_y = self.properties_manager.region_widget.y_spinbox
        self.region_color_button = self.properties_manager.region_widget.color_button
        self.region_id = self.properties_manager.region_widget.id_edit
        
        # Стена
        self.wall_x1 = self.properties_manager.wall_widget.x1_spinbox
        self.wall_y1 = self.properties_manager.wall_widget.y1_spinbox
        self.wall_x2 = self.properties_manager.wall_widget.x2_spinbox
        self.wall_y2 = self.properties_manager.wall_widget.y2_spinbox
        self.wall_width_spinbox = self.properties_manager.wall_widget.wall_width_spinbox
        self.wall_id = self.properties_manager.wall_widget.id_edit
        
        # Робот
        self.robot_x = self.properties_manager.robot_widget.x_spinbox
        self.robot_y = self.properties_manager.robot_widget.y_spinbox
        self.robot_rotation = self.properties_manager.robot_widget.rotation_spinbox
        self.robot_id = self.properties_manager.robot_widget.robot_id_label
        
    def _connect_signals(self):
        """Подключение сигналов и слотов."""
        # Сигналы робота
        self.properties_manager.robot_position_changed.connect(self.robot_position_changed)
        self.properties_manager.robot_rotation_changed.connect(self.robot_rotation_changed)
        
        # Сигналы стены
        self.properties_manager.wall_position_point1_changed.connect(self.wall_position_point1_changed)
        self.properties_manager.wall_position_point2_changed.connect(self.wall_position_point2_changed)
        self.properties_manager.wall_stroke_width_changed.connect(self.wall_stroke_width_changed)
        self.properties_manager.wall_id_changed.connect(self.wall_id_changed)
        
        # Сигналы региона
        self.properties_manager.region_position_changed.connect(self.region_position_changed)
        self.properties_manager.region_size_changed.connect(self.region_size_changed)
        self.properties_manager.region_color_changed.connect(self.region_color_changed)
        self.properties_manager.region_id_changed.connect(self.region_id_changed)
        
        # Сигналы стартовой позиции
        self.properties_manager.start_position_changed.connect(self.start_position_changed)
        self.properties_manager.start_direction_changed.connect(self.start_position_direction_changed)
        
    def set_theme(self, is_dark_theme):
        """
        Установка темы оформления.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        logger.debug(f"Adapter: set_theme called with {is_dark_theme}")
        
        # Применяем тему к менеджеру свойств
        self.properties_manager.set_theme(is_dark_theme)
        
        # Применяем тему к пустой метке
        if is_dark_theme:
            self.empty_label.setStyleSheet("color: #ffffff;")
            self.setStyleSheet("background-color: #2d2d2d;")
        else:
            self.empty_label.setStyleSheet("color: #333333;")
            self.setStyleSheet("background-color: #f5f5f5;")
        
    def setup_cursors(self):
        """Устанавливает курсоры для всех элементов интерфейса в окне свойств."""
        # Вызываем соответствующий метод в менеджере
        # Этот метод вызывается из main_window.py
        pass  # Реализация происходит автоматически в виджетах
        
    def update_properties(self, item):
        """
        Обновление свойств элемента.
        
        Args:
            item: Элемент для отображения свойств
        """
        logger.debug(f"PropertiesWindow.update_properties вызван для {type(item).__name__}")
        
        self.current_item = item
        
        # Скрываем пустую метку и показываем менеджер свойств
        if self.empty_label.isVisible():
            self.empty_label.hide()
            self.properties_manager.show()
            
        # Делегируем обновление свойств менеджеру
        self.properties_manager.update_properties(item)
        
        logger.debug(f"PropertiesWindow.update_properties завершил обработку {type(item).__name__}")
        
    def clear_properties(self):
        """Очистка свойств."""
        # Убираем подсветку у предыдущего региона, если был выбран
        if hasattr(self, '_last_region') and self._last_region:
            try:
                logger.debug(f"Отключаем подсветку при очистке свойств: {self._last_region}")
                self._last_region.set_highlight(False)
                self._last_region = None
            except:
                pass
                
        self.current_item = None
        
        # Скрываем менеджер свойств и показываем пустую метку
        self.properties_manager.hide()
        self.empty_label.show()
        
        # Делегируем очистку свойств менеджеру
        self.properties_manager.clear_properties()
        
    # Методы для работы с field_widget из main_window.py
    def on_grid_snap_changed(self, enabled):
        """
        Обработчик изменения привязки к сетке.
        
        Args:
            enabled: Статус привязки
        """
        self.properties_manager.on_grid_snap_changed(enabled)
        
    # Совместимость с FieldWidget
    def connect_to_field_widget(self, field_widget):
        """
        Подключение к виджету поля.
        
        Args:
            field_widget: Виджет поля
        """
        self.properties_manager.connect_to_field_widget(field_widget)
        
    # Функции для сохранения обратной совместимости с FieldWidget
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
                if height != self.region_height.value():
                    self.region_height.setValue(height)
            
        logger.debug(f"[PropertiesWindow] Отправляем сигнал region_size_changed ({width}, {height})")
        self.region_size_changed.emit(width, height)
        
        logger.debug(f"[PropertiesWindow] ===== КОНЕЦ update_region_size =====")
    
    def hide_groups(self):
        """Скрывает все группы свойств."""
        self.properties_manager.hide_all_widgets()
        
    # Оригинальные методы, переадресующие вызовы к менеджеру свойств
    def show_robot_properties(self, x, y, rotation, robot_id=None):
        """Показывает свойства робота."""
        self.properties_manager.robot_widget.set_properties(x, y, rotation, robot_id)
        self.properties_manager.robot_widget.show()
        
    def show_wall_properties(self, x1, y1, x2, y2, width, wall_id=None):
        """Показывает свойства стены."""
        self.properties_manager.wall_widget.set_properties(x1, y1, x2, y2, width, wall_id)
        self.properties_manager.wall_widget.show()
        
    def show_region_properties(self, x, y, width, height, color, region_id=None):
        """Показывает свойства региона."""
        self.properties_manager.region_widget.set_properties(x, y, width, height, color, region_id)
        self.properties_manager.region_widget.show()
    
    # ==== Слоты для обработки сигналов ====
    
    def _on_wall_properties_changed(self, wall):
        """
        Обработчик изменения свойств стены.
        
        Args:
            wall: Объект стены
        """
        if wall and isinstance(wall, Wall):
            # Получаем актуальные свойства стены
            line = wall.line()
            width = wall.pen().width()
            
            # Эмитируем сигналы для оповещения о изменении свойств
            self.wall_begin_changed.emit(line.x1(), line.y1())
            self.wall_end_changed.emit(line.x2(), line.y2())
            self.wall_thickness_changed.emit(width)
    
    def _on_region_properties_changed(self, region):
        """
        Обработчик изменения свойств региона.
        
        Args:
            region: Объект региона
        """
        if region and isinstance(region, Region):
            # Получаем актуальные свойства региона
            rect = region.boundingRect()
            pos = region.pos()
            color = region.color().name()
            
            # Эмитируем сигналы для оповещения о изменении свойств
            self.region_position_changed.emit(pos.x(), pos.y())
            self.region_size_changed.emit(rect.width(), rect.height())
            self.region_color_changed.emit(color)
    
    def _on_robot_properties_changed(self, robot):
        """
        Обработчик изменения свойств робота.
        
        Args:
            robot: Объект робота
        """
        if robot and isinstance(robot, Robot):
            # Получаем актуальные свойства робота
            pos = robot.pos()
            name = robot.name
            direction = robot.direction
            
            # Эмитируем сигналы для оповещения о изменении свойств
            self.robot_position_changed.emit(pos.x(), pos.y())
            self.robot_name_changed.emit(name)
            self.robot_direction_changed.emit(direction)
    
    def _on_start_position_properties_changed(self, start_position):
        """
        Обработчик изменения свойств стартовой позиции.
        
        Args:
            start_position: Объект стартовой позиции
        """
        if start_position and isinstance(start_position, StartPosition):
            # Получаем актуальные свойства стартовой позиции
            pos = start_position.pos()
            direction = start_position.direction()
            
            # Эмитируем сигналы для оповещения о изменении свойств
            self.start_position_position_changed.emit(pos.x(), pos.y())
            self.start_position_direction_changed.emit(direction)