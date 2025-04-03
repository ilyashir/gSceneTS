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
    with SignalBlock(widget):
        # Код, выполняемый при заблокированных сигналах
        widget.setValue(100)
    """
    
    def __init__(self, widget):
        self.widget = widget
        
    def __enter__(self):
        self.widget.blockSignals(True)
        return self.widget
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.widget.blockSignals(False)

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