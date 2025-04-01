from PyQt6.QtWidgets import QScrollBar, QGraphicsView
from PyQt6.QtCore import Qt, QRect, pyqtProperty, QTimer, QObject, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor

# Предопределенные цвета для тем
LIGHT_THEME = {
    "bg_color": QColor(200, 200, 200, 30),
    "handle_color": QColor(150, 150, 150, 80),
    "hover_color": QColor(80, 80, 80, 120),
    "pressed_color": QColor(40, 40, 40, 160)
}

DARK_THEME = {
    "bg_color": QColor(80, 80, 80, 30),
    "handle_color": QColor(120, 120, 120, 80),
    "hover_color": QColor(200, 200, 200, 120),
    "pressed_color": QColor(240, 240, 240, 160)
}

class GraphicsViewScrollBarThemeManager:
    """Менеджер тем для скроллбаров QGraphicsView"""
    
    @staticmethod
    def get_theme_colors(theme="light"):
        """Возвращает цвета для выбранной темы"""
        return DARK_THEME if theme == "dark" else LIGHT_THEME
    
    @staticmethod
    def apply_theme(scrollbar, theme="light"):
        """Применяет тему к скроллбару"""
        if hasattr(scrollbar, 'setTheme'):
            scrollbar.setTheme(theme)

