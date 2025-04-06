from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsOpacityEffect, QLabel, QColorDialog, QSpinBox, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty, QSize
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QIcon
from styles import AppStyles

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
    
    def __init__(self, parent=None, is_dark_theme=True):
        super().__init__(parent)
        self._original_value = ""
        self._is_edited = False
        self._linked_object = None  # Ссылка на связанный объект
        self._is_dark_theme = is_dark_theme
        self._animation_initialized = False  # Флаг для контроля начальной инициализации
        
        # Основной layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Текстовое поле
        self.text_field = QLineEdit(self)
        self.text_field.textChanged.connect(self._handle_text_changed)
        self.layout.addWidget(self.text_field)
        
        # Кнопка подтверждения (галочка)
        self.confirm_button = FlatRoundButton(self)
        self.confirm_button.setText("✓")
        self.confirm_button.clicked.connect(self._confirm_changes)
        self.layout.addWidget(self.confirm_button)
        
        # Кнопка отмены (крестик)
        self.cancel_button = FlatRoundButton(self)
        self.cancel_button.setText("✕")
        self.cancel_button.clicked.connect(self._cancel_changes)
        self.layout.addWidget(self.cancel_button)
        
        # Обновляем стили ПЕРЕД скрытием
        self.update_styles(is_dark_theme)
        
        # Изначально скрываем кнопки
        self.confirm_button.hide()
        self.cancel_button.hide()
        
        # Эффекты прозрачности для анимации (уже должны быть 0)
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
        
        # Отмечаем, что анимация инициализирована и готова к использованию
        self._animation_initialized = True
        
    def update_styles(self, is_dark_theme=True):
        """Обновляет стили виджета в зависимости от темы"""
        self._is_dark_theme = is_dark_theme
        colors = AppStyles._get_theme_colors(is_dark_theme)
        
        # Вычисляем цвета для эффектов
        hover_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.1)"
        focus_bg = f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.2)"
        
        # Стиль для текстового поля
        self.text_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['secondary_dark']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 4px 8px;
                min-height: 24px;
            }}
            QLineEdit:hover {{
                background-color: {hover_bg};
                border: 1px solid {colors['primary']};
            }}
            QLineEdit:focus {{
                background-color: {focus_bg};
                border: 2px solid {colors['primary']};
            }}
        """)
        
        # Стиль для кнопки подтверждения
        confirm_color = colors['success']
        confirm_hover_border = "white"
        self.confirm_button.setStyleSheet(f"""
            background-color: {confirm_color};
            color: {colors['text_highlight']};
            border-radius: 4px;
            min-width: 24px;
            min-height: 18px;
            border: 0px solid {confirm_hover_border};
        """)
        
        # Стиль для кнопки отмены
        cancel_color = colors['error']
        cancel_hover_border = "white"
        self.cancel_button.setStyleSheet(f"""
            background-color: {cancel_color};
            color: {colors['text_highlight']};
            border-radius: 4px;
            min-width: 24px;
            min-height: 18px;
            border: 0px solid {cancel_hover_border};
        """)
        
    def set_theme(self, is_dark_theme=True):
        """Устанавливает тему для виджета"""
        if self._is_dark_theme != is_dark_theme:
            self.update_styles(is_dark_theme)
    
    def text(self):
        """Возвращает текущий текст в поле ввода."""
        return self.text_field.text()
    
    def setText(self, text):
        """Устанавливает текст в поле ввода."""
        # Временно блокируем сигналы, чтобы избежать вызова _handle_text_changed
        self.text_field.blockSignals(True)
        self.text_field.setText(text)
        self.text_field.blockSignals(False)
        
        self._original_value = text
        # Убедимся, что флаг сброшен ПОСЛЕ установки текста и original_value
        self._is_edited = False
        # Вызываем скрытие кнопок (без анимации, если они уже скрыты)
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
        # Проверяем, что анимация инициализирована
        if not self._animation_initialized:
            return
            
        # Сначала проверяем, что кнопки не в процессе анимации
        if self.confirm_animation.state() == QPropertyAnimation.State.Running or self.cancel_animation.state() == QPropertyAnimation.State.Running:
            return
            
        # Убеждаемся, что кнопки видимы перед началом анимации
        self.confirm_button.show()
        self.cancel_button.show()
        
        # Отключаем соединения с предыдущей анимацией
        try:
            self.cancel_animation.finished.disconnect()
        except TypeError:
            pass
        
        # Запускаем анимацию появления
        self.confirm_animation.setStartValue(0.0)
        self.confirm_animation.setEndValue(1.0)
        self.confirm_animation.start()
        
        self.cancel_animation.setStartValue(0.0)
        self.cancel_animation.setEndValue(1.0)
        self.cancel_animation.start()
    
    def _hide_buttons(self):
        """Анимирует скрытие кнопок."""
        # Проверяем, что анимация инициализирована
        if not self._animation_initialized:
            return
            
        # Скрываем только если редактирование не активно
        if not self._is_edited:
            # Сначала проверяем, что кнопки не в процессе анимации
            if self.confirm_animation.state() == QPropertyAnimation.State.Running or self.cancel_animation.state() == QPropertyAnimation.State.Running:
                return
                
            # Отключаем соединения с предыдущей анимацией
            try:
                self.cancel_animation.finished.disconnect()
            except TypeError:
                pass
                
            # Запускаем анимацию скрытия
            self.confirm_animation.setStartValue(1.0)
            self.confirm_animation.setEndValue(0.0)
            self.confirm_animation.start()
            
            self.cancel_animation.setStartValue(1.0)
            self.cancel_animation.setEndValue(0.0)
            # Подключаем обработчик завершения анимации
            self.cancel_animation.finished.connect(self._hide_buttons_after_animation)
            self.cancel_animation.start()
    
    def _hide_buttons_after_animation(self):
        """Скрывает кнопки после завершения анимации"""
        if not self._is_edited:
            self.confirm_button.hide()
            self.cancel_button.hide()
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
        
    def setValue(self, value):
        """
        Устанавливает значение в поле редактирования.
        Метод для совместимости с другими компонентами UI.
        
        Args:
            value: Новое значение
        """
        self.setText(str(value))
        
    def getText(self):
        """
        Возвращает текущий текст из поля редактирования.
        
        Returns:
            str: Текущий текст
        """
        return self.text_field.text()
    
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
        self.setFixedSize(24, 24)  # Чуть увеличиваем размер для лучшей кликабельности
        self.setFlat(True)
        self._is_hovered = False
        self._border_width = 0
        self._border_color = QColor("white")
        # Включаем отслеживание наведения мыши
        self.setMouseTracking(True)
        # Устанавливаем курсор
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        """Переопределяем событие входа курсора мыши в область кнопки"""
        self._is_hovered = True
        self._border_width = 2
        self.update()  # Вызываем перерисовку
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Переопределяем событие выхода курсора мыши из области кнопки"""
        self._is_hovered = False
        self._border_width = 0
        self.update()  # Вызываем перерисовку
        super().leaveEvent(event)
    
    def setStyleSheet(self, stylesheet):
        """Переопределяем метод для извлечения цвета границы из styleSheet"""
        super().setStyleSheet(stylesheet)
        # Извлекаем цвет границы, если он указан
        if "border:" in stylesheet:
            try:
                border_parts = stylesheet.split("border:")[1].split(";")[0]
                # Извлекаем значение цвета
                if "solid" in border_parts:
                    color_str = border_parts.split("solid")[1].strip()
                    self._border_color = QColor(color_str)
            except Exception:
                pass
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Определяем путь для скругленного прямоугольника с учетом границы
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width()-2, self.height()-2, 4, 4)
        
        # Заливаем фон
        if self.styleSheet():
            # Получаем базовый цвет фона
            try:
                color_str = self.styleSheet().split("background-color:")[1].split(";")[0].strip()
                bg_color = QColor(color_str)
                
                # Для эффекта наведения
                if self._is_hovered and self._border_width > 0:
                    # Настраиваем перо для рисования границы
                    pen = painter.pen()
                    pen.setWidth(self._border_width)
                    pen.setColor(self._border_color)
                    painter.setPen(pen)
                    
                    # Рисуем границу
                    border_path = QPainterPath()
                    border_path.addRoundedRect(1, 1, self.width()-2, self.height()-2, 4, 4)
                    painter.drawPath(border_path)
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                
                # Заливка основным цветом
                painter.fillPath(path, bg_color)
            except Exception:
                # В случае ошибки разбора styleSheet используем заливку по умолчанию
                painter.fillPath(path, QColor("#333333"))
        
        # Рисуем текст
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


