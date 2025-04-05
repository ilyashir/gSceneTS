# Changelog / История изменений

Все заметные изменения в этом проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.9] - 2025-04-05

### Changed / Изменено
- Improved properties window with more intuitive controls / Улучшено окно свойств с более интуитивными элементами управления
- Refactored properties window UI widgets into separate module for better maintainability / Выделены UI виджеты окна свойств в отдельный модуль для улучшения поддерживаемости
- Migrated tests from pytest to unittest for better integration / Переведены тесты с pytest на unittest для лучшей интеграции
- Fixed Region.set_id method to accept any unique string ID / Исправлен метод Region.set_id для принятия любого уникального строкового ID

## [0.2.5] - 2025-04-02

### Added / Добавлено
- Full XML import/export functionality with validation / Полноценная функциональность импорта/экспорта XML с валидацией
- Created XMLHandler class for XML processing / Создан класс XMLHandler для обработки XML
- Added application menu with File, View, and Help sections / Добавлено меню приложения с разделами Файл, Вид и Помощь
- Added "About" dialog with version information / Добавлен диалог "О программе" с информацией о версии
- Implemented XML file dialog for opening and saving / Реализован диалог выбора файлов XML для открытия и сохранения

### Changed / Изменено
- Improved region geometry handling using paths instead of rectangles / Улучшена обработка геометрии регионов с использованием путей вместо прямоугольников
- Changed region appearance / Изменен внешний вид регионов
- Changed robot rotation to rotate around its center / Изменен поворот робота: теперь он вращается вокруг своего центра
- Redesigned initialization and rendering structure for robot, walls and regions / Переработана структура инициализации и отрисовки для робота, стен и регионов

## [0.2.0] - 2025-03-30

### Added / Добавлено
- UI interaction tests for theme toggle and element dragging / Тесты взаимодействия с интерфейсом для переключения темы и перетаскивания элементов
- Automatic message box handling in tests for improved reliability / Автоматическая обработка диалоговых окон в тестах для повышения надежности
- Centralized fixture for tests in conftest.py / Централизованная фикстура для тестов в conftest.py
- Base functionality with scene editor, robot control, walls and regions / Базовая функциональность с редактором сцены, управлением роботом, стенами и регионами
- XML export and import capabilities / Возможности экспорта и импорта XML

### Changed / Изменено
- Improved UI design with better styles and layout / Улучшенный дизайн интерфейса с лучшими стилями и компоновкой
- Added theme switching capability (light/dark) / Добавлена возможность переключения темы (светлая/темная)
- Enhanced adaptive elements for better responsiveness / Улучшенные адаптивные элементы для лучшей отзывчивости
- Fixed incorrect wall and region tests / Исправлены некорректные тесты стен и регионов

### Fixed / Исправлено
- Fixed issues with duplicated ID handling in walls and regions / Исправлены проблемы с обработкой дублирующихся ID стен и регионов
- Improved test robustness with message box auto-closing / Повышена надежность тестов с автоматическим закрытием диалоговых окон
- Corrected stroke width assertions in wall tests / Исправлены проверки ширины линий в тестах стен

## [0.1.0] - 2025-03-27

### Added / Добавлено
- Initial project setup and architecture / Начальная настройка проекта и архитектура
- Basic graphics scene implementation / Базовая реализация графической сцены
- Robot model with rotation capabilities / Модель робота с возможностью вращения
- Wall creation and editing / Создание и редактирование стен
- Region creation and editing / Создание и редактирование регионов
- Grid and background with coordinate system / Сетка и фон с координатной системой
- Properties window for object editing / Окно свойств для редактирования объектов
- Testing framework implementation / Реализация фреймворка тестирования 