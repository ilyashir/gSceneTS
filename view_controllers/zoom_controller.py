from PyQt6.QtCore import QObject, pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QTransform
import logging

logger = logging.getLogger(__name__)

class ZoomController(QObject):
    """Управляет логикой масштабирования для QGraphicsView."""
    scale_changed = pyqtSignal(float)

    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view

        # Атрибуты масштаба (перенесены из FieldWidget)
        self._scale_factor = 1.0
        self._min_scale = 0.5
        self._max_scale = 3.0
        self._scale_step = 0.5

    # Методы будут добавлены здесь
    def current_scale(self):
        return self._scale_factor

    def handle_wheel_event(self, event):
        """Обрабатывает событие колеса мыши для масштабирования."""
        # Проверяем, зажата ли клавиша Ctrl
        is_ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        
        if is_ctrl_pressed:
            # Получаем текущее положение курсора в координатах сцены
            view_pos = event.position()
            scene_pos = self.view.mapToScene(int(view_pos.x()), int(view_pos.y()))
            
            # Определяем направление прокрутки
            scroll_direction = 1 if event.angleDelta().y() > 0 else -1
            
            # Изменяем масштаб
            old_scale = self._scale_factor
            if scroll_direction > 0:
                self.zoom_in()
            else:
                self.zoom_out()
                
            # Если масштаб не изменился, ничего не делаем
            if self._scale_factor == old_scale:
                return False # Сигнал, что событие не обработано
                
            # Корректируем положение сцены, чтобы точка под курсором осталась на месте
            new_pos = self.view.mapFromScene(scene_pos)
            delta = QPointF(new_pos.x() - view_pos.x(), new_pos.y() - view_pos.y())
            self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() + int(delta.x()))
            self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() + int(delta.y()))
            
            # Сообщаем об изменении масштаба через сигнал
            self.scale_changed.emit(self._scale_factor)
            logger.debug(f"Scale changed to: {self._scale_factor}")
            
            event.accept() # Подавляем стандартную обработку события
            return True # Сигнал, что событие обработано
        else:
            return False # Сигнал, что событие не обработано (передаем дальше)

    def scale_view(self, new_scale):
        """Масштабирует представление до указанного значения."""
        # Ограничиваем масштаб минимальным и максимальным значениями
        new_scale = max(min(new_scale, self._max_scale), self._min_scale)
        
        # Если масштаб не изменился, ничего не делаем
        if new_scale == self._scale_factor:
            return
            
        # Сохраняем новый масштаб
        self._scale_factor = new_scale
        
        # Применяем новый масштаб к QGraphicsView
        self.view.setTransform(QTransform().scale(self._scale_factor, self._scale_factor))
        
        # Сообщаем об изменении масштаба
        self.scale_changed.emit(self._scale_factor)
        
        logger.debug(f"View scaled to: {self._scale_factor}")

    def reset_scale(self):
        """Сбрасывает масштаб к стандартному (1.0)."""
        self.scale_view(1.0)
        logger.debug("Scale reset to 1.0")

    def zoom_in(self):
        """Увеличивает масштаб на один шаг."""
        self.scale_view(self._scale_factor + self._scale_step)
        logger.debug(f"Zoomed in to: {self._scale_factor}")

    def zoom_out(self):
        """Уменьшает масштаб на один шаг."""
        self.scale_view(self._scale_factor - self._scale_step)
        logger.debug(f"Zoomed out to: {self._scale_factor}") 