# Создаем локализованный диалог выбора цвета
class RussianColorDialog(QColorDialog):
    """Локализованный на русский язык диалог выбора цвета"""
    
    def __init__(self, initial_color=None, parent=None, is_dark_theme=False):
        super().__init__(initial_color, parent)
        self._is_dark_theme = is_dark_theme
        self.setWindowTitle("Выберите цвет")
        self.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        logger.debug("Создан локализованный диалог выбора цвета RussianColorDialog")
        
    def set_theme(self, is_dark_theme):
        """
        Устанавливает тему оформления для диалога.
        
        Args:
            is_dark_theme: True для темной темы, False для светлой
        """
        if self._is_dark_theme != is_dark_theme:
            self._is_dark_theme = is_dark_theme
            self.update_style()
        
    def update_style(self):
        """Обновляет стиль диалога в соответствии с текущей темой"""
        # Получаем цветовую тему для стилизации диалога
        bg_color = AppStyles.SECONDARY_COLOR if self._is_dark_theme else AppStyles.LIGHT_SECONDARY_COLOR
        text_color = AppStyles.TEXT_COLOR if self._is_dark_theme else AppStyles.LIGHT_TEXT_COLOR
        input_bg = AppStyles.SECONDARY_DARK if self._is_dark_theme else AppStyles.LIGHT_SECONDARY_DARK
        border_color = AppStyles.BORDER_COLOR if self._is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        
        self.setStyleSheet(f"""
            QColorDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QLineEdit {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 3px;
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 2px;
            }}
            QPushButton {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.PRIMARY_COLOR if self._is_dark_theme else AppStyles.LIGHT_PRIMARY_COLOR};
                color: {'white' if self._is_dark_theme else AppStyles.LIGHT_TEXT_COLOR};
            }}
        """)
        
    def showEvent(self, event):
        """Переопределяем метод показа окна, чтобы локализовать элементы интерфейса"""
        super().showEvent(event)
        logger.debug("Вызван метод showEvent для RussianColorDialog")
        
        # Обновляем стиль перед показом
        self.update_style()
        
        # Переводим кнопки
        buttons = self.findChildren(QPushButton)
        logger.debug(f"Найдено кнопок: {len(buttons)}")
        for button in buttons:
            logger.debug(f"Кнопка с текстом: '{button.text()}'")
            if button.text() == "&OK" or button.text() == "OK":
                button.setText("ОК")
                logger.debug("Заменено на 'ОК'")
            elif button.text() == "&Cancel" or button.text() == "Cancel":
                button.setText("Отмена")
                logger.debug("Заменено на 'Отмена'")
            elif button.text() == "&Pick Screen Color":
                button.setText("Взять цвет с экрана")
                logger.debug("Заменено на 'Взять цвет с экрана'")
            elif button.text() == "&Add to Custom Colors":
                button.setText("Добавить в пользовательские цвета")
                logger.debug("Заменено на 'Добавить в пользовательские цвета'")
        
        # Переводим метки
        labels = self.findChildren(QLabel)
        logger.debug(f"Найдено меток: {len(labels)}")
        for label in labels:
            logger.debug(f"Метка с текстом: '{label.text()}'")
            if label.text() == "&Basic colors" or label.text() == "Basic colors":
                label.setText("Основные цвета")
                logger.debug("Заменено на 'Основные цвета'")
            elif label.text() == "&Custom colors" or label.text() == "Custom colors":
                label.setText("Пользовательские цвета")
                logger.debug("Заменено на 'Пользовательские цвета'")
            elif label.text() == "Hu&e:" or label.text() == "Hue:":
                label.setText("Тон:")
                logger.debug("Заменено на 'Тон:'")
            elif label.text() == "&Sat:" or label.text() == "Sat:":
                label.setText("Насыщ:")
                logger.debug("Заменено на 'Насыщ:'")
            elif label.text() == "&Val:" or label.text() == "Val:":
                label.setText("Знач:")
                logger.debug("Заменено на 'Знач:'")
            elif label.text() == "&Red:" or label.text() == "Red:":
                label.setText("Красный:")
                logger.debug("Заменено на 'Красный:'")
            elif label.text() == "&Green:" or label.text() == "Green:":
                label.setText("Зеленый:")
                logger.debug("Заменено на 'Зеленый:'")
            elif label.text() == "Bl&ue:" or label.text() == "Blue:":
                label.setText("Синий:")
                logger.debug("Заменено на 'Синий:'")
            elif label.text() == "A&lpha channel:" or label.text() == "Alpha channel:":
                label.setText("Прозрачность:")
                logger.debug("Заменено на 'Прозрачность:'")
            elif label.text() == "&HTML:" or label.text() == "HTML:":
                label.setText("HTML:")
                logger.debug("Заменено на 'HTML:'")
            
        # Дополнительный способ локализации - обновляем кнопки и метки по их объектному имени
        # Qt иногда использует другие виджеты для отображения текста
        for obj in self.findChildren(QWidget):
            if hasattr(obj, 'setText'):
                try:
                    current_text = obj.text() if hasattr(obj, 'text') else ""
                    logger.debug(f"Проверяем текст виджета: '{current_text}', класс: {obj.__class__.__name__}")
                    
                    # Локализация текста
                    if "&Basic colors" in current_text or "Basic colors" in current_text:
                        obj.setText("Основные цвета")
                    elif "&Custom colors" in current_text or "Custom colors" in current_text:
                        obj.setText("Пользовательские цвета")
                    elif "Hu&e:" in current_text or "Hue:" in current_text:
                        obj.setText("Тон:")
                    elif "&Sat:" in current_text or "Sat:" in current_text:
                        obj.setText("Насыщ:")
                    elif "&Val:" in current_text or "Val:" in current_text:
                        obj.setText("Знач:")
                    elif "&Red:" in current_text or "Red:" in current_text:
                        obj.setText("Красный:")
                    elif "&Green:" in current_text or "Green:" in current_text:
                        obj.setText("Зеленый:")
                    elif "Bl&ue:" in current_text or "Blue:" in current_text:
                        obj.setText("Синий:")
                    elif "A&lpha channel:" in current_text or "Alpha:" in current_text or "Alpha channel:" in current_text:
                        obj.setText("Прозрачность:")
                    elif "&HTML:" in current_text or "HTML:" in current_text:
                        obj.setText("HTML:")
                    elif "&Pick Screen Color" in current_text:
                        obj.setText("Взять цвет с экрана")
                    elif "&Add to Custom Colors" in current_text:
                        obj.setText("Добавить в пользовательские цвета")
                except Exception as e:
                    logger.debug(f"Ошибка при изменении текста: {e}")


