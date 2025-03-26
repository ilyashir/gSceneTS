from PyQt6.QtWidgets import QDockWidget, QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem
from region import Region
from wall import Wall
from robot import Robot

class PropertiesWindow(QDockWidget):
    def __init__(self):
        super().__init__("Properties")
        # Создаем QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Разрешаем изменение размера содержимого

        # Создаем виджет для свойств
        self.properties_widget = QWidget()
        self.layout = QVBoxLayout()
        self.properties_widget.setLayout(self.layout)

        # Устанавливаем виджет в QScrollArea
        self.scroll_area.setWidget(self.properties_widget)
        self.setWidget(self.scroll_area)

        # Устанавливаем минимальную высоту окна свойств
        self.setMinimumHeight(300)  # Минимальная высота 100 пикселей
        self.setMinimumWidth(300)  # Минимальная ширина 100 пикселей
        # self.clear_properties()

    def update_properties(self, item):
        self.clear_properties()  # Очищаем текущее содержимое
        if isinstance(item, Wall):
            self.layout.addWidget(QLabel(f"Wall Properties"))
            self.layout.addWidget(QLabel(f"  ID: {item.id}"))
            self.layout.addWidget(QLabel(f"  Start: ({item.line().x1()}, {item.line().y1()})"))
            self.layout.addWidget(QLabel(f"  End: ({item.line().x2()}, {item.line().y2()})"))
        elif isinstance(item, Robot):
            self.layout.addWidget(QLabel(f"Robot Properties"))
            self.layout.addWidget(QLabel(f"  X: {item.pos().x()}"))
            self.layout.addWidget(QLabel(f"  Y: {item.pos().y()}"))
            self.layout.addWidget(QLabel(f"  Direction: {item.direction}"))
        elif isinstance(item, Region):
            self.layout.addWidget(QLabel(f"Region Properties"))
            self.layout.addWidget(QLabel(f"  ID: {item.id}"))
            self.layout.addWidget(QLabel(f"  X: {item.rect().x()}"))
            self.layout.addWidget(QLabel(f"  Y: {item.rect().y()}"))
            self.layout.addWidget(QLabel(f"  Width: {item.rect().width()}"))
            self.layout.addWidget(QLabel(f"  Height: {item.rect().height()}"))
            self.layout.addWidget(QLabel(f"  Color: {item.color}"))
        
        # Динамически изменяем высоту окна
        self.properties_widget.adjustSize()
        # self.adjustSize()
        self.setFixedHeight(self.properties_widget.sizeHint().height()*10 + 50)  # Добавляем небольшой отступ
    

    def clear_properties(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.setMinimumHeight(300)  # Минимальная высота 100 пикселей
        self.setMinimumWidth(300)  # Минимальная ширина 100 пикселей