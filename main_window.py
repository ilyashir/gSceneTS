from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QToolButton, QPushButton, QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QCheckBox, QSpacerItem, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from field_widget import FieldWidget
from properties_window import PropertiesWindow
import xml.etree.ElementTree as ET
from xml.dom import minidom 
from PyQt6.QtWidgets import QMessageBox
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TS scene generator")
        self.resize(1200, 800)  # Устанавливаем начальный размер
        self.showMaximized()  # Открыть на весь экран

        # Создаем виджет для отображения координат
        self.coords_label = QLabel("Mouse Coords: (0, 0)", self)
        self.coords_label.setStyleSheet("font-size: 14px; color: black; background-color: white; padding: 5px;")

        # Добавляем окно со свойствами
        self.properties_window = PropertiesWindow()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_window)

        # Создаем контейнер для координат и FieldWidget
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.coords_label)  # Добавляем метку с координатами
        # Добавляем окно с полем
        self.field_widget = FieldWidget(self.properties_window)
       
        layout.addWidget(self.field_widget)
    
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключаем сигнал от FieldWidget для обновления полей ввода размера сцены
        self.field_widget.update_size_fields.connect(self.update_size_fields)
        # Подключаем сигнал от FieldWidget для обновления координат
        self.field_widget.mouse_coords_updated.connect(self.update_coords_label)

        # Создаем кнопку для скрытия/открытия окна свойств
        self.toggle_properties_button = QToolButton(self)
        self.toggle_properties_button.setIcon(QIcon("images/icon.webp"))  # Укажите путь к иконке
        self.toggle_properties_button.setToolTip("Toggle Properties")
        self.toggle_properties_button.setStyleSheet("""
            QToolButton {
                background-color: lightgray;
                border: 1px solid gray;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: darkgray;
            }
            QToolButton:checked {
                background-color: darkgray;
                border: 2px solid black;
            }
        """)
        self.toggle_properties_button.clicked.connect(self.toggle_properties_window)

        # Создаем правую панель инструментов и добавляем кнопку
        self.right_toolbar = QToolBar("Right Toolbar", self)
        self.right_toolbar.addWidget(self.toggle_properties_button)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.right_toolbar)
        
        # Основная панель инструментов слева
        self.toolbar = QToolBar()
        self.toolbar.setMinimumWidth(180)  # Минимальная ширина панели инструментов
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Добавляем виджет для изменения размера
        self.create_scene_size_widget()

        # Добавляем чекбокс "Привязываться к сетке"
        self.snap_to_grid_checkbox = QCheckBox("Привязываться к сетке", self)
        self.snap_to_grid_checkbox.setChecked(True)  # По умолчанию включено
        self.snap_to_grid_checkbox.stateChanged.connect(self.toggle_snap_to_grid)
        self.toolbar.addWidget(self.snap_to_grid_checkbox)

        self.create_tool_buttons()
        self.debug_mode = False  # Переменная для отслеживания режима отладки
    
    def update_coords_label(self, x, y):
        # Обновляет текст в QLabel с координатами мыши.
        self.coords_label.setText(f"Mouse Coords: ({x:.2f}, {y:.2f})")

    def toggle_snap_to_grid(self, state):
        """Включает или выключает привязку к сетке."""
        self.field_widget.snap_to_grid_enabled = state == Qt.CheckState.Checked.value
    
    def toggle_properties_window(self):
        """Скрывает или показывает окно свойств."""
        if self.properties_window.isVisible():
            self.properties_window.hide()
        else:
            self.properties_window.show()            
    
    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            print("Debug mode enabled")  # Сообщение в консоль
        else:
            print("Debug mode disabled")  # Сообщение в консоль    

    def create_scene_size_widget(self):
        size_widget = QWidget()
        size_layout = QVBoxLayout()  # Используем вертикальный макет
        size_layout.setSpacing(5)  # Уменьшаем расстояние между элементами
        size_layout.setContentsMargins(5, 0, 5, 0)  # внешние отступы
        size_widget.setLayout(size_layout)

        # Лейбл "Размер сцены"
        size_label = QLabel("Размер сцены")
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
        # self.width_input.editingFinished.connect(self.update_scene_size)
        input_layout.addWidget(self.width_input)

        # Поле для высоты
        self.height_input = QLineEdit(str(self.field_widget.scene_height))
        self.height_input.setPlaceholderText("Height")
        # self.height_input.editingFinished.connect(self.update_scene_size)
        input_layout.addWidget(self.height_input)

        # Добавляем виджет с полями ввода в вертикальный макет
        size_layout.addWidget(input_widget)
        
        # Кнопка для применения изменений   
        self.apply_button = QPushButton("Применить", self)
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
        self.field_widget.set_scene_size(new_width, new_height)
    
    def update_size_fields(self, width, height):
        """Обновляет поля ввода текущими размерами сцены."""
        self.width_input.setText(str(width))
        self.height_input.setText(str(height))   

    def create_tool_buttons(self):
        # Кнопка для стены
        self.wall_button = QToolButton()
        self.wall_button.setText("Draw wall")
        self.wall_button.setCheckable(True)
        self.wall_button.setFixedSize(100, 50)
        self.wall_button.setStyleSheet(self.get_button_style())
        self.wall_button.clicked.connect(lambda: self.set_drawing_mode("wall"))
        self.toolbar.addWidget(self.wall_button)

        # Кнопка для региона
        self.region_button = QToolButton()
        self.region_button.setText("Draw region")
        self.region_button.setCheckable(True)
        self.region_button.setFixedSize(100, 50)
        self.region_button.setStyleSheet(self.get_button_style())
        self.region_button.clicked.connect(lambda: self.set_drawing_mode("region"))
        self.toolbar.addWidget(self.region_button)

        # Создаем пустой виджет для отступа
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(30)  # Устанавливаем высоту отступа
        self.toolbar.addWidget(spacer_widget)  # Добавляем отступ на панель инструментов

        # Кнопка для редактирования
        self.edit_button = QToolButton()
        self.edit_button.setText("Edit")
        self.edit_button.setCheckable(True)
        self.edit_button.setFixedSize(50, 50)
        self.edit_button.setStyleSheet(self.get_button_style())
        self.edit_button.clicked.connect(self.set_edit_mode)
        self.toolbar.addWidget(self.edit_button)

        # Кнопка для отладки
        self.debug_button = QToolButton()
        self.debug_button.setText("Debug")
        self.debug_button.setCheckable(True)
        self.debug_button.setFixedSize(50, 50)
        self.debug_button.setStyleSheet(self.get_button_style())
        self.debug_button.clicked.connect(self.toggle_debug_mode)
        self.toolbar.addWidget(self.debug_button)

        # Кнопка для генерации XML
        generate_button = QPushButton("Generate XML")
        generate_button.clicked.connect(self.generate_xml)
        self.toolbar.addWidget(generate_button)

    def get_button_style(self):
        return """
            QToolButton {
                background-color: lightgray;
                border: 1px solid gray;
                border-radius: 5px;
            }
            QToolButton:hover {
                background-color: darkgray;
            }
            QToolButton:checked {
                background-color: darkgray;
                border: 2px solid black;
            }
        """

    def set_drawing_mode(self, mode):
        # Отключаем все кнопки
        self.wall_button.setChecked(False)
        self.region_button.setChecked(False)
        self.edit_button.setChecked(False)
        self.field_widget.set_edit_mode(False)

        # Включаем выбранную кнопку
        if mode == "wall":
            self.wall_button.setChecked(True)         
            if self.debug_mode:
                print("Drawing mode: Wall")  # Отладочный вывод
        elif mode == "region":
            self.region_button.setChecked(True)
            # self.region_button.setStyleSheet("background-color: darkgray;")
            if self.debug_mode:
                print("Drawing mode: Region")  # Отладочный вывод
        elif mode == "edit":
            self.edit_button.setChecked(True)
            self.field_widget.set_edit_mode(True)
            # self.edit_button.setStyleSheet("background-color: darkgray;")
            if self.debug_mode:
                print("Drawing mode: Edit")  # Отладочный вывод


        # Устанавливаем режим рисования
        self.field_widget.set_drawing_mode(mode)
   
    def update_scene_size(self):
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        self.field_widget.set_scene_size(width, height)

    def set_edit_mode(self):        
        self.set_drawing_mode("edit" if self.edit_button.isChecked() else None)

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

            if self.field_widget.robot_position:
                robot_elem = ET.SubElement(root, "robots")
                x = self.field_widget.robot_position.pos().x()
                y = self.field_widget.robot_position.pos().y()
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