class ColorPickerButton(QPushButton):
    """Кнопка для выбора цвета с отображением текущего выбранного цвета и поддержкой альфа-канала"""
    
    colorChanged = pyqtSignal(str)  # Сигнал при изменении цвета (строка с цветом)
    
    def __init__(self, color="#800000ff", parent=None, is_dark_theme=False):
        super().__init__(parent)
        self._color = color
        self._is_dark_theme = is_dark_theme
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.show_color_dialog)
        self.update_style()
        
    def update_style(self):
        """Обновляет стиль кнопки в соответствии с текущим цветом"""
        # Получаем цвет для фона кнопки
        qcolor = QColor(self._color)
        qcolor_str = qcolor.name(QColor.NameFormat.HexArgb)
        
        # Получаем цвет границы в зависимости от темы
        border_color = AppStyles.BORDER_COLOR if self._is_dark_theme else AppStyles.LIGHT_BORDER_COLOR
        hover_border = "#BBBBBB" if self._is_dark_theme else "#555555"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {qcolor_str};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid {hover_border};
            }}
        """)
        
    def show_color_dialog(self):
        """Показывает диалог выбора цвета с поддержкой прозрачности"""
        # Создаем объект QColor из текущего значения цвета с альфа-каналом
        current_color = QColor(self._color)
        
        # Используем локализованный диалог
        dialog = RussianColorDialog(current_color, self, self._is_dark_theme)
        
        # Отображаем диалог и обрабатываем результат
        if dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = dialog.selectedColor()
            if color.isValid():
                # Формат с альфа-каналом #AARRGGBB
                self.setColor(color.name(QColor.NameFormat.HexArgb))
            
    def color(self):
        """Возвращает текущий цвет"""
        return self._color
        
    def setColor(self, color):
        """Устанавливает цвет кнопки"""
        if self._color != color:
            self._color = color
            self.update_style()
            self.colorChanged.emit(color)
            
    def set_theme(self, is_dark_theme):
        """Устанавливает тему для виджета"""
        if self._is_dark_theme != is_dark_theme:
            self._is_dark_theme = is_dark_theme
            self.update_style()


class CustomSpinBox(QSpinBox):
    """
    Спинбокс с разделением обработки событий кнопок и ручного ввода.
    
    Стандартный QSpinBox отправляет сигнал valueChanged при каждом изменении,
    что неудобно при ручном вводе текста (прерывает ввод).
    
    Этот класс отличает изменения, вызванные кнопками от изменений, вызванных
    редактированием, и генерирует соответствующие сигналы.
    """
    # Обычный сигнал отправляется только при изменении с помощью кнопок спинбокса
    buttonValueChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_editing = False
        self._value_before_edit = 0
        self._is_button_change = False
        
        # Перенаправляем сигналы
        super().valueChanged.connect(self._on_value_changed)
        
    def _on_value_changed(self, value):
        """
        Обработчик изменения значения, определяет источник изменения.
        
        Если изменение происходит от кнопки, вызывает buttonValueChanged.
        Если от ручного ввода, сигнал не вызывается, а ждет завершения редактирования.
        """
        # Если изменение было вызвано кнопкой, эмитируем сигнал
        if self._is_button_change:
            self._is_button_change = False
            self.buttonValueChanged.emit(value)
        # Программное изменение значения (не от ручного ввода и не от кнопок)
        elif not self.hasFocus():
            self.buttonValueChanged.emit(value)
    
    def stepBy(self, steps):
        """
        Переопределение метода шага, вызываемого при нажатии кнопок спинбокса.
        """
        self._is_button_change = True
        super().stepBy(steps)
    
    def focusInEvent(self, event):
        """
        Обработчик события получения фокуса.
        Запоминает текущее значение для отслеживания изменений.
        """
        self._is_editing = True
        self._value_before_edit = self.value()
        super().focusInEvent(event)
        
    def focusOutEvent(self, event):
        """
        Обработчик события потери фокуса.
        Сигнализирует о завершении редактирования.
        """
        if self._is_editing and self.value() != self._value_before_edit:
            # При потере фокуса, если значение изменилось, отправляем сигнал
            self.buttonValueChanged.emit(self.value())
        self._is_editing = False
        super().focusOutEvent(event) 