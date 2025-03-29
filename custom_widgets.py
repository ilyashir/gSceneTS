from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsOpacityEffect, QLabel
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty, QSize
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QIcon
from styles import ButtonStyles

import logging

logger = logging.getLogger(__name__)

class EditableLineEdit(QWidget):
    """
    Виджет редактируемого текстового поля с кнопками подтверждения и отмены.
    """
    # Сигналы
    valueChanged = pyqtSignal(str, object)  # Сигнал при подтверждении нового значения, теперь передает и объект
    editingCanceled = pyqtSignal()  # Сигнал при отмене редактирования
    editingStarted = pyqtSignal()   # Сигнал при начале редактирования
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_value = ""
        self._is_edited = False
        self._linked_object = None  # Ссылка на связанный объект
        
        # Основной layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Текстовое поле
        self.text_field = QLineEdit(self)
        self.text_field.setStyleSheet(f"""
            background-color: {ButtonStyles.SECONDARY_DARK};
            color: {ButtonStyles.TEXT_COLOR};
            border: 1px solid {ButtonStyles.BORDER_COLOR};
            border-radius: 3px;
            padding: 3px;
        """)
        self.text_field.textChanged.connect(self._handle_text_changed)
        self.layout.addWidget(self.text_field)
        
        # Кнопка подтверждения (галочка)
        self.confirm_button = FlatRoundButton(self)
        self.confirm_button.setText("✓")
        self.confirm_button.setStyleSheet(f"""
            background-color: {ButtonStyles.SUCCESS_COLOR};
            color: {ButtonStyles.TEXT_HIGHLIGHT};
            border-radius: 4px;
        """)
        self.confirm_button.clicked.connect(self._confirm_changes)
        self.layout.addWidget(self.confirm_button)
        
        # Кнопка отмены (крестик)
        self.cancel_button = FlatRoundButton(self)
        self.cancel_button.setText("✕")
        self.cancel_button.setStyleSheet(f"""
            background-color: {ButtonStyles.ERROR_COLOR};
            color: {ButtonStyles.TEXT_HIGHLIGHT};
            border-radius: 4px;
        """)
        self.cancel_button.clicked.connect(self._cancel_changes)
        self.layout.addWidget(self.cancel_button)
        
        # Изначально скрываем кнопки
        self.confirm_button.setVisible(False)
        self.cancel_button.setVisible(False)
        
        # Эффекты прозрачности для анимации
        self.confirm_opacity_effect = QGraphicsOpacityEffect(self.confirm_button)
        self.confirm_opacity_effect.setOpacity(0)
        self.confirm_button.setGraphicsEffect(self.confirm_opacity_effect)
        
        self.cancel_opacity_effect = QGraphicsOpacityEffect(self.cancel_button)
        self.cancel_opacity_effect.setOpacity(0)
        self.cancel_button.setGraphicsEffect(self.cancel_opacity_effect)
        
        # Анимации
        self.confirm_animation = QPropertyAnimation(self.confirm_opacity_effect, b"opacity")
        self.confirm_animation.setDuration(300)
        self.confirm_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.cancel_animation = QPropertyAnimation(self.cancel_opacity_effect, b"opacity")
        self.cancel_animation.setDuration(300)
        self.cancel_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def text(self):
        """Возвращает текущий текст в поле ввода."""
        return self.text_field.text()
    
    def setText(self, text):
        """Устанавливает текст в поле ввода."""
        self.text_field.setText(text)
        self._original_value = text
        self._is_edited = False
        self._hide_buttons()
    
    def _handle_text_changed(self, text):
        """Обрабатывает изменение текста в поле ввода."""
        if text != self._original_value and not self._is_edited:
            logger.debug(f"Text changed from '{self._original_value}' to '{text}', showing buttons")
            self._is_edited = True
            self._show_buttons()
            self.editingStarted.emit()
        elif text == self._original_value and self._is_edited:
            logger.debug(f"Text reverted to original value '{self._original_value}', hiding buttons")
            self._is_edited = False
            self._hide_buttons()
    
    def _show_buttons(self):
        """Анимирует появление кнопок."""
        self.confirm_button.setVisible(True)
        self.cancel_button.setVisible(True)
        
        self.confirm_animation.setStartValue(0.0)
        self.confirm_animation.setEndValue(1.0)
        self.confirm_animation.start()
        
        self.cancel_animation.setStartValue(0.0)
        self.cancel_animation.setEndValue(1.0)
        self.cancel_animation.start()
    
    def _hide_buttons(self):
        """Анимирует скрытие кнопок."""
        if not self._is_edited:
            self.confirm_animation.setStartValue(1.0)
            self.confirm_animation.setEndValue(0.0)
            self.confirm_animation.start()
            
            self.cancel_animation.setStartValue(1.0)
            self.cancel_animation.setEndValue(0.0)
            self.cancel_animation.finished.connect(lambda: self._hide_buttons_after_animation())
            self.cancel_animation.start()
            
    def _hide_buttons_after_animation(self):
        """Скрывает кнопки после завершения анимации"""
        if not self._is_edited:
            self.confirm_button.setVisible(False)
            self.cancel_button.setVisible(False)
            # Отключаем соединение, чтобы избежать множественных вызовов
            try:
                self.cancel_animation.finished.disconnect()
            except TypeError:
                # Если нет подключенных слотов, игнорируем ошибку
                pass
    
    def _confirm_changes(self):
        """Подтверждает изменения."""
        text = self.text_field.text()
        # Проверяем, что текст действительно изменился
        if text != self._original_value:
            logger.debug(f"Confirming change from '{self._original_value}' to '{text}'")
            # Сначала отправляем сигнал, и только потом меняем внутреннее состояние
            # Это предотвратит потерю ссылки на текущий объект до отправки сигнала
            self.valueChanged.emit(text, self._linked_object)
            self._original_value = text
            self._is_edited = False
            self._hide_buttons()
        else:
            # Если текст не изменился, просто скрываем кнопки
            logger.debug(f"Text unchanged, hiding buttons")
            self._is_edited = False
            self._hide_buttons()
    
    def _cancel_changes(self):
        """Отменяет изменения."""
        logger.debug(f"Canceling changes, reverting to '{self._original_value}'")
        self.text_field.setText(self._original_value)
        self._is_edited = False
        self._hide_buttons()
        self.editingCanceled.emit()

    def setReadOnly(self, readonly):
        """Устанавливает режим только для чтения для текстового поля."""
        self.text_field.setReadOnly(readonly)
    
    def setStyleSheet(self, stylesheet):
        """Устанавливает стиль для текстового поля."""
        self.text_field.setStyleSheet(stylesheet)
        super().setStyleSheet(stylesheet)
        
    def setLinkedObject(self, obj):
        """Устанавливает связанный объект для текстового поля."""
        self._linked_object = obj
        logger.debug(f"Linked object set: {obj}")
        
    def getLinkedObject(self):
        """Возвращает связанный объект."""
        return self._linked_object


class FlatRoundButton(QPushButton):
    """Плоская кнопка со скруглёнными углами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setFlat(True)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Определяем путь для скругленного прямоугольника
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 4, 4)
        
        # Заливаем фон
        if self.styleSheet():
            color_str = self.styleSheet().split("background-color:")[1].split(";")[0].strip()
            painter.fillPath(path, QColor(color_str))
        
        # Рисуем текст
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text()) 