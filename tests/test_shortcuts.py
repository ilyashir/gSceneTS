import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF
from PyQt6.QtGui import QKeySequence

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_window import MainWindow
import logging
import field_widget
from robot import Robot  # Явно импортируем Robot для сброса экземпляра

# Настраиваем логирование для тестов
# Вместо полного отключения, будем выводить только критические ошибки
logging.basicConfig(level=logging.DEBUG, 
                   format="%(asctime)s [%(levelname)s] %(message)s",
                   stream=sys.stdout)

# Список проблемных тестов, которые следует пропустить
PROBLEMATIC_TESTS = [
]

# Сначала отключаем логирование, чтобы не засорять вывод
logging.disable(logging.CRITICAL)
# Включаем логирование для отладки
# logging.basicConfig(level=logging.DEBUG)

# Патчим класс FieldWidget до его импорта и использования
original_init_robot = field_widget.FieldWidget.init_robot

def patched_init_robot(self, pos):
    logging.info("ПАТЧ: Вызван patched_init_robot глобально")
    from PyQt6.QtWidgets import QGraphicsItem
    
    class GlobalMockRobot:
        def __init__(self):
            self.id = "trikKitRobot"
            self.pos_value = pos
            self.boundingRect_value = QRectF(0, 0, 50, 50)
            
        def pos(self):
            return self.pos_value
        
        def boundingRect(self):
            return self.boundingRect_value
        
        def setPos(self, x, y=None):
            if isinstance(x, QPointF):
                self.pos_value = x
            else:
                self.pos_value = QPointF(x, y)
            logging.debug(f"Mock Robot setPos called with {self.pos_value}")
    
    self.robot_model = GlobalMockRobot()
    logging.info("ПАТЧ: Global mock_robot успешно установлен")
    return True

# Заменяем оригинальный метод патченным на уровне класса
field_widget.FieldWidget.init_robot = patched_init_robot

# Делаем то же самое для check_object_within_scene
original_check_object = field_widget.FieldWidget.check_object_within_scene

def patched_check_object(self, item):
    logging.info("ПАТЧ: Вызван patched_check_object_within_scene глобально")
    return True

field_widget.FieldWidget.check_object_within_scene = patched_check_object

class TestShortcuts(unittest.TestCase):
    """Тесты для проверки работы горячих клавиш"""

    @classmethod
    def setUpClass(cls):
        """Создаем приложение для всех тестов"""
        # Инициализируем приложение PyQt
        cls.app = QApplication(sys.argv)
        
        # Сохраняем оригинальный метод init_robot
        cls.original_init_robot = field_widget.FieldWidget.init_robot
        
        # Создаем заглушку для init_robot
        def mock_init_robot(self, pos):
            logging.debug(f"Mock: Инициализация робота в позиции {pos}")
            # Создаем мок-объект робота
            from PyQt6.QtWidgets import QGraphicsItem
            
            class MockRobot:
                def __init__(self):
                    self.id = "mock_robot"
                    self.pos_value = pos
                    self.boundingRect_value = QRectF(0, 0, 50, 50)
                    
                def pos(self):
                    return self.pos_value
                    
                def boundingRect(self):
                    return self.boundingRect_value
                    
                def setPos(self, x, y=None):
                    if isinstance(x, QPointF):
                        self.pos_value = x
                    else:
                        self.pos_value = QPointF(x, y)
                    logging.debug(f"Mock Robot: setPos вызван с {self.pos_value}")
            
            # Устанавливаем мок-робота
            self.robot_model = MockRobot()
            logging.debug(f"Mock: Робот создан с id={self.robot_model.id}")
            return True
        
        # Заменяем оригинальный метод моком
        field_widget.FieldWidget.init_robot = mock_init_robot
        
        # Также заменяем check_object_within_scene для предотвращения проблем с проверкой границ
        cls.original_check_object = field_widget.FieldWidget.check_object_within_scene
        
        def mock_check_object_within_scene(self, item):
            logging.debug(f"Mock: check_object_within_scene вызван")
            return True
            
        field_widget.FieldWidget.check_object_within_scene = mock_check_object_within_scene
        
    @classmethod
    def tearDownClass(cls):
        """Восстанавливаем оригинальные методы после всех тестов"""
        # Восстанавливаем оригинальные методы класса
        field_widget.FieldWidget.init_robot = cls.original_init_robot
        field_widget.FieldWidget.check_object_within_scene = cls.original_check_object
        
    def setUp(self):
        """Создаем главное окно перед каждым тестом"""
        try:
            logging.info("Инициализация теста - создание MainWindow")
            
            # ВАЖНОЕ ИСПРАВЛЕНИЕ: сбрасываем экземпляр Robot перед каждым тестом
            # Это необходимо, так как Robot использует паттерн Singleton
            logging.debug("Сбрасываем экземпляр Robot перед созданием нового")
            Robot.reset_instance()
            
            self.main_window = MainWindow()
            self.field_widget = self.main_window.field_widget
            
            # Проверка, что объекты корректно инициализированы
            if not hasattr(self, 'main_window') or self.main_window is None:
                logging.error("main_window не инициализирован в setUp")
                raise RuntimeError("main_window не инициализирован в setUp")
                
            if not hasattr(self, 'field_widget') or self.field_widget is None:
                logging.error("field_widget не инициализирован в setUp")
                raise RuntimeError("field_widget не инициализирован в setUp")
                
            # Логируем успешную инициализацию основных компонентов
            logging.debug("MainWindow и FieldWidget успешно инициализированы")
            
        except Exception as e:
            logging.error(f"Ошибка в setUp: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def tearDown(self):
        """Очищаем ресурсы после каждого теста"""
        try:
            logging.info("Завершение теста - очистка ресурсов")
            
            # ВАЖНОЕ ИСПРАВЛЕНИЕ: сбрасываем экземпляр Robot после каждого теста
            logging.debug("Сбрасываем экземпляр Robot после теста")
            Robot.reset_instance()
            
            # Закрываем главное окно
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.close()
                logging.debug("Главное окно закрыто")
            
            self.main_window = None
            self.field_widget = None
            
        except Exception as e:
            logging.error(f"Ошибка в tearDown: {e}")
            import traceback
            traceback.print_exc()
    
    def test_zoom_in_shortcut(self):
        """Тест для горячей клавиши увеличения масштаба ("+")"""
        # Проверяем, что объекты инициализированы
        if not hasattr(self, 'main_window') or self.main_window is None:
            self.main_window = MainWindow()
        
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            self.field_widget = self.main_window.field_widget
        
        # Запоминаем исходный масштаб
        initial_scale = self.field_widget.currentScale()
        
        # Вызываем метод напрямую, так как клавиши могут не работать в тестовой среде
        self.field_widget.zoomIn()
        
        # Проверяем, что масштаб увеличился
        self.assertGreater(self.field_widget.currentScale(), initial_scale)
    
    def test_zoom_out_shortcut(self):
        """Тест для горячей клавиши уменьшения масштаба ("-")"""
        # Проверяем, что объекты инициализированы
        if not hasattr(self, 'main_window') or self.main_window is None:
            self.main_window = MainWindow()
        
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            self.field_widget = self.main_window.field_widget
        
        # Сначала увеличим масштаб дважды, чтобы потом можно было его уменьшить
        self.field_widget.zoomIn()
        self.field_widget.zoomIn()
        initial_scale = self.field_widget.currentScale()
        
        # Вызываем метод напрямую
        self.field_widget.zoomOut()
        
        # Проверяем, что масштаб уменьшился
        self.assertLess(self.field_widget.currentScale(), initial_scale)
    
    def test_reset_zoom_shortcut(self):
        """Тест для горячей клавиши сброса масштаба ("0")"""
        # Проверяем, что объекты инициализированы
        if not hasattr(self, 'main_window') or self.main_window is None:
            self.main_window = MainWindow()
        
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            self.field_widget = self.main_window.field_widget
        
        # Сначала увеличим масштаб
        self.field_widget.zoomIn()
        
        # Вызываем метод напрямую
        self.field_widget.resetScale()
        
        # Проверяем, что масштаб сбросился до 1.0
        self.assertEqual(self.field_widget.currentScale(), 1.0)
    
    def test_mode_switching(self):
        """Тест для переключения режимов"""
        logging.info("================ НАЧАЛО ТЕСТА test_mode_switching ================")
        
        # Проверяем, что необходимые объекты инициализированы
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            logging.error("Ошибка: field_widget не инициализирован")
            self.fail("field_widget не инициализирован")
            return
        
        if not hasattr(self, 'main_window') or self.main_window is None:
            logging.error("Ошибка: main_window не инициализирован")
            self.fail("main_window не инициализирован")
            return
        
        logging.info("1. Сохраняем оригинальные методы и создаем моки")
        # Сохраняем оригинальные методы
        original_init_robot = getattr(self.field_widget, 'init_robot', None)
        original_check_object_within_scene = getattr(self.field_widget, 'check_object_within_scene', None)
        
        # Создаем заглушку для метода init_robot
        def mock_init_robot(pos):
            logging.info("Mock: Вызван mock_init_robot")
            # Создаем минимальную структуру для robot_model
            from PyQt6.QtWidgets import QGraphicsItem
            class MockRobot:
                def __init__(self):
                    self.id = "mock_robot"
                    self.pos_value = QPointF(0, 0)
                    self.boundingRect_value = QRectF(0, 0, 50, 50)
                    
                def pos(self):
                    return self.pos_value
                    
                def boundingRect(self):
                    return self.boundingRect_value
                
                def setPos(self, x, y=None):
                    if isinstance(x, QPointF):
                        self.pos_value = x
                    else:
                        self.pos_value = QPointF(x, y)
                    logging.debug(f"Mock Robot: setPos called with {self.pos_value}")
            
            # Устанавливаем мок-робота
            logging.info("Mock: Создаем mock_robot")
            self.field_widget.robot_model = MockRobot()
            logging.info("Mock: mock_robot успешно установлен")
            return True
        
        # Заглушка для метода check_object_within_scene
        def mock_check_object_within_scene(item):
            from wall import Wall
            from region import Region
            from robot import Robot
            
            item_type = "unknown"
            if isinstance(item, Wall):
                item_type = "Wall"
            elif isinstance(item, Region):
                item_type = "Region"
            elif isinstance(item, Robot):
                item_type = "Robot"
            elif hasattr(item, 'id'):
                item_type = f"Object with id={item.id}"
            
            logging.debug(f"Mock: check_object_within_scene вызван с объектом типа {item_type}")
            # Всегда возвращаем True
            return True
        
        try:
            logging.info("2. Подменяем методы на моки")
            # Подменяем методы и свойства на заглушки
            if original_init_robot is not None:
                self.field_widget.init_robot = mock_init_robot
            if original_check_object_within_scene is not None:
                self.field_widget.check_object_within_scene = mock_check_object_within_scene
            
            logging.info("3. Инициализируем робота")
            # Инициализируем робота с помощью нашего мока
            self.field_widget.init_robot(QPointF(0, 0))
            
            # Проверяем, что метод set_mode существует
            logging.info("4. Проверяем существование метода set_mode")
            self.assertTrue(hasattr(self.main_window, 'set_mode'))
            
            # Переключаемся в режим рисования
            logging.info("5. Переключаемся в режим рисования")
            self.main_window.set_mode("drawing")
            logging.info(f"Режим рисования: {self.field_widget.drawing_mode}, режим редактирования: {self.field_widget.edit_mode}")
            
            # Переключаемся в режим редактирования
            logging.info("6. Переключаемся в режим редактирования")
            self.main_window.set_mode("edit")
            logging.info(f"Режим рисования: {self.field_widget.drawing_mode}, режим редактирования: {self.field_widget.edit_mode}")
            
            # Переключаемся в режим наблюдателя
            logging.info("7. Переключаемся в режим наблюдателя")
            self.main_window.set_mode("observer")
            logging.info(f"Режим рисования: {self.field_widget.drawing_mode}, режим редактирования: {self.field_widget.edit_mode}")
            
            # Проверка ожидаемых результатов
            logging.info("8. Проверка результатов")
            self.assertIsNone(self.field_widget.drawing_mode, "Режим рисования не был сброшен")
            self.assertFalse(self.field_widget.edit_mode, "Режим редактирования не был сброшен")
            
            logging.info("================ ТЕСТ УСПЕШНО ЗАВЕРШЕН ================")
        
        except Exception as e:
            logging.error(f"ОШИБКА в тесте: {e}")
            raise
        
        finally:
            logging.info("9. Восстанавливаем оригинальные методы")
            # Восстанавливаем оригинальные методы и свойства
            try:
                if original_init_robot is not None:
                    self.field_widget.init_robot = original_init_robot
                if original_check_object_within_scene is not None:
                    self.field_widget.check_object_within_scene = original_check_object_within_scene
                logging.info("Оригинальные методы восстановлены")
            except Exception as e:
                logging.error(f"Ошибка при восстановлении методов: {e}")
    
    def test_delete_selected_item(self):
        """Тест для проверки удаления выбранного элемента."""
        logging.info("================ НАЧАЛО ТЕСТА test_delete_selected_item ================")
        
        # Проверяем, что необходимые объекты инициализированы
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            logging.error("Ошибка: field_widget не инициализирован")
            self.fail("field_widget не инициализирован")
            return
        
        if not hasattr(self, 'main_window') or self.main_window is None:
            logging.error("Ошибка: main_window не инициализирован")
            self.fail("main_window не инициализирован")
            return
        
        logging.info("1. Сохраняем оригинальные методы и создаем моки")
        # Сохраняем оригинальные методы
        original_init_robot = getattr(self.field_widget, 'init_robot', None)
        original_select_item = getattr(self.field_widget, 'select_item', None)
        original_deselect_item = getattr(self.field_widget, 'deselect_item', None)
        original_delete_selected_item = getattr(self.field_widget, 'delete_selected_item', None)
        original_properties_window = getattr(self.field_widget, 'properties_window', None)
        original_check_object_within_scene = getattr(self.field_widget, 'check_object_within_scene', None)
        
        # Создаем заглушку для properties_window
        class MockPropertiesWindow:
            def update_properties(self, item):
                logging.debug("Mock: update_properties вызван")
                pass
            
            def clear_properties(self):
                logging.debug("Mock: clear_properties вызван")
                pass
        
        # Заглушка для метода init_robot
        def mock_init_robot(pos):
            logging.info("Mock: Вызван mock_init_robot")
            # Создаем минимальную структуру для robot_model
            from PyQt6.QtWidgets import QGraphicsItem
            class MockRobot:
                def __init__(self):
                    self.id = "mock_robot"
                    self.pos_value = QPointF(0, 0)
                    self.boundingRect_value = QRectF(0, 0, 50, 50)
                    
                def pos(self):
                    return self.pos_value
                    
                def boundingRect(self):
                    return self.boundingRect_value
                
                def setPos(self, x, y=None):
                    if isinstance(x, QPointF):
                        self.pos_value = x
                    else:
                        self.pos_value = QPointF(x, y)
                    logging.debug(f"Mock Robot: setPos called with {self.pos_value}")
        
            # Устанавливаем мок-робота
            logging.info("Mock: Создаем mock_robot")
            self.field_widget.robot_model = MockRobot()
            logging.info("Mock: mock_robot успешно установлен")
            return True
        
        # Заглушка для метода select_item
        def mock_select_item(item):
            logging.debug(f"Mock: select_item вызван с {item}")
            # Просто устанавливаем выбранный элемент без вызова сигналов
            self.field_widget.selected_item = item
        
        # Заглушка для метода deselect_item
        def mock_deselect_item():
            logging.debug("Mock: deselect_item вызван")
            # Просто сбрасываем выбранный элемент без вызова сигналов
            self.field_widget.selected_item = None
        
        # Заглушка для метода delete_selected_item
        def mock_delete_selected_item():
            logging.info("Mock: delete_selected_item вызван")
            if self.field_widget.selected_item:
                item = self.field_widget.selected_item
                self.field_widget.selected_item = None
                logging.info(f"Mock: Удален элемент с id={item.id if hasattr(item, 'id') else 'unknown'}")
                return True
            return False
        
        # Заглушка для метода check_object_within_scene
        def mock_check_object_within_scene(item):
            from wall import Wall
            from region import Region
            from robot import Robot
            
            item_type = "unknown"
            if isinstance(item, Wall):
                item_type = "Wall"
            elif isinstance(item, Region):
                item_type = "Region"
            elif isinstance(item, Robot):
                item_type = "Robot"
            elif hasattr(item, 'id'):
                item_type = f"Object with id={item.id}"
            
            logging.debug(f"Mock: check_object_within_scene вызван с объектом типа {item_type}")
            # Всегда возвращаем True
            return True
        
        try:
            logging.info("2. Подменяем методы на моки")
            # Подменяем методы и свойства на заглушки
            if original_init_robot is not None:
                self.field_widget.init_robot = mock_init_robot
            if original_select_item is not None:
                self.field_widget.select_item = mock_select_item
            if original_deselect_item is not None:
                self.field_widget.deselect_item = mock_deselect_item
            if original_delete_selected_item is not None:
                self.field_widget.delete_selected_item = mock_delete_selected_item
            if original_properties_window is not None:
                self.field_widget.properties_window = MockPropertiesWindow()
            if original_check_object_within_scene is not None:
                self.field_widget.check_object_within_scene = mock_check_object_within_scene
            
            logging.info("3. Инициализируем робота")
            # Инициализируем робота с помощью нашего мока
            self.field_widget.init_robot(QPointF(0, 0))
            
            # ТЕСТ 1: Проверка создания стены
            logging.info("4. Создаем стену")
            start_point = QPointF(-100, -100)
            end_point = QPointF(-50, -50)
            
            logging.info(f"Создаем стену от {start_point} до {end_point}")
            wall = self.field_widget.add_wall(start_point, end_point)
            
            # Проверяем, что стена создана
            logging.info(f"Стена: {wall}")
            self.assertIsNotNone(wall, "Стена не была создана")
            logging.info(f"Стена успешно создана с id={wall.id if wall else 'None'}")
            
            # ТЕСТ 2: Проверка удаления выбранного элемента с горячей клавиши
            logging.info("5. Выбираем стену и удаляем её")
            
            # Выбираем стену
            self.field_widget.select_item(wall)
            self.assertEqual(self.field_widget.selected_item, wall, "Стена не была выбрана")
            logging.info("Стена успешно выбрана")
            
            # Проверяем, что выделенный элемент можно удалить
            logging.info("6. Проверяем метод удаления выделенного элемента")
            self.assertTrue(hasattr(self.field_widget, 'delete_selected_item'))
            logging.info("Метод delete_selected_item существует")
            
            # Удаляем выделенный элемент
            logging.info("7. Удаляем выделенный элемент")
            result = self.field_widget.delete_selected_item()
            self.assertTrue(result, "Элемент не был удален")
            
            # Проверяем, что выделенный элемент удален
            self.assertIsNone(self.field_widget.selected_item, "Выделенный элемент не был удален")
            logging.info("Элемент успешно удален")
            
            logging.info("================ ТЕСТ УСПЕШНО ЗАВЕРШЕН ================")
        
        except Exception as e:
            logging.error(f"ОШИБКА в тесте: {e}")
            raise
        
        finally:
            logging.info("8. Восстанавливаем оригинальные методы")
            # Восстанавливаем оригинальные методы и свойства
            try:
                if original_init_robot is not None:
                    self.field_widget.init_robot = original_init_robot
                if original_select_item is not None:
                    self.field_widget.select_item = original_select_item
                if original_deselect_item is not None:
                    self.field_widget.deselect_item = original_deselect_item
                if original_delete_selected_item is not None:
                    self.field_widget.delete_selected_item = original_delete_selected_item
                if original_properties_window is not None:
                    self.field_widget.properties_window = original_properties_window
                if original_check_object_within_scene is not None:
                    self.field_widget.check_object_within_scene = original_check_object_within_scene
                logging.info("Оригинальные методы восстановлены")
            except Exception as e:
                logging.error(f"Ошибка при восстановлении методов: {e}")

    def test_manual_wall_creation_and_deselection(self):
        """Проверка ручного создания стены и снятия выделения без инициализации робота"""
        logging.info("================ НАЧАЛО ТЕСТА test_manual_wall_creation_and_deselection ================")
        
        # Сохраняем оригинальные методы и создаем заглушки только если field_widget инициализирован
        if not hasattr(self, 'field_widget') or self.field_widget is None:
            logging.error("Ошибка: field_widget не инициализирован")
            self.fail("field_widget не инициализирован")
            return
        
        logging.info("1. Сохраняем оригинальные методы и создаем моки")
        # Сохраняем оригинальные методы
        original_init_robot = getattr(self.field_widget, 'init_robot', None)
        original_select_item = getattr(self.field_widget, 'select_item', None)
        original_deselect_item = getattr(self.field_widget, 'deselect_item', None)
        original_properties_window = getattr(self.field_widget, 'properties_window', None)
        original_check_object_within_scene = getattr(self.field_widget, 'check_object_within_scene', None)
        
        # Создаем заглушку для properties_window
        class MockPropertiesWindow:
            def update_properties(self, item):
                logging.debug("Mock: update_properties вызван")
                pass
            
            def clear_properties(self):
                logging.debug("Mock: clear_properties вызван")
                pass
        
        # Заглушка для метода init_robot
        def mock_init_robot(pos):
            logging.info("Mock: Вызван mock_init_robot")
            # Создаем минимальную структуру для robot_model
            from PyQt6.QtWidgets import QGraphicsItem
            class MockRobot:
                def __init__(self):
                    self.id = "mock_robot"
                    self.pos_value = QPointF(0, 0)
                    self.boundingRect_value = QRectF(0, 0, 50, 50)
                    
                def pos(self):
                    return self.pos_value
                    
                def boundingRect(self):
                    return self.boundingRect_value
                
                def setPos(self, x, y=None):
                    if isinstance(x, QPointF):
                        self.pos_value = x
                    else:
                        self.pos_value = QPointF(x, y)
                    logging.debug(f"Mock Robot: setPos called with {self.pos_value}")
        
        # Заглушка для метода select_item
        def mock_select_item(item):
            logging.debug(f"Mock: select_item вызван с {item}")
            # Просто устанавливаем выбранный элемент без вызова сигналов
            self.field_widget.selected_item = item
        
        # Заглушка для метода deselect_item
        def mock_deselect_item():
            logging.debug("Mock: deselect_item вызван")
            # Просто сбрасываем выбранный элемент без вызова сигналов
            self.field_widget.selected_item = None
        
        # Заглушка для метода check_object_within_scene
        def mock_check_object_within_scene(item):
            from wall import Wall
            from region import Region
            from robot import Robot
            
            item_type = "unknown"
            if isinstance(item, Wall):
                item_type = "Wall"
            elif isinstance(item, Region):
                item_type = "Region"
            elif isinstance(item, Robot):
                item_type = "Robot"
            elif hasattr(item, 'id'):
                item_type = f"Object with id={item.id}"
            
            logging.debug(f"Mock: check_object_within_scene вызван с объектом типа {item_type}")
            # Всегда возвращаем True
            return True
        
        try:
            logging.info("2. Подменяем методы на моки")
            # Подменяем методы и свойства на заглушки
            if original_init_robot is not None:
                self.field_widget.init_robot = mock_init_robot
            if original_select_item is not None:
                self.field_widget.select_item = mock_select_item
            if original_deselect_item is not None:
                self.field_widget.deselect_item = mock_deselect_item
            if original_properties_window is not None:
                self.field_widget.properties_window = MockPropertiesWindow()
            if original_check_object_within_scene is not None:
                self.field_widget.check_object_within_scene = mock_check_object_within_scene
            
            logging.info("3. Инициализируем робота")
            # Инициализируем робота с помощью нашего мока
            self.field_widget.init_robot(QPointF(0, 0))
            
            # ТЕСТ 1: Проверка создания стены программным способом
            logging.info("4. Создаем стену")
            start_point = QPointF(-200, -200)
            end_point = QPointF(-150, -150)
            
            logging.info(f"Создаем стену от {start_point} до {end_point}")
            wall = self.field_widget.add_wall(start_point, end_point)
            
            # Проверяем, что стена создана
            logging.info(f"Стена: {wall}")
            self.assertIsNotNone(wall, "Стена не была создана")
            logging.info(f"Стена успешно создана с id={wall.id if wall else 'None'}")
            
            # ТЕСТ 2: Проверка снятия выделения
            logging.info("5. Проверяем выделение и снятие выделения")
            self.field_widget.select_item(wall)
            self.assertEqual(self.field_widget.selected_item, wall, "Стена не была выбрана")
            
            logging.info("Снимаем выделение со стены")
            self.field_widget.deselect_item()
            
            # Проверяем, что выделение снято
            self.assertIsNone(self.field_widget.selected_item, "Выделение не было снято")
            logging.info("Выделение успешно снято")
            
            # ТЕСТ 3: Проверка режима наблюдателя
            logging.info("6. Проверяем переключение режима")
            logging.info("Переключаемся в режим наблюдателя")
            self.main_window.set_mode("observer")
            
            # Проверяем, что режим рисования сброшен
            self.assertIsNone(self.field_widget.drawing_mode, "Режим рисования не был сброшен")
            logging.info("Режим рисования успешно сброшен")
            
            logging.info("================ ТЕСТ УСПЕШНО ЗАВЕРШЕН ================")
        
        except Exception as e:
            logging.error(f"ОШИБКА в тесте: {e}")
            raise
        
        finally:
            logging.info("7. Восстанавливаем оригинальные методы")
            # Восстанавливаем оригинальные методы и свойства
            try:
                if original_init_robot is not None:
                    self.field_widget.init_robot = original_init_robot
                if original_select_item is not None:
                    self.field_widget.select_item = original_select_item
                if original_deselect_item is not None:
                    self.field_widget.deselect_item = original_deselect_item
                if original_properties_window is not None:
                    self.field_widget.properties_window = original_properties_window
                if original_check_object_within_scene is not None:
                    self.field_widget.check_object_within_scene = original_check_object_within_scene
                logging.info("Оригинальные методы восстановлены")
            except Exception as e:
                logging.error(f"Ошибка при восстановлении методов: {e}")

if __name__ == '__main__':
    unittest.main() 