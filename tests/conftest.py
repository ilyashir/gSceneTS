import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Создаем экземпляр QApplication для всех тестов
app = QApplication.instance()
if app is None:
    app = QApplication([])

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов с графическим интерфейсом"""
    app_instance = QApplication.instance() or QApplication(sys.argv)
    yield app_instance

@pytest.fixture(autouse=True)
def auto_close_message_boxes(monkeypatch):
    """Заменяет QMessageBox.warning на фиктивную функцию,
    которая не показывает диалоговое окно и сразу возвращает QMessageBox.StandardButton.Ok.
    
    Эта фикстура применяется автоматически для всех тестов.
    """
    
    # Создаем фиктивную функцию замены для QMessageBox.warning
    def mock_warning(*args, **kwargs):
        return QMessageBox.StandardButton.Ok
    
    # Заменяем реальную функцию нашей фиктивной
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)
    
    # То же для critical и information
    monkeypatch.setattr(QMessageBox, "critical", mock_warning)
    monkeypatch.setattr(QMessageBox, "information", mock_warning) 