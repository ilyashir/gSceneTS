"""
Утилиты для работы с сигналами Qt.
"""

from PyQt6.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class SignalBlock:
    """
    Контекстный менеджер для блокировки сигналов.
    
    Использование:
    with SignalBlock(widget1, widget2, ...):
        # Код, выполняемый при заблокированных сигналах
        widget1.setValue(100)
        widget2.setValue(200)
    """
    
    def __init__(self, *widgets):
        """
        Инициализация с одним или несколькими виджетами.
        
        Args:
            *widgets: Один или несколько виджетов, сигналы которых нужно блокировать
        """
        self.widgets = widgets
        self.blocked_states = []
        
    def __enter__(self):
        """
        Блокирует сигналы от всех виджетов.
        """
        self.blocked_states = []
        for widget in self.widgets:
            if isinstance(widget, QObject):
                self.blocked_states.append(widget.blockSignals(True))
            else:
                self.blocked_states.append(False)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Восстанавливает исходное состояние сигналов для всех виджетов.
        """
        for i, widget in enumerate(self.widgets):
            if isinstance(widget, QObject):
                widget.blockSignals(self.blocked_states[i])

def safe_emit(signal, *args, **kwargs):
    """
    Безопасная эмиссия сигнала с обработкой ошибок.
    
    Args:
        signal: Сигнал для эмиссии
        *args: Позиционные аргументы для сигнала
        **kwargs: Именованные аргументы для сигнала
    """
    try:
        signal.emit(*args, **kwargs)
    except Exception as e:
        logger.error(f"Ошибка при эмиссии сигнала: {e}")

def safe_connect(signal, slot):
    """
    Безопасное подключение слота к сигналу.
    
    Args:
        signal: Сигнал для подключения
        slot: Слот для подключения
    """
    try:
        signal.connect(slot)
    except Exception as e:
        logger.error(f"Ошибка при подключении сигнала: {e}")

def safe_disconnect(signal, slot):
    """
    Безопасное отключение слота от сигнала.
    
    Args:
        signal: Сигнал для отключения
        slot: Слот для отключения
    """
    try:
        signal.disconnect(slot)
    except Exception as e:
        logger.error(f"Ошибка при отключении сигнала: {e}") 