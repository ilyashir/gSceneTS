from PyQt6.QtCore import QObject, QPointF, QRectF, QLineF
from PyQt6.QtWidgets import QMessageBox
from ..items import Robot, Wall, Region, StartPosition
from utils.geometry_utils import line_with_thickness_intersects_rect
import logging

logger = logging.getLogger(__name__)

class SceneManager(QObject):
    """
    Менеджер сцены, отвечающий за управление элементами на сцене.
    """
    
    def __init__(self, scene_width=1300, scene_height=800):
        super().__init__()
        self.scene_width = scene_width
        self.scene_height = scene_height
        
        # Списки элементов сцены
        self.walls = []
        self.regions = []
        self.robot = None
        self.start_position = None
        
    def add_wall(self, p1, p2, wall_id=None):
        """
        Добавляет стену на сцену.
        
        Args:
            p1: Начальная точка стены (QPointF)
            p2: Конечная точка стены (QPointF)
            wall_id: Идентификатор стены (опционально)
            
        Returns:
            Wall: Созданная стена или None, если добавление не удалось
        """
        # Создаем временную стену для проверки
        temp_wall = Wall(p1, p2, wall_id=None, is_temp=True)
        
        # Проверяем пересечение с роботом
        if self.robot and self.wall_intersects_robot(p1.x(), p1.y(), p2.x(), p2.y(), thickness=temp_wall.stroke_width):
            logger.warning("Стена пересекается с роботом - отмена добавления")
            return None
            
        # Проверяем границы сцены
        if not self.check_object_within_scene(temp_wall):
            logger.warning("Стена выходит за границы сцены - отмена добавления")
            return None
            
        # Создаем реальную стену
        wall = Wall(p1, p2, wall_id)
        self.walls.append(wall)
        logger.debug(f"Добавлена стена: {wall.id} от {p1} до {p2}")
        
        return wall
        
    def add_region(self, rect_or_points, region_id=None, color=None):
        """
        Добавляет регион на сцену.
        
        Args:
            rect_or_points: QRectF или список точек для региона
            region_id: Идентификатор региона (опционально)
            color: Цвет региона (опционально)
            
        Returns:
            Region: Созданный регион или None, если добавление не удалось
        """
        # Создаем временный регион для проверки
        temp_region = Region(rect_or_points, region_id=None, color=color, is_temp=True)
        temp_region_id = temp_region.id
        
        # Проверяем границы сцены
        if not self.check_object_within_scene(temp_region):
            logger.warning("Регион выходит за границы сцены - отмена добавления")
            Region.cleanup_temp_id(temp_region_id)
            return None
            
        # Создаем реальный регион
        region = Region(rect_or_points, region_id, color)
        self.regions.append(region)
        logger.debug(f"Добавлен регион: {region.id}")
        
        return region
        
    def place_robot(self, position, name="", direction=0):
        """
        Размещает робота на сцене.
        
        Args:
            position: Позиция робота (QPointF)
            name: Имя робота
            direction: Направление робота в градусах
            
        Returns:
            Robot: Объект робота или None, если размещение не удалось
        """
        # Проверяем пересечение со стенами
        if self.robot_intersects_walls(position):
            logger.warning("Робот пересекается со стенами - отмена размещения")
            return None
            
        # Создаем временного робота для проверки границ
        temp_robot = Robot(position, name=name, direction=direction)
        if not self.check_object_within_scene(temp_robot):
            logger.warning("Робот выходит за границы сцены - отмена размещения")
            Robot.reset_instance()
            return None
            
        # Создаем реального робота
        self.robot = Robot(position, name=name, direction=direction)
        logger.debug(f"Робот размещен: pos={position}, name={name}, direction={direction}")
        
        return self.robot
        
    def place_start_position(self, position, direction=0):
        """
        Размещает стартовую позицию на сцене.
        
        Args:
            position: Позиция (QPointF)
            direction: Направление в градусах
            
        Returns:
            StartPosition: Объект стартовой позиции или None, если размещение не удалось
        """
        # Создаем временную стартовую позицию для проверки границ
        temp_start = StartPosition(position, direction)
        if not self.check_object_within_scene(temp_start):
            logger.warning("Стартовая позиция выходит за границы сцены - отмена размещения")
            StartPosition.reset_instance()
            return None
            
        # Создаем реальную стартовую позицию
        self.start_position = StartPosition(position, direction)
        logger.debug(f"Стартовая позиция размещена: pos={position}, direction={direction}")
        
        return self.start_position
        
    def check_object_within_scene(self, item):
        """
        Проверяет, находится ли объект в пределах сцены.
        
        Args:
            item: Объект для проверки
            
        Returns:
            bool: True, если объект в пределах сцены, False в противном случае
        """
        # Проверяем тип объекта и вызываем соответствующую проверку
        if isinstance(item, Wall):
            return self._check_wall_within_scene(item)
        elif isinstance(item, Region):
            return self._check_region_within_scene(item)
        elif isinstance(item, Robot):
            return self._check_robot_within_scene(item)
        elif isinstance(item, StartPosition):
            return self._check_start_position_within_scene(item)
        return False
        
    def _check_wall_within_scene(self, wall):
        """Проверяет, находится ли стена в пределах сцены."""
        line = wall.line()
        return (
            -self.scene_width / 2 <= line.x1() <= self.scene_width / 2 and
            -self.scene_height / 2 <= line.y1() <= self.scene_height / 2 and
            -self.scene_width / 2 <= line.x2() <= self.scene_width / 2 and
            -self.scene_height / 2 <= line.y2() <= self.scene_height / 2
        )
        
    def _check_region_within_scene(self, region):
        """Проверяет, находится ли регион в пределах сцены."""
        rect = region.boundingRect()
        pos = region.pos()
        
        # Проверяем все углы прямоугольника
        points = [
            QPointF(pos.x() + rect.x(), pos.y() + rect.y()),
            QPointF(pos.x() + rect.x() + rect.width(), pos.y() + rect.y()),
            QPointF(pos.x() + rect.x(), pos.y() + rect.y() + rect.height()),
            QPointF(pos.x() + rect.x() + rect.width(), pos.y() + rect.y() + rect.height())
        ]
        
        for point in points:
            if not (-self.scene_width / 2 <= point.x() <= self.scene_width / 2 and
                   -self.scene_height / 2 <= point.y() <= self.scene_height / 2):
                return False
        return True
        
    def _check_robot_within_scene(self, robot):
        """Проверяет, находится ли робот в пределах сцены."""
        pos = robot.pos()
        # Размер робота 50x50 пикселей
        return (
            -self.scene_width / 2 <= pos.x() and pos.x() + 50 <= self.scene_width / 2 and
            -self.scene_height / 2 <= pos.y() and pos.y() + 50 <= self.scene_height / 2
        )
        
    def _check_start_position_within_scene(self, start_pos):
        """Проверяет, находится ли стартовая позиция в пределах сцены."""
        pos = start_pos.pos()
        # Добавляем отступ 25 пикселей для стартовой позиции
        return (
            -self.scene_width / 2 + 25 <= pos.x() <= self.scene_width / 2 - 25 and
            -self.scene_height / 2 + 25 <= pos.y() <= self.scene_height / 2 - 25
        )
        
    def wall_intersects_robot(self, x1, y1, x2, y2, thickness=None):
        """
        Проверяет, пересекается ли стена с роботом.
        
        Args:
            x1, y1: Координаты первой точки стены
            x2, y2: Координаты второй точки стены
            thickness: Толщина стены
            
        Returns:
            bool: True, если стена пересекается с роботом
        """
        if not self.robot:
            return False
            
        # Создаем прямоугольник робота
        robot_rect = QRectF(
            self.robot.pos().x(),
            self.robot.pos().y(),
            50,  # Размер робота 50x50
            50
        )
        
        # Если толщина не указана, используем значение по умолчанию
        if thickness is None:
            thickness = 10  # Стандартная толщина стены
            
        # Проверяем пересечение линии стены с прямоугольником робота
        return line_with_thickness_intersects_rect(
            QLineF(x1, y1, x2, y2),
            robot_rect,
            thickness
        )
        
    def robot_intersects_walls(self, position):
        """
        Проверяет, пересекается ли робот со стенами в указанной позиции.
        
        Args:
            position: Позиция робота (QPointF)
            
        Returns:
            bool: True, если робот пересекается хотя бы с одной стеной
        """
        # Создаем прямоугольник робота
        robot_rect = QRectF(
            position.x(),
            position.y(),
            50,  # Размер робота 50x50
            50
        )
        
        # Проверяем пересечение с каждой стеной
        for wall in self.walls:
            line = wall.line()
            thickness = wall.stroke_width
            
            if line_with_thickness_intersects_rect(line, robot_rect, thickness):
                return True
                
        return False
        
    def clear(self):
        """Очищает все элементы сцены."""
        # Очищаем списки элементов
        self.walls.clear()
        self.regions.clear()
        
        # Сбрасываем робота и стартовую позицию
        if self.robot:
            Robot.reset_instance()
            self.robot = None
            
        if self.start_position:
            StartPosition.reset_instance()
            self.start_position = None
            
        logger.debug("Сцена очищена") 