class GraphicsViewScrollBar(QScrollBar):
    """Базовый класс для настраиваемых скроллбаров QGraphicsView"""
    
    def __init__(self, orientation, bg_alpha=30, handle_alpha=80, 
                 hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False,
                 auto_hide=True):
        super().__init__(orientation)
        
        # Сохраняем ориентацию
        self._orientation = orientation
        
        # Прозрачность для разных состояний
        self._bg_alpha = bg_alpha
        self._handle_alpha = handle_alpha
        self._hover_alpha = hover_alpha
        self._pressed_alpha = pressed_alpha
        
        # Значение прозрачности для анимации (0-1)
        self._opacity = 1.0
        
        # Настройка темы
        self._theme = "dark" if use_dark_theme else "light"
        
        # Состояние скроллбара
        self._mouse_over = False
        self._mouse_pressed = False
        
        # Настройка внешнего вида
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Настройка размера
        self._configure_size(scroll_bar_width)
        
        # Отслеживание положения мыши
        self.setMouseTracking(True)
        
        # Инициализация цветов
        self._init_colors()
        
        # Ссылка на GraphicsView
        self._view = None
        self._native_scrollbar = None
        
        # Для предотвращения рекурсии
        self._updating_value = False
        
        # Флаг для отслеживания удаления view
        self._view_deleted = False
        
        # Автоскрытие
        self._auto_hide = auto_hide
        if auto_hide:
            self.setOpacity(0.0)
            self._setup_auto_hide()
    
    def setGraphicsView(self, view):
        """Связывает скроллбар с QGraphicsView"""
        self._view = view
        
        # Отслеживаем уничтожение view
        view.destroyed.connect(self._on_view_destroyed)
        
        # Получаем соответствующий нативный скроллбар
        if self._orientation == Qt.Orientation.Vertical:
            self._native_scrollbar = view.verticalScrollBar()
            # Скрываем нативный вертикальный скроллбар
            view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self._native_scrollbar = view.horizontalScrollBar()
            # Скрываем нативный горизонтальный скроллбар
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Подключаем сигналы нативного скроллбара
        if self._native_scrollbar:
            self._native_scrollbar.valueChanged.connect(self._on_native_value_changed)
            self._native_scrollbar.rangeChanged.connect(self._on_native_range_changed)
        
        # Обновляем параметры из нативного скроллбара
        self._sync_from_native()
        
        # Подключаем наш сигнал valueChanged
        self.valueChanged.connect(self._on_own_value_changed)
        
        # Устанавливаем родителем GraphicsView
        self.setParent(view)
        
        # Размещаем скроллбар в правильном месте
        self._update_geometry()
        
        # Отслеживаем изменение размера и события мыши в GraphicsView
        view.installEventFilter(self)
                
         # Проверяем необходимость скроллбара и показываем/скрываем его
        self._update_visibility()
        
        # Также отслеживаем события для viewport
        view.viewport().installEventFilter(self)
    
    def _on_view_destroyed(self):
        """Обработчик события уничтожения view"""
        self._view_deleted = True
        self._view = None
        self._native_scrollbar = None
    
    def _configure_size(self, scroll_bar_width):
        """Настраивает размер скроллбара"""
        if self._orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(scroll_bar_width)
        else:
            self.setFixedHeight(scroll_bar_width)
    
    def _init_colors(self):
        """Инициализирует цвета в зависимости от темы"""
        colors = GraphicsViewScrollBarThemeManager.get_theme_colors(self._theme)
        self._bg_color = colors["bg_color"]
        self._handle_color = colors["handle_color"]
        self._hover_color = colors["hover_color"]
        self._pressed_color = colors["pressed_color"]
        
        # Устанавливаем прозрачность
        self._bg_color.setAlpha(self._bg_alpha)
        self._handle_color.setAlpha(self._handle_alpha)
        self._hover_color.setAlpha(self._hover_alpha)
        self._pressed_color.setAlpha(self._pressed_alpha)
    
    def _sync_from_native(self):
        """Синхронизирует параметры с нативным скроллбаром"""
        if not self._native_scrollbar:
            return
        
        # Предотвращаем рекурсию
        self._updating_value = True
        
        # Копируем диапазон и значение
        self.setMinimum(self._native_scrollbar.minimum())
        self.setMaximum(self._native_scrollbar.maximum())
        self.setPageStep(self._native_scrollbar.pageStep())
        self.setSingleStep(self._native_scrollbar.singleStep())
        self.setValue(self._native_scrollbar.value())
        
        self._updating_value = False
        
        # Обновляем внешний вид
        self.update()
    
    def _on_native_value_changed(self, value):
        """Обрабатывает изменение значения нативного скроллбара"""
        if not self._updating_value:
            self._updating_value = True
            self.setValue(value)
            self._updating_value = False
            # Показываем скроллбар при прокрутке
            if self._auto_hide:
                self.show_scrollbar()
    
    def _on_native_range_changed(self, min_val, max_val):
        """Обрабатывает изменение диапазона нативного скроллбара"""
        self.setRange(min_val, max_val)
    
    def _on_own_value_changed(self, value):
        """Обрабатывает изменение нашего значения"""
        if self._native_scrollbar and not self._updating_value:
            self._updating_value = True
            self._native_scrollbar.setValue(value)
            self._updating_value = False
    
    def _update_geometry(self):
        """Обновляет геометрию скроллбара"""
        if not self._view:
            return
            
        
        viewport = self._view.viewport()
        if not viewport:
            return
            
        viewport_rect = viewport.rect()
        scroll_size = self.width() if self._orientation == Qt.Orientation.Vertical else self.height()
        
        if self._orientation == Qt.Orientation.Vertical:
            # Вертикальный скроллбар справа
            self.setGeometry(
                viewport_rect.right() - scroll_size,
                viewport_rect.top(),
                scroll_size,
                viewport_rect.height()
            )
        else:
            # Горизонтальный скроллбар внизу
            self.setGeometry(
                viewport_rect.left(),
                viewport_rect.bottom() - scroll_size,
                viewport_rect.width(),
                scroll_size
            )
    
    def eventFilter(self, obj, event):
        """Фильтр событий для отслеживания действий в GraphicsView"""
        # Если GraphicsView был удален, прекращаем обработку
        if self._view_deleted:
            return False
            
        try:
            # Проверяем, что объект view существует и не был удален
            if self._view and obj is self._view:
                # При изменении размера GraphicsView обновляем геометрию скроллбара
                if event.type() == event.Type.Resize:
                    QTimer.singleShot(0, self._update_geometry)
                    QTimer.singleShot(0, self._update_visibility)  # Добавляем обновление видимости
                # Реагируем на вход курсора в область GraphicsView
                elif event.type() == event.Type.Enter and self._auto_hide:
                    self.show_scrollbar()
                # Реагируем на выход курсора из области GraphicsView
                elif event.type() == event.Type.Leave and self._auto_hide:
                    # Не запускаем таймер скрытия, если курсор находится над скроллбаром
                    if not self.underMouse():
                        self.start_hide_timer()
            
            # Проверяем, что объект view и viewport существуют и не были удалены
            elif self._view and hasattr(self._view, 'viewport') and obj is self._view.viewport():
                # Реагируем на вход курсора в область viewport
                if event.type() == event.Type.Enter and self._auto_hide:
                    self.show_scrollbar()
                # Реагируем на выход курсора из области viewport
                elif event.type() == event.Type.Leave and self._auto_hide:
                    # Не запускаем таймер скрытия, если курсор находится над скроллбаром или самим QGraphicsView
                    if not (self.underMouse() or (self._view and self._view.underMouse())):
                        self.start_hide_timer()
                # Также показываем скроллбары при движении мыши над viewport
                elif event.type() == event.Type.MouseMove and self._auto_hide:
                    self.show_scrollbar()
                # Обновляем видимость при изменении размера viewport
                elif event.type() == event.Type.Resize:
                     QTimer.singleShot(0, self._update_visibility)    
        except RuntimeError:
            # Если объект был удален, отключаем фильтр событий
            self._view_deleted = True
            self._view = None
            self._native_scrollbar = None
            return False
        
        return super().eventFilter(obj, event)
    
    def paintEvent(self, event):
        """Отрисовка скроллбара"""
        # Если полностью прозрачный - ничего не рисуем
        if self._opacity <= 0.01:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)
        
        # Рисуем фон
        painter.fillRect(self.rect(), self._bg_color)
        
        # Определяем цвет ползунка в зависимости от состояния
        if self._mouse_pressed:
            handle_color = self._pressed_color
        elif self._mouse_over:
            handle_color = self._hover_color
        else:
            handle_color = self._handle_color
        
        # Вычисляем размер и положение ползунка
        handle_rect = self._calculate_handle_rect()
        
        # Рисуем ползунок с закругленными углами
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(handle_color)
        
        # Радиус закругления
        radius = min(4, min(handle_rect.width(), handle_rect.height()) / 2)
        painter.drawRoundedRect(handle_rect, radius, radius)
    
    def _calculate_handle_rect(self):
        """Вычисляет прямоугольник ползунка"""
        # Получаем основные параметры
        min_val = self.minimum()
        max_val = self.maximum()
        page_step = self.pageStep()
        value = self.value()
        
        # Если нет диапазона для прокрутки, занимаем всю область
        if max_val <= min_val:
            return self.rect().adjusted(2, 2, -2, -2)
        
        # Вычисляем размер ползунка относительно размера скроллбара
        handle_size_ratio = min(1.0, float(page_step) / (max_val - min_val + page_step))
        
        # Вычисляем положение ползунка
        position_ratio = 0 if max_val == min_val else float(value - min_val) / (max_val - min_val)
        
        # Отступы
        margin = 2
        width = self.width()
        height = self.height()
        
        # Вычисляем прямоугольник в зависимости от ориентации
        if self._orientation == Qt.Orientation.Vertical:
            # Вертикальный скроллбар
            handle_height = max(width, int((height - 2 * margin) * handle_size_ratio))
            max_y = height - handle_height - 2 * margin
            handle_y = margin + int(max_y * position_ratio)
            return QRect(margin, handle_y, width - 2 * margin, handle_height)
        else:
            # Горизонтальный скроллбар
            handle_width = max(height, int((width - 2 * margin) * handle_size_ratio))
            max_x = width - handle_width - 2 * margin
            handle_x = margin + int(max_x * position_ratio)
            return QRect(handle_x, margin, handle_width, height - 2 * margin)
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        super().mousePressEvent(event)
        self._mouse_pressed = True
        self.update()
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        super().mouseReleaseEvent(event)
        self._mouse_pressed = False
        self.update()
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        super().mouseMoveEvent(event)
        
        # Проверяем, находится ли мышь над ползунком
        handle_rect = self._calculate_handle_rect()
        was_over = self._mouse_over
        self._mouse_over = handle_rect.contains(event.pos())
        
        # Обновляем только при изменении состояния
        if was_over != self._mouse_over:
            self.update()
    
    def enterEvent(self, event):
        """Обработка входа курсора в область скроллбара"""
        super().enterEvent(event)
        if self._auto_hide:
            self.show_scrollbar()
    
    def leaveEvent(self, event):
        """Обработка выхода курсора из области скроллбара"""
        super().leaveEvent(event)
        self._mouse_over = False
        self.update()
        
        if self._auto_hide:
            self.start_hide_timer()
    
    def opacity(self):
        """Геттер для свойства прозрачности"""
        return self._opacity
    
    def setOpacity(self, opacity):
        """Сеттер для свойства прозрачности"""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()
    
    # Определяем свойство для анимации
    opacity = pyqtProperty(float, opacity, setOpacity)
    
    def _setup_auto_hide(self):
        """Настраивает автоматическое скрытие скроллбара"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
        
        # Таймер для скрытия скроллбара
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_scrollbar)
        
        # Анимации для показа и скрытия
        self._show_animation = QPropertyAnimation(self, b"opacity")
        self._show_animation.setDuration(300)
        self._show_animation.setStartValue(0.0)
        self._show_animation.setEndValue(1.0)
        self._show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._hide_animation = QPropertyAnimation(self, b"opacity")
        self._hide_animation.setDuration(1000)
        self._hide_animation.setStartValue(1.0)
        self._hide_animation.setEndValue(0.0)
        self._hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
    
    def show_scrollbar(self):
        """Показывает скроллбар с анимацией"""
        if not hasattr(self, '_hide_timer'):
            return
            
        # Останавливаем таймер и анимацию скрытия
        self._hide_timer.stop()
        if self._hide_animation.state() == self._hide_animation.State.Running:
            self._hide_animation.stop()
        
        # Проверяем необходимость скроллбара
        self._update_visibility()
        
        # Если скроллбар не нужен, не показываем его
        if not self.isVisible():
            return
        
        # Запускаем анимацию показа
        current_opacity = self._opacity
        if current_opacity < 1.0:
            self._show_animation.setStartValue(current_opacity)
            self._show_animation.start()
    
    def start_hide_timer(self):
        """Запускает таймер для скрытия скроллбара"""
        if not hasattr(self, '_hide_timer'):
            return
            
        self._hide_timer.start(1000)  # Задержка в мс
    
    def hide_scrollbar(self):
        """Скрывает скроллбар с анимацией"""
        if not hasattr(self, '_hide_animation'):
            return
            
        current_opacity = self._opacity
        if current_opacity > 0.0:
            self._hide_animation.setStartValue(current_opacity)
            self._hide_animation.start()  # Запускаем анимацию скрытия

    def _update_visibility(self):
        """Обновление видимости скроллбара"""
        if not self._view or not self._native_scrollbar:
            return

        # Получаем размеры сцены и viewport
        scene_rect = self._view.scene().sceneRect()
        viewport_rect = self._view.viewport().rect()
        
        # Получаем матрицу преобразования для учета масштабирования
        transform = self._view.transform()
        
        # Применяем преобразование к размерам сцены
        mapped_rect = transform.mapRect(scene_rect)
        
        # Проверяем, нужен ли скроллбар с учетом масштабирования
        if self._orientation == Qt.Orientation.Horizontal:
            is_needed = mapped_rect.width() > viewport_rect.width()
        else:
            is_needed = mapped_rect.height() > viewport_rect.height()

        if is_needed:
            if not self.isVisible():
                self.show()
        else:
            if self.isVisible():
                self.hide()

    def resizeEvent(self, event):
        """Обработка изменения размера виджета"""
        super().resizeEvent(event)
        if self._view:
            self._update_geometry()
            self._update_visibility()        
    
    def setTheme(self, theme):
        """Устанавливает тему скроллбара"""
        if theme not in ["light", "dark"]:
            return
            
        self._theme = theme
        self._init_colors()
        self.update()
    
    def toggle_theme(self):
        """Переключает тему скроллбара"""
        new_theme = "dark" if self._theme == "light" else "light"
        self.setTheme(new_theme)


class GraphicsViewVerticalScrollBar(GraphicsViewScrollBar):
    """Вертикальный скроллбар для QGraphicsView"""
    
    def __init__(self, bg_alpha=30, handle_alpha=80, hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False, auto_hide=True):
        super().__init__(Qt.Orientation.Vertical, bg_alpha, handle_alpha, 
                        hover_alpha, pressed_alpha, scroll_bar_width, 
                        use_dark_theme, auto_hide)


class GraphicsViewHorizontalScrollBar(GraphicsViewScrollBar):
    """Горизонтальный скроллбар для QGraphicsView"""
    
    def __init__(self, bg_alpha=30, handle_alpha=80, hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False, auto_hide=True):
        super().__init__(Qt.Orientation.Horizontal, bg_alpha, handle_alpha, 
                        hover_alpha, pressed_alpha, scroll_bar_width, 
                        use_dark_theme, auto_hide)


class GraphicsViewScrollManager(QObject):
    """Менеджер для совместного управления скроллбарами QGraphicsView"""
    
    def __init__(self, view, vsb, hsb):
        super().__init__(view)
        self.view = view
        self.vsb = vsb
        self.hsb = hsb
        
        # Флаг для отслеживания удаления view
        self._view_deleted = False
        
        # Отслеживаем уничтожение view
        view.destroyed.connect(self._on_view_destroyed)
        
        # Устанавливаем фильтр событий для QGraphicsView и его viewport
        view.installEventFilter(self)
        view.viewport().installEventFilter(self)
    
    def _on_view_destroyed(self):
        """Обработчик события уничтожения view"""
        self._view_deleted = True
        self.view = None
    
    def eventFilter(self, obj, event):
        """Фильтр событий для QGraphicsView и его viewport"""
        if self._view_deleted:
            return False
            
        try:
            # Проверяем, существует ли view и что obj есть view
            if self.view and obj is self.view:
                # Показываем скроллбары при входе курсора и движении мыши
                if event.type() in [event.Type.Enter, event.Type.MouseMove]:
                    self._showScrollbars()
                # Запускаем таймер скрытия при выходе курсора
                elif event.type() == event.Type.Leave:
                    # Не скрываем, если курсор находится над одним из скроллбаров
                    if not (self.vsb.underMouse() or self.hsb.underMouse()):
                        self._startHideTimer()
            # Проверяем, существует ли view и viewport и что obj есть viewport
            elif self.view and hasattr(self.view, 'viewport') and obj is self.view.viewport():
                # Показываем скроллбары при входе курсора и движении мыши
                if event.type() in [event.Type.Enter, event.Type.MouseMove]:
                    self._showScrollbars()
                # Запускаем таймер скрытия при выходе курсора
                elif event.type() == event.Type.Leave:
                    # Не скрываем, если курсор находится над одним из скроллбаров
                    if not (self.vsb.underMouse() or self.hsb.underMouse()):
                        self._startHideTimer()
        except RuntimeError:
            # Если произошла ошибка доступа к удаленному C++ объекту
            self._view_deleted = True
            self.view = None
            return False
        
        return super().eventFilter(obj, event)
    
    def _showScrollbars(self):
        """Показывает оба скроллбара"""
        try:
            # Проверяем необходимость скроллбаров перед показом
            self.vsb._update_visibility()
            self.hsb._update_visibility()
            
            # Показываем только те скроллбары, которые нужны
            if self.vsb.isVisible():
                self.vsb.show_scrollbar()
            if self.hsb.isVisible():
                self.hsb.show_scrollbar()
        except RuntimeError:
            # Игнорируем ошибки при доступе к удаленным объектам
            pass
    
    def _startHideTimer(self):
        """Запускает таймер скрытия для обоих скроллбаров"""
        try:
            self.vsb.start_hide_timer()
            self.hsb.start_hide_timer()
        except RuntimeError:
            # Игнорируем ошибки при доступе к удаленным объектам
            pass
    
    def setTheme(self, theme):
        """Устанавливает тему для обоих скроллбаров"""
        if self._view_deleted:
            return
            
        try:
            self.vsb.setTheme(theme)
            self.hsb.setTheme(theme)
        except RuntimeError:
            self._view_deleted = True
            self.view = None
    
    def toggle_theme(self):
        """Переключает тему для обоих скроллбаров"""
        if self._view_deleted:
            return
            
        try:
            self.vsb.toggle_theme()
            self.hsb.toggle_theme()
        except RuntimeError:
            self._view_deleted = True
            self.view = None

def apply_scrollbars_to_graphics_view(view, bg_alpha=30, handle_alpha=80, 
                                     hover_alpha=120, pressed_alpha=160,
                                     scroll_bar_width=8, use_dark_theme=False, 
                                     auto_hide=True):
    """
    Применяет настраиваемые скроллбары к QGraphicsView
    
    Args:
        view: QGraphicsView, к которому нужно применить скроллбары
        bg_alpha: Прозрачность фона (0-255)
        handle_alpha: Прозрачность ползунка (0-255)
        hover_alpha: Прозрачность при наведении (0-255)
        pressed_alpha: Прозрачность при нажатии (0-255)
        scroll_bar_width: Ширина скроллбаров
        use_dark_theme: Использовать темную тему
        auto_hide: Автоматически скрывать скроллбары
    
    Returns:
        tuple: (vertical_scrollbar, horizontal_scrollbar)
    """
    # Создаем скроллбары
    vsb = GraphicsViewVerticalScrollBar(
        bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
        scroll_bar_width, use_dark_theme, auto_hide
    )
    
    hsb = GraphicsViewHorizontalScrollBar(
        bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
        scroll_bar_width, use_dark_theme, auto_hide
    )
    
    # Связываем с GraphicsView
    vsb.setGraphicsView(view)
    hsb.setGraphicsView(view)
    
    # Создаем менеджер для совместной работы скроллбаров
    if auto_hide:
        # Сохраняем ссылку на менеджер в атрибуте view для защиты от сборщика мусора
        view._scroll_manager = GraphicsViewScrollManager(view, vsb, hsb)
    
    return (vsb, hsb)


def toggle_graphics_view_scrollbar_theme(view, use_dark_theme=False):
    """
    Переключает тему скроллбаров QGraphicsView
    
    Args:
        view: QGraphicsView, для которого нужно переключить тему
        use_dark_theme: Использовать темную тему
    """
    if hasattr(view, '_scroll_manager'):
        view._scroll_manager.setTheme("dark" if use_dark_theme else "light") 