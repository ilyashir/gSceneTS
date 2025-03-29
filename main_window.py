from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QToolButton, QPushButton, QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QCheckBox, QSpacerItem, QSizePolicy, QFileDialog, QDockWidget, QSpinBox, QDoubleSpinBox, QButtonGroup, QStatusBar, QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from field_widget import FieldWidget
from properties_window import PropertiesWindow
import xml.etree.ElementTree as ET
from xml.dom import minidom 
from PyQt6.QtWidgets import QMessageBox
import logging
from styles import AppStyles
from config import config

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    scene_size_changed = pyqtSignal(int, int)  # width, height

    def __init__(self):
        super().__init__()
        
        # Получаем настройки из конфигурации
        app_name = config.get("app", "name")
        self.scene_width = config.get("scene", "default_width")
        self.scene_height = config.get("scene", "default_height")
        self.grid_size = config.get("grid", "size")
        self.snap_to_grid_default = config.get("grid", "snap_to_grid")
        
        # Определяем текущую тему
        self.is_dark_theme = config.get("appearance", "theme") == "dark"
        
        self.setWindowTitle(app_name)
        self.resize(1200, 800)  # Устанавливаем начальный размер
        self.showMaximized()  # Открыть на весь экран
        
        # Применяем текущую тему к главному окну
        self.apply_theme()
        
        # Создаем панель для координат и переключателя темы
        self.coords_panel = QWidget()
        coords_layout = QHBoxLayout()
        coords_layout.setContentsMargins(5, 5, 5, 5)
        
        # Создаем виджет для отображения координат
        self.coords_label = QLabel("X: 0, Y: 0", self)
        self.coords_label.setStyleSheet(AppStyles.get_coords_label_style(self.is_dark_theme))
        coords_layout.addWidget(self.coords_label)
        
        # Добавляем растягивающий элемент, чтобы переключатель был справа
        coords_layout.addStretch()
        
        # Создаем переключатель темы
        self.theme_switch = QPushButton("🌙" if not self.is_dark_theme else "☀️", self)
        self.theme_switch.setStyleSheet(AppStyles.get_theme_switch_style(self.is_dark_theme))
        self.theme_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_switch.clicked.connect(self.toggle_theme)
        self.theme_switch.setToolTip("Переключить тему")
        coords_layout.addWidget(self.theme_switch)
        
        self.coords_panel.setLayout(coords_layout)

        # Создаем окно свойств
        self.properties_window = PropertiesWindow()
        # Устанавливаем тему для окна свойств
        if hasattr(self.properties_window, 'set_theme'):
            self.properties_window.set_theme(self.is_dark_theme)
        else:
            self.properties_window.setStyleSheet(
                AppStyles.DARK_PROPERTIES_WINDOW if self.is_dark_theme else AppStyles.LIGHT_PROPERTIES_WINDOW
            )
        self.properties_dock = QDockWidget("Свойства", self)
        self.properties_dock.setWidget(self.properties_window)
        self.properties_dock.setStyleSheet(
            AppStyles.DARK_PROPERTIES_WINDOW if self.is_dark_theme else AppStyles.LIGHT_PROPERTIES_WINDOW
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

        # Создаем контейнер для координат и FieldWidget
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.coords_panel)  # Добавляем панель с координатами и переключателем
        
        # Добавляем окно с полем с параметрами из конфигурации
        self.field_widget = FieldWidget(self.properties_window, 
                                        scene_width=self.scene_width, 
                                        scene_height=self.scene_height,
                                        grid_size=self.grid_size)       
        layout.addWidget(self.field_widget)
    
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Подключаем сигналы от главного окна
        self.scene_size_changed.connect(self.field_widget.set_scene_size)
        # Подключаем сигналы от окна свойств
        self.properties_window.robot_position_changed.connect(self.field_widget.update_robot_position)
        self.properties_window.robot_rotation_changed.connect(self.field_widget.update_robot_rotation)
        self.properties_window.wall_position_point1_changed.connect(self.field_widget.update_wall_point1)
        self.properties_window.wall_position_point2_changed.connect(self.field_widget.update_wall_point2)
        self.properties_window.wall_size_changed.connect(self.field_widget.update_wall_size)
        self.properties_window.region_position_changed.connect(self.field_widget.update_region_position)
        self.properties_window.region_size_changed.connect(self.field_widget.update_region_size)
        self.properties_window.region_color_changed.connect(self.field_widget.update_region_color)
        # Подключаем сигналы изменения ID от окна свойств
        self.properties_window.wall_id_changed.connect(self.field_widget.update_wall_id)
        self.properties_window.region_id_changed.connect(self.field_widget.update_region_id)
        # Подключаем сигналы изменения координат мыши
        self.field_widget.mouse_coords_updated.connect(self.update_coords_label)

        # Создаем кнопку для скрытия/открытия окна свойств
        self.toggle_properties_button = QToolButton(self)
        self.toggle_properties_button.setIcon(QIcon("images/icon.webp"))  # Укажите путь к иконке
        self.toggle_properties_button.setToolTip("Toggle Properties")
        self.toggle_properties_button.setStyleSheet(AppStyles.get_toggle_button_style(self.is_dark_theme))
        self.toggle_properties_button.clicked.connect(self.toggle_properties_panel)        
        # Устанавливаем курсор для кнопки
        self.toggle_properties_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_properties_button.setToolTip("Показать/скрыть панель свойств")

        # Создаем правую панель инструментов и добавляем кнопку
        self.right_toolbar = QToolBar("Right Toolbar", self)
        self.right_toolbar.addWidget(self.toggle_properties_button)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.right_toolbar)
        
        # Основная левая панель инструментов
        self.toolbar = QToolBar()
        self.toolbar.setMinimumWidth(180)  # Минимальная ширина панели инструментов
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Добавляем виджет для изменения размера
        self.create_scene_size_widget()

        # Добавляем чекбокс "Привязываться к сетке"
        snap_to_grid_container = QWidget()
        snap_to_grid_layout = QHBoxLayout()
        snap_to_grid_layout.setContentsMargins(10, 0, 0, 0)  # Добавляем отступ слева
        
        self.snap_to_grid_checkbox = QCheckBox("Привязаться к сетке", self)
        self.snap_to_grid_checkbox.setStyleSheet(AppStyles.DARK_CHECKBOX_STYLE if self.is_dark_theme else AppStyles.LIGHT_CHECKBOX_STYLE)
        self.snap_to_grid_checkbox.setChecked(self.field_widget.snap_to_grid_enabled)
        self.snap_to_grid_checkbox.stateChanged.connect(self.toggle_snap_to_grid)
        self.snap_to_grid_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        
        snap_to_grid_layout.addWidget(self.snap_to_grid_checkbox)
        snap_to_grid_container.setLayout(snap_to_grid_layout)
        self.toolbar.addWidget(snap_to_grid_container)

        # Создаем кнопки режимов
        self.create_mode_buttons()
        self.create_drawing_buttons()
        
        # Добавляем разделитель перед кнопкой генерации XML
        separator_container = QWidget()
        separator_layout = QVBoxLayout()
        separator_layout.setContentsMargins(5, 10, 5, 10)  # Добавляем отступы сверху и снизу
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setMinimumHeight(2)  # Увеличиваем высоту линии
        separator.setStyleSheet(f"background-color: {AppStyles.BORDER_COLOR if self.is_dark_theme else AppStyles.LIGHT_BORDER_COLOR};")
        
        separator_layout.addWidget(separator)
        separator_container.setLayout(separator_layout)
        self.toolbar.addWidget(separator_container)
        
        # Кнопка для генерации XML
        generate_button = QPushButton("Сгенерировать XML")
        generate_button.setStyleSheet(AppStyles.get_accent_button_style(self.is_dark_theme))
        generate_button.clicked.connect(self.generate_xml)
        generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toolbar.addWidget(generate_button)

        # Устанавливаем режим наблюдателя по умолчанию
        self.set_mode("observer")
        
        # Устанавливаем курсоры для всех элементов интерфейса
        self.setup_cursors()
    
    def setup_cursors(self):
        """Устанавливает курсоры для всех элементов интерфейса"""
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
        
        # Устанавливаем для properties_window
        if hasattr(self, 'properties_window'):
            self.properties_window.setup_cursors()

    def update_coords_label(self, x, y):
        # Обновляет текст в QLabel с координатами мыши.
        self.coords_label.setText(f"Координаты мыши: X: {x:.2f}, Y: {y:.2f}")

    def toggle_snap_to_grid(self, state):
        """Включает или выключает привязку к сетке."""
        enabled = state == Qt.CheckState.Checked.value
        self.field_widget.snap_to_grid_enabled = enabled
        # Сохраняем настройку в конфиг
        config.set("grid", "snap_to_grid", enabled)
    
    def toggle_properties_panel(self):
        """Скрывает или показывает окно свойств."""
        if self.properties_dock.isVisible():
            self.properties_dock.hide()
        else:
            self.properties_dock.show()
    
    def create_scene_size_widget(self):
        size_widget = QWidget()
        size_layout = QVBoxLayout()  # Используем вертикальный макет
        size_layout.setSpacing(5)  # Уменьшаем расстояние между элементами
        size_layout.setContentsMargins(5, 0, 5, 0)  # внешние отступы
        size_widget.setLayout(size_layout)

        # Лейбл "Размер сцены"
        size_label = QLabel("Размер сцены")
        size_label.setStyleSheet(AppStyles.get_mode_label_style(self.is_dark_theme))
        size_layout.addWidget(size_label)

        # Виджет для лейблов полей ввода
        input_labels_widget = QWidget()
        input_labels_layout = QHBoxLayout()  # Горизонтальный макет для лейблов полей ввода
        input_labels_layout.setSpacing(0)  # Уменьшаем расстояние между элементами
        input_labels_layout.setContentsMargins(5, 0, 5, 0)  
        input_labels_widget.setLayout(input_labels_layout)

        self.input_height_label = QLabel("Высота сцены:")
        self.input_width_label = QLabel("Ширина сцены:")
        input_labels_layout.addWidget(self.input_height_label)
        input_labels_layout.addWidget(self.input_width_label)

        # Добавляем виджет с полями ввода в вертикальный макет
        size_layout.addWidget(input_labels_widget)

        # Виджет для полей ввода
        input_widget = QWidget()
        input_layout = QHBoxLayout()  # Горизонтальный макет для полей ввода
        input_layout.setSpacing(5)  # Уменьшаем расстояние между полями ввода
        input_layout.setContentsMargins(0, 0, 0, 0)  # Убираем внешние отступы
        input_widget.setLayout(input_layout)

        # Поле для ширины
        self.width_input = QLineEdit(str(self.field_widget.scene_width))
        self.width_input.setPlaceholderText("Width")
        self.width_input.setCursor(Qt.CursorShape.IBeamCursor)
        input_layout.addWidget(self.width_input)

        # Поле для высоты
        self.height_input = QLineEdit(str(self.field_widget.scene_height))
        self.height_input.setPlaceholderText("Height")
        self.height_input.setCursor(Qt.CursorShape.IBeamCursor)
        input_layout.addWidget(self.height_input)

        # Добавляем виджет с полями ввода в вертикальный макет
        size_layout.addWidget(input_widget)
        
        # Кнопка для применения изменений   
        self.apply_button = QPushButton("Применить", self)
        self.apply_button.setStyleSheet(AppStyles.get_accent_button_style(self.is_dark_theme))
        self.apply_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_button.clicked.connect(self.apply_size_changes)
        size_layout.addWidget(self.apply_button)

        # Создаем пустой виджет для отступа
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(30)  # Устанавливаем высоту отступа
        size_layout.addWidget(spacer_widget)  # Добавляем отступ на панель инструментов

        # Добавляем виджет на панель инструментов
        self.toolbar.addWidget(size_widget)

    def apply_size_changes(self):
        """Обработчик нажатия кнопки 'Применить'."""
        try:
            new_width = int(self.width_input.text())
            new_height = int(self.height_input.text())
        
            # Проверка на положительные значения
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Width and height must be greater than 0.")
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Некорректные значения ширины или высоты: {e}",
                QMessageBox.StandardButton.Ok
            )
            return

        # Вызываем метод изменения размера сцены
        self.scene_size_changed.emit(new_width, new_height)

    def create_mode_buttons(self):
        # Создаем контейнер для кнопок режимов
        mode_container = QWidget()
        mode_layout = QVBoxLayout()  # Изменяем на вертикальный макет для лучшего вида
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(5, 0, 5, 0)
        
        # Заголовок "Режим"
        self.mode_label = QLabel("Режим")
        self.mode_label.setStyleSheet(AppStyles.get_mode_label_style(self.is_dark_theme))
        mode_layout.addWidget(self.mode_label)
        
        # Группа кнопок для переключения режимов
        mode_buttons_group = QButtonGroup(self)
        
        # Кнопка режима наблюдателя
        self.observer_button = QPushButton("Наблюдатель")
        self.observer_button.setCheckable(True)
        self.observer_button.setChecked(True)  # Выбран по умолчанию
        self.observer_button.setStyleSheet(self.get_mode_button_style())
        self.observer_button.clicked.connect(lambda: self.set_mode("observer"))
        self.observer_button.setCursor(Qt.CursorShape.PointingHandCursor)
        mode_layout.addWidget(self.observer_button)
        mode_buttons_group.addButton(self.observer_button)
        
        # Кнопка режима редактирования
        self.edit_button = QPushButton("Редактирование")
        self.edit_button.setCheckable(True)
        self.edit_button.setStyleSheet(self.get_mode_button_style())
        self.edit_button.clicked.connect(lambda: self.set_mode("edit"))
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        mode_layout.addWidget(self.edit_button)
        mode_buttons_group.addButton(self.edit_button)
        
        # Кнопка режима рисования
        self.drawing_button = QPushButton("Рисование")
        self.drawing_button.setCheckable(True)
        self.drawing_button.setStyleSheet(self.get_mode_button_style())
        self.drawing_button.clicked.connect(lambda: self.set_mode("drawing"))
        self.drawing_button.setCursor(Qt.CursorShape.PointingHandCursor)
        mode_layout.addWidget(self.drawing_button)
        mode_buttons_group.addButton(self.drawing_button)
        
        # Устанавливаем макет для контейнера
        mode_container.setLayout(mode_layout)
        
        # Добавляем контейнер на панель инструментов
        self.toolbar.addWidget(mode_container)
        
    def create_drawing_buttons(self):
        # Создаем контейнер для инструментов рисования
        drawing_container = QWidget()
        drawing_layout = QVBoxLayout()  # Изменяем на вертикальный макет
        drawing_layout.setSpacing(5)
        drawing_layout.setContentsMargins(5, 0, 5, 0)
        
        # Заголовок "Рисовать"
        self.drawing_label = QLabel("Рисовать")
        self.drawing_label.setStyleSheet(AppStyles.get_mode_label_style(self.is_dark_theme))
        drawing_layout.addWidget(self.drawing_label)
        
        # Группа кнопок для инструментов рисования
        drawing_buttons_group = QButtonGroup(self)
        
        # Кнопка для рисования стен
        self.wall_button = QPushButton("Стена")
        self.wall_button.setCheckable(True)
        self.wall_button.setStyleSheet(self.get_tool_button_style())
        self.wall_button.clicked.connect(lambda: self.set_drawing_type("wall"))
        self.wall_button.setEnabled(False)
        self.wall_button.setCursor(Qt.CursorShape.PointingHandCursor)
        drawing_layout.addWidget(self.wall_button)
        drawing_buttons_group.addButton(self.wall_button)
        
        # Кнопка для рисования регионов
        self.region_button = QPushButton("Регион")
        self.region_button.setCheckable(True)
        self.region_button.setStyleSheet(self.get_tool_button_style())
        self.region_button.clicked.connect(lambda: self.set_drawing_type("region"))
        self.region_button.setEnabled(False)
        self.region_button.setCursor(Qt.CursorShape.PointingHandCursor)
        drawing_layout.addWidget(self.region_button)
        drawing_buttons_group.addButton(self.region_button)
        
        # Устанавливаем макет для контейнера
        drawing_container.setLayout(drawing_layout)
        
        # Добавляем контейнер на панель инструментов
        self.toolbar.addWidget(drawing_container)
    
    def get_mode_button_style(self):
        """Возвращает стиль кнопок режима в зависимости от темы"""
        return AppStyles.get_mode_button_style(self.is_dark_theme)
    
    def get_tool_button_style(self):
        """Возвращает стиль кнопок инструментов в зависимости от темы"""
        return AppStyles.get_tool_button_style(self.is_dark_theme)

    def set_mode(self, mode):
        """Устанавливает режим работы."""
        logger.debug(f"Setting mode to: {mode}")
        
        # Отключаем все кнопки режимов
        self.observer_button.setChecked(False)
        self.drawing_button.setChecked(False)
        self.edit_button.setChecked(False)
        
        # Включаем нужную кнопку
        if mode == "observer":
            logger.debug("Switching to observer mode")
            self.observer_button.setChecked(True)
            self.wall_button.setEnabled(False)
            self.region_button.setEnabled(False)
            self.field_widget.set_drawing_mode(None)
            self.field_widget.set_edit_mode(False)
        elif mode == "drawing":
            logger.debug("Switching to drawing mode")
            self.drawing_button.setChecked(True)
            self.wall_button.setEnabled(True)
            self.region_button.setEnabled(True)
            self.field_widget.set_edit_mode(False)
            # Если есть активная кнопка рисования, устанавливаем соответствующий режим
            if self.wall_button.isChecked():
                self.field_widget.set_drawing_mode("wall")
            elif self.region_button.isChecked():
                self.field_widget.set_drawing_mode("region")
        elif mode == "edit":
            logger.debug("Switching to edit mode")
            self.edit_button.setChecked(True)
            self.wall_button.setEnabled(False)
            self.region_button.setEnabled(False)
            self.field_widget.set_drawing_mode(None)
            self.field_widget.set_edit_mode(True)
    
    def set_drawing_type(self, drawing_type):
        """Устанавливает тип рисования (стена или регион)."""
        logger.debug(f"Setting drawing type to: {drawing_type}")
        
        # Отключаем обе кнопки
        self.wall_button.setChecked(False)
        self.region_button.setChecked(False)
        
        # Включаем нужную кнопку
        if drawing_type == "wall":
            logger.debug("Setting wall drawing mode")
            self.wall_button.setChecked(True)
            self.field_widget.set_drawing_mode("wall")
        elif drawing_type == "region":
            logger.debug("Setting region drawing mode")
            self.region_button.setChecked(True)
            self.field_widget.set_drawing_mode("region")
        else:
            logger.debug("Clearing drawing mode")
            self.field_widget.set_drawing_mode(None)

    def generate_xml(self):
        try:
            root = ET.Element("root")
            world = ET.SubElement(root, "world")

            walls_elem = ET.SubElement(world, "walls")
            for wall in self.field_widget.walls:
                begin = f"{wall.line().x1()}:{wall.line().y1()}"
                end = f"{wall.line().x2()}:{wall.line().y2()}"
                id = f"{wall.id}"
                ET.SubElement(walls_elem, "wall", begin=begin, end=end, id=id)

            regions_elem = ET.SubElement(world, "regions")
            for region in self.field_widget.regions:
                x = region.rect().x()
                y = region.rect().y()
                width = region.rect().width()
                height = region.rect().height()
                id = str(region.id)
                color = str(region.color)
                ET.SubElement(regions_elem, "region", x=str(x), y=str(y), width=str(width), height=str(height), id=id, color=color)

            if self.field_widget.robot_model:
                robot_elem = ET.SubElement(root, "robots")
                x = self.field_widget.robot_model.pos().x()
                y = self.field_widget.robot_model.pos().y()
                ET.SubElement(robot_elem, "robot", position=f"{x}:{y}")

            # Преобразуем ElementTree в строку
            xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)

            # Форматируем XML с помощью minidom
            formatted_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")

            # Записываем форматированный XML в файл
            file_name, _ = QFileDialog.getSaveFileName(self, "Save XML File", "", "XML Files (*.xml)")
            if file_name:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(formatted_xml)

                QMessageBox.information(self, "Success", "XML file generated successfully.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def apply_theme(self):
        """Применяет текущую тему к приложению"""
        if self.is_dark_theme:
            # Темная тема
            self.setStyleSheet(AppStyles.DARK_MAIN_WINDOW)
            if hasattr(self, 'properties_window'):
                if hasattr(self.properties_window, 'set_theme'):
                    self.properties_window.set_theme(True)
                else:
                    self.properties_window.setStyleSheet(AppStyles.DARK_PROPERTIES_WINDOW)
            # Применяем тему к полю сцены
            if hasattr(self, 'field_widget') and hasattr(self.field_widget, 'set_theme'):
                self.field_widget.set_theme(True)
            # Применяем стиль к QDockWidget
            if hasattr(self, 'properties_dock'):
                self.properties_dock.setStyleSheet(AppStyles.DARK_PROPERTIES_WINDOW)
            if hasattr(self, 'coords_label'):
                self.coords_label.setStyleSheet(AppStyles.DARK_COORDS_LABEL)
            if hasattr(self, 'theme_switch'):
                self.theme_switch.setStyleSheet(AppStyles.get_theme_switch_style(True))
                self.theme_switch.setText("☀️")  # Солнце для переключения на светлую тему
            
            # Обновляем стиль чекбокса
            if hasattr(self, 'snap_to_grid_checkbox'):
                self.snap_to_grid_checkbox.setStyleSheet(AppStyles.DARK_CHECKBOX_STYLE)
            
            # Обновляем стили заголовков и кнопок режимов
            if hasattr(self, 'observer_button'):
                self.observer_button.setStyleSheet(self.get_mode_button_style())
                self.drawing_button.setStyleSheet(self.get_mode_button_style())
                self.edit_button.setStyleSheet(self.get_mode_button_style())
            
            # Обновляем стили заголовков
            if hasattr(self, 'mode_label'):
                self.mode_label.setStyleSheet(AppStyles.get_mode_label_style(True))
            
            # Обновляем стили кнопок инструментов
            if hasattr(self, 'wall_button'):
                self.wall_button.setStyleSheet(self.get_tool_button_style())
                self.region_button.setStyleSheet(self.get_tool_button_style())
                
            # Обновляем стиль заголовка инструментов
            if hasattr(self, 'drawing_label'):
                self.drawing_label.setStyleSheet(AppStyles.get_mode_label_style(True))
        else:
            # Светлая тема
            self.setStyleSheet(AppStyles.LIGHT_MAIN_WINDOW)
            if hasattr(self, 'properties_window'):
                if hasattr(self.properties_window, 'set_theme'):
                    self.properties_window.set_theme(False)
                else:
                    self.properties_window.setStyleSheet(AppStyles.LIGHT_PROPERTIES_WINDOW)
            # Применяем тему к полю сцены
            if hasattr(self, 'field_widget') and hasattr(self.field_widget, 'set_theme'):
                self.field_widget.set_theme(False)
            # Применяем стиль к QDockWidget
            if hasattr(self, 'properties_dock'):
                self.properties_dock.setStyleSheet(AppStyles.LIGHT_PROPERTIES_WINDOW)
            if hasattr(self, 'coords_label'):
                self.coords_label.setStyleSheet(AppStyles.LIGHT_COORDS_LABEL)
            if hasattr(self, 'theme_switch'):
                self.theme_switch.setStyleSheet(AppStyles.get_theme_switch_style(False))
                self.theme_switch.setText("🌙")  # Луна для переключения на темную тему
            
            # Обновляем стиль чекбокса
            if hasattr(self, 'snap_to_grid_checkbox'):
                self.snap_to_grid_checkbox.setStyleSheet(AppStyles.LIGHT_CHECKBOX_STYLE)
            
            # Обновляем стили заголовков и кнопок режимов
            if hasattr(self, 'observer_button'):
                self.observer_button.setStyleSheet(self.get_mode_button_style())
                self.drawing_button.setStyleSheet(self.get_mode_button_style())
                self.edit_button.setStyleSheet(self.get_mode_button_style())
            
            # Обновляем стили заголовков
            if hasattr(self, 'mode_label'):
                self.mode_label.setStyleSheet(AppStyles.get_mode_label_style(False))
            
            # Обновляем стили кнопок инструментов
            if hasattr(self, 'wall_button'):
                self.wall_button.setStyleSheet(self.get_tool_button_style())
                self.region_button.setStyleSheet(self.get_tool_button_style())
                
            # Обновляем стиль заголовка инструментов
            if hasattr(self, 'drawing_label'):
                self.drawing_label.setStyleSheet(AppStyles.get_mode_label_style(False))
            
        # Сохраняем состояние темы в конфиг
        config.set("appearance", "dark_theme", str(self.is_dark_theme))

    def toggle_theme(self):
        """Переключает тему между светлой и темной"""
        self.is_dark_theme = not self.is_dark_theme
        
        # Сохраняем настройку в конфиг
        config.set("appearance", "theme", "dark" if self.is_dark_theme else "light")
        config.set("appearance", "theme_name", "Темный стиль" if self.is_dark_theme else "Светлый стиль")
        
        # Применяем тему
        self.apply_theme()
        
        # Обновляем курсоры
        self.setup_cursors()