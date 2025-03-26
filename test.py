import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Создаем QAction
        self.create_actions()
        
        # Установка заголовка окна
        self.setWindowTitle("Test Application")

    def create_actions(self):
        # Создаем QAction и добавляем его в меню
        action = QAction("My Action", self)
        action.triggered.connect(self.on_action_triggered)
        self.menuBar().addAction(action)

    def on_action_triggered(self):
        print("Action triggered!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())