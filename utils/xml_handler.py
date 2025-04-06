"""
Модуль для работы с XML-файлами сцен.
Включает функции для экспорта, импорта и валидации.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
import re
from PyQt6.QtCore import QRectF, QPointF, QLineF

# Настройка логгера
logger = logging.getLogger(__name__)

# Версия формата XML
XML_FORMAT_VERSION = "1.0"

class XMLValidationError(Exception):
    """Исключение, вызываемое при ошибке валидации XML"""
    pass

class XMLHandler:
    """
    Класс для обработки XML-файлов: экспорт, импорт и валидация.
    """

    def __init__(self, scene_width=1300, scene_height=1000):
        """
        Инициализация обработчика XML.
        
        Args:
            scene_width: Ширина сцены по умолчанию
            scene_height: Высота сцены по умолчанию
        """
        self.scene_width = scene_width
        self.scene_height = scene_height
        
        # Допустимые диапазоны значений
        self.min_x = -self.scene_width // 2
        self.max_x = self.scene_width // 2
        self.min_y = -self.scene_height // 2
        self.max_y = self.scene_height // 2
        
        # Словарь для хранения уникальных идентификаторов
        self.ids = {}
        
    def _reset_ids(self):
        """Сбрасывает словарь идентификаторов"""
        self.ids = {}
        
    def _parse_coords(self, coords_str):
        """
        Парсит строку координат вида "x:y".
        
        Args:
            coords_str: Строка с координатами в формате "x:y"
            
        Returns:
            tuple: (x, y) - координаты точки
            
        Raises:
            ValueError: Если формат координат некорректен
        """
        if not coords_str or not isinstance(coords_str, str):
            raise ValueError(f"Некорректный формат координат: {coords_str}")
            
        # Проверяем формат на соответствие шаблону x:y
        if not re.match(r'^-?\d+(\.\d+)?:-?\d+(\.\d+)?$', coords_str):
            raise ValueError(f"Некорректный формат координат: {coords_str}")
            
        try:
            x, y = coords_str.split(':')
            return float(x), float(y)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Ошибка при парсинге координат '{coords_str}': {e}")
    
    def validate_coordinates(self, x, y):
        """
        Проверяет, находятся ли координаты в допустимом диапазоне.
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            bool: True, если координаты в допустимом диапазоне
            
        Raises:
            XMLValidationError: Если координаты вне допустимого диапазона
        """
        if not (self.min_x <= x <= self.max_x):
            raise XMLValidationError(f"Координата X ({x}) вне допустимого диапазона [{self.min_x}, {self.max_x}]")
        
        if not (self.min_y <= y <= self.max_y):
            raise XMLValidationError(f"Координата Y ({y}) вне допустимого диапазона [{self.min_y}, {self.max_y}]")
            
        return True
    
    def validate_id(self, id_str, object_type):
        """
        Проверяет уникальность идентификатора.
        
        Args:
            id_str: Строковое представление идентификатора (w1, r2, m3, etc.)
            object_type: Тип объекта (wall, region, robot)
            
        Returns:
            bool: True, если идентификатор уникален
            
        Raises:
            XMLValidationError: Если идентификатор уже используется
        """
        if not id_str or not isinstance(id_str, str):
            raise XMLValidationError(f"Некорректный идентификатор: {id_str}")
        
        # Извлекаем числовой ID из строкового представления
        prefix_map = {
            'wall': 'w',
            'region': 'r',
            'robot': 'm'
        }
        expected_prefix = prefix_map.get(object_type)
        
        try:
            # Если ID начинается с префикса (w, r, m), убираем его
            if expected_prefix and id_str.startswith(expected_prefix):
                id_num = int(id_str[1:])
            else:
                # Иначе пробуем преобразовать весь ID в число
                id_num = int(id_str)
                
            if id_num < 0:
                raise XMLValidationError(f"Идентификатор должен быть положительным числом: {id_str}")
        except (ValueError, TypeError):
            raise XMLValidationError(f"Идентификатор должен быть целым числом: {id_str}")
            
        # Проверяем уникальность идентификатора
        key = f"{object_type}_{id_num}"
        if key in self.ids:
            raise XMLValidationError(f"Идентификатор '{id_str}' для объекта типа '{object_type}' уже используется")
            
        # Сохраняем идентификатор для проверки уникальности
        self.ids[key] = True
        
        return True
    
    def extract_numeric_id(self, id_str, object_type):
        """
        Извлекает числовой ID из строкового представления.
        
        Args:
            id_str: Строковое представление идентификатора (w1, r2, m3, etc.)
            object_type: Тип объекта (wall, region, robot)
            
        Returns:
            int: Числовое значение ID
            
        Raises:
            XMLValidationError: Если идентификатор имеет неверный формат
        """
        prefix_map = {
            'wall': 'w',
            'region': 'r',
            'robot': 'm'
        }
        expected_prefix = prefix_map.get(object_type)
        
        try:
            # Если ID начинается с префикса (w, r, m), убираем его
            if expected_prefix and id_str.startswith(expected_prefix):
                id_num = int(id_str[1:])
            else:
                # Иначе пробуем преобразовать весь ID в число
                id_num = int(id_str)
                
            if id_num < 0:
                raise XMLValidationError(f"Идентификатор должен быть положительным числом: {id_str}")
                
            return id_num
        except (ValueError, TypeError):
            raise XMLValidationError(f"Идентификатор должен быть целым числом: {id_str}")
    
    def validate_wall(self, begin_coords, end_coords, id_str):
        """
        Проверяет корректность данных стены.
        
        Args:
            begin_coords: Координаты начала стены в формате "x:y"
            end_coords: Координаты конца стены в формате "x:y"
            id_str: Идентификатор стены
            
        Returns:
            tuple: ((x1, y1), (x2, y2), id_int) - координаты и идентификатор
            
        Raises:
            XMLValidationError: Если данные некорректны
        """
        try:
            x1, y1 = self._parse_coords(begin_coords)
            x2, y2 = self._parse_coords(end_coords)
            
            # Проверяем, что координаты в допустимом диапазоне
            self.validate_coordinates(x1, y1)
            self.validate_coordinates(x2, y2)
            
            # Проверяем, что идентификатор уникален
            self.validate_id(id_str, "wall")
            
            # Проверяем, что точки не совпадают
            if x1 == x2 and y1 == y2:
                raise XMLValidationError(f"Начало и конец стены не могут совпадать: {begin_coords} and {end_coords}")
                
            return (x1, y1), (x2, y2), int(id_str)
            
        except ValueError as e:
            raise XMLValidationError(f"Ошибка при проверке стены: {e}")
    
    def validate_region(self, x_str, y_str, width_str, height_str, id_str, color_str=None):
        """
        Проверяет корректность данных региона.
        
        Args:
            x_str: Координата X левого верхнего угла
            y_str: Координата Y левого верхнего угла
            width_str: Ширина региона
            height_str: Высота региона
            id_str: Идентификатор региона
            color_str: Цвет региона (опционально)
            
        Returns:
            tuple: (x, y, width, height, id_int, color) - параметры региона
            
        Raises:
            XMLValidationError: Если данные некорректны
        """
        try:
            x = float(x_str)
            y = float(y_str)
            width = float(width_str)
            height = float(height_str)
            
            # Проверяем, что координаты в допустимом диапазоне
            self.validate_coordinates(x, y)
            self.validate_coordinates(x + width, y + height)
            
            # Проверяем, что размеры положительные
            if width <= 0 or height <= 0:
                raise XMLValidationError(f"Размеры региона должны быть положительными: ширина={width}, высота={height}")
                
            # Проверяем, что идентификатор уникален
            self.validate_id(id_str, "region")
            
            # Проверяем, что цвет имеет правильный формат (если указан)
            color = None
            if color_str:
                color = color_str
                # Здесь можно добавить валидацию формата цвета, если нужно
                
            return x, y, width, height, int(id_str), color
            
        except ValueError as e:
            raise XMLValidationError(f"Ошибка при проверке региона: {e}")
    
    def validate_robot(self, position_coords):
        """
        Проверяет корректность данных робота.
        
        Args:
            position_coords: Координаты позиции робота в формате "x:y"
            
        Returns:
            tuple: (x, y) - координаты позиции
            
        Raises:
            XMLValidationError: Если данные некорректны
        """
        try:
            x, y = self._parse_coords(position_coords)
            
            # Проверяем, что координаты в допустимом диапазоне
            self.validate_coordinates(x, y)
            
            return x, y
            
        except ValueError as e:
            raise XMLValidationError(f"Ошибка при проверке робота: {e}")
    
    def validate_root_element(self, root):
        """
        Проверяет корректность корневого элемента.
        
        Args:
            root: Корневой элемент XML
            
        Returns:
            ET.Element: Корневой элемент
            
        Raises:
            XMLValidationError: Если структура корневого элемента некорректна
        """
        # Проверяем, что корневой элемент существует и имеет тег "root"
        if root is None or root.tag != "root":
            raise XMLValidationError("Некорректный формат XML: отсутствует корневой элемент 'root'")
            
        # Проверяем наличие атрибута version (опционально)
        version = root.get("version", "1.0")
        logger.debug(f"Версия XML: {version}")
        
        # Проверяем наличие элемента world
        world = root.find("world")
        if world is None:
            raise XMLValidationError("Некорректный формат XML: отсутствует элемент 'world'")
            
        return root
    
    def generate_xml(self, walls, regions, robot_model=None, start_position=None):
        """
        Генерирует XML на основе объектов сцены.
        
        Args:
            walls: Список стен
            regions: Список регионов
            robot_model: Объект робота
            start_position: Объект стартовой позиции
            
        Returns:
            str: Форматированный XML
            
        Raises:
            XMLValidationError: Если данные не проходят валидацию
        """
        self._reset_ids()  # Сбрасываем словарь идентификаторов
        
        # Создаем корневой элемент
        root = ET.Element("root")
        root.set("version", XML_FORMAT_VERSION)
        
        # Добавляем элемент размера сцены
        world = ET.SubElement(root, "world")
        world.set("width", str(self.scene_width))
        world.set("height", str(self.scene_height))
        
        # Добавляем элемент для стен
        walls_element = ET.SubElement(root, "walls")
        
        # Добавляем каждую стену
        for wall in walls:
            wall_element = ET.SubElement(walls_element, "wall")
            
            # Получаем числовой ID стены (без префикса 'w')
            wall_id = self.extract_numeric_id(wall.id, "wall")
            
            # Получаем координаты стены
            line = wall.line()
            
            # Проверяем, что ID и координаты валидны
            try:
                (x1, y1), (x2, y2), _ = self.validate_wall(
                    f"{line.x1()}:{line.y1()}", 
                    f"{line.x2()}:{line.y2()}",
                    str(wall_id)
                )
            except XMLValidationError as e:
                logger.warning(f"Стена {wall.id} не прошла валидацию: {e}")
                continue
                
            # Добавляем атрибуты стены
            wall_element.set("id", str(wall_id))
            wall_element.set("begin", f"{x1}:{y1}")
            wall_element.set("end", f"{x2}:{y2}")
        
        # Добавляем элемент для регионов
        regions_element = ET.SubElement(root, "regions")
        
        # Добавляем каждый регион
        for region in regions:
            region_element = ET.SubElement(regions_element, "region")
            
            # Получаем числовой ID региона (без префикса 'r')
            region_id = self.extract_numeric_id(region.id, "region")
            
            # Получаем координаты и размеры региона
            rect = region.path().boundingRect()
            
            # Проверяем, что ID и координаты валидны
            try:
                x, y, width, height, _, color = self.validate_region(
                    str(rect.x()),
                    str(rect.y()),
                    str(rect.width()),
                    str(rect.height()),
                    str(region_id),
                    region.color
                )
            except XMLValidationError as e:
                logger.warning(f"Регион {region.id} не прошел валидацию: {e}")
                continue
                
            # Добавляем атрибуты региона
            region_element.set("id", str(region_id))
            region_element.set("x", str(x))
            region_element.set("y", str(y))
            region_element.set("width", str(width))
            region_element.set("height", str(height))
            
            # Добавляем цвет, если он задан
            if color:
                region_element.set("color", color)
        
        # Добавляем элемент для роботов (если есть)
        if robot_model:
            robots_element = ET.SubElement(root, "robots")
            robot_element = ET.SubElement(robots_element, "robot")
            
            # ID робота всегда 1
            robot_id = 1
            
            # Получаем позицию и направление робота
            robot_pos = robot_model.pos()
            
            # Проверяем, что координаты валидны
            try:
                x, y = self.validate_robot(f"{robot_pos.x()}:{robot_pos.y()}")
            except XMLValidationError as e:
                logger.warning(f"Робот {robot_model.id} не прошел валидацию: {e}")
            else:
                # Добавляем атрибуты робота
                robot_element.set("id", str(robot_id))
                robot_element.set("position", f"{x}:{y}")
                robot_element.set("direction", str(robot_model.direction))
                
                # Добавляем имя робота, если оно задано
                if hasattr(robot_model, 'name') and robot_model.name:
                    robot_element.set("name", robot_model.name)
                
                # Добавляем стартовую позицию, если она есть
                if start_position:
                    start_pos_element = ET.SubElement(robot_element, "startPosition")
                    start_pos_element.set("id", start_position.id)
                    start_pos_element.set("x", str(int(start_position.pos().x())))
                    start_pos_element.set("y", str(int(start_position.pos().y())))
                    start_pos_element.set("direction", str(int(start_position.direction())))
        
        # Преобразуем XML в строку с отступами
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        formatted_xml = dom.toprettyxml(indent="  ")
        
        return formatted_xml
            
    def parse_xml(self, xml_content):
        """
        Парсит XML контент и возвращает данные для создания объектов сцены.
        
        Args:
            xml_content: Строка с XML контентом
            
        Returns:
            dict: Словарь с данными сцены
            
        Raises:
            XMLValidationError: Если XML не проходит валидацию
        """
        try:
            # Парсим XML
            root = ET.fromstring(xml_content)
            
            # Проверяем корневой элемент
            self.validate_root_element(root)
            
            # Получаем размеры сцены
            world = root.find("world")
            scene_width = int(world.get("width", self.scene_width))
            scene_height = int(world.get("height", self.scene_height))
            
            # Обновляем размеры сцены
            self.scene_width = scene_width
            self.scene_height = scene_height
            self.min_x = -self.scene_width // 2
            self.max_x = self.scene_width // 2
            self.min_y = -self.scene_height // 2
            self.max_y = self.scene_height // 2
            
            # Сбрасываем словарь идентификаторов
            self._reset_ids()
            
            # Извлекаем данные о стенах
            walls_data = []
            walls_element = root.find("walls")
            if walls_element is not None:
                for wall in walls_element.findall("wall"):
                    id_str = wall.get("id")
                    begin = wall.get("begin")
                    end = wall.get("end")
                    
                    try:
                        (x1, y1), (x2, y2), wall_id = self.validate_wall(begin, end, id_str)
                        walls_data.append({
                            "id": wall_id,
                            "begin": (x1, y1),
                            "end": (x2, y2)
                        })
                    except XMLValidationError as e:
                        logger.warning(f"Стена с ID {id_str} не прошла валидацию: {e}")
            
            # Извлекаем данные о регионах
            regions_data = []
            regions_element = root.find("regions")
            if regions_element is not None:
                for region in regions_element.findall("region"):
                    id_str = region.get("id")
                    x = region.get("x")
                    y = region.get("y")
                    width = region.get("width")
                    height = region.get("height")
                    color = region.get("color")
                    
                    try:
                        x, y, width, height, region_id, color = self.validate_region(
                            x, y, width, height, id_str, color
                        )
                        regions_data.append({
                            "id": region_id,
                            "rect": QRectF(x, y, width, height),
                            "color": color
                        })
                    except XMLValidationError as e:
                        logger.warning(f"Регион с ID {id_str} не прошел валидацию: {e}")
            
            # Извлекаем данные о роботах
            robot_data = None
            start_position_data = None
            robots_element = root.find("robots")
            if robots_element is not None:
                robot = robots_element.find("robot")
                if robot is not None:
                    id_str = robot.get("id")
                    position = robot.get("position")
                    direction = float(robot.get("direction", 0))
                    name = robot.get("name", "")
                    
                    try:
                        robot_id = int(id_str)
                        self.validate_id(id_str, "robot")
                        x, y = self.validate_robot(position)
                        robot_data = {
                            "id": robot_id,
                            "position": QPointF(x, y),
                            "direction": direction,
                            "name": name
                        }
                        
                        # Парсим стартовую позицию, если она есть
                        start_position = robot.find("startPosition")
                        if start_position is not None:
                            start_id = start_position.get("id", "startPosition")
                            start_x = int(start_position.get("x", 25))
                            start_y = int(start_position.get("y", 25))
                            start_direction = float(start_position.get("direction", 0))
                            
                            # Проверяем координаты стартовой позиции
                            try:
                                self.validate_coordinates(start_x, start_y)
                                start_position_data = {
                                    "id": start_id,
                                    "x": start_x,
                                    "y": start_y,
                                    "direction": start_direction
                                }
                            except XMLValidationError as e:
                                logger.warning(f"Стартовая позиция не прошла валидацию: {e}")
                        
                    except XMLValidationError as e:
                        logger.warning(f"Робот с ID {id_str} не прошел валидацию: {e}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Ошибка при разборе данных робота с ID {id_str}: {e}")
            
            return {
                "scene_width": scene_width,
                "scene_height": scene_height,
                "walls": walls_data,
                "regions": regions_data,
                "robot": robot_data,
                "start_position": start_position_data
            }
            
        except ET.ParseError as e:
            raise XMLValidationError(f"Ошибка при парсинге XML: {e}")
        except Exception as e:
            raise XMLValidationError(f"Неизвестная ошибка при парсинге XML: {e}")
            
    def load_from_file(self, file_path):
        """
        Загружает и парсит XML из файла.
        
        Args:
            file_path: Путь к XML-файлу
            
        Returns:
            dict: Словарь с данными сцены (walls, regions, robot)
            
        Raises:
            XMLValidationError: Если XML некорректен или не соответствует требованиям
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self.parse_xml(f.read())
        except (IOError, FileNotFoundError) as e:
            raise XMLValidationError(f"Ошибка при чтении файла: {e}") 