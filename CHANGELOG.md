# Changelog / История изменений

All notable changes to this project will be documented in this file.

Все значимые изменения в проекте будут документироваться в этом файле.

## [0.2.0] - 2024-06-22

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

## [0.1.0] - 2024-05-30

### Added / Добавлено
- Initial project setup and architecture / Начальная настройка проекта и архитектура
- Basic graphics scene implementation / Базовая реализация графической сцены
- Robot model with rotation capabilities / Модель робота с возможностью вращения
- Wall creation and editing / Создание и редактирование стен
- Region creation and editing / Создание и редактирование регионов
- Grid and background with coordinate system / Сетка и фон с координатной системой
- Properties window for object editing / Окно свойств для редактирования объектов
- Testing framework implementation / Реализация фреймворка тестирования 