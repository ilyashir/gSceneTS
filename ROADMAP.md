# Project Roadmap / Дорожная карта проекта

This document outlines the planned development path for the project, including upcoming features, improvements, and fixes.

Этот документ описывает планируемый путь развития проекта, включая предстоящие функции, улучшения и исправления.

## Current Release (v0.4.0) / Текущий релиз

### Features / Функции
- [x] Add robot start position marker as a red cross / Добавить метку старта робота в виде красного крестика
- [ ] Add ability to draw lines on the scene / Добавить возможность рисовать линии на сцене
- [ ] Add option to display regions on top of other objects in edit mode for easier movement / Добавить в режиме редактирования возможность отображать регионы поверх остальных объектов для перемещения
- [ ] Add "Realistic Physics" section with 3 checkpoints / Добавить раздел "Реалистичная физика" с 3мя чекпоинтами
- [ ] Update menu style and add new functionality / Обновить стиль меню и добавить новую функциональность

### Improvements / Улучшения 
- [ ] Refactor codebase for better maintainability / Рефакторинг кодовой базы для улучшения сопровождаемости
- [ ] Enhance error handling throughout the application / Улучшить обработку ошибок во всем приложении
- [ ] Optimize memory usage / Оптимизировать использование памяти
- [ ] Improve the scene rendering system / Улучшить систему рендеринга сцены
- [x] Enhance robot-wall intersection checks with proper wall thickness handling / Улучшить проверку пересечения робота со стенами с учетом толщины стены
- [ ] Align object properties with current TRIK Studio scene tag attributes format / Привести свойства объектов к текущему формату атрибутов тегов сцен TRIK Studio
- [ ] Optimize performance for large scenes / Оптимизировать производительность для больших сцен
- [ ] Implement undo/redo functionality / Реализовать функциональность отмены/повтора действий

### Documentation / Документация
- [ ] Add code documentation / Добавить документацию кода

## Long-term goals (v1.0.0 and beyond) / Долгосрочные цели

### Features / Функции
- [ ] Add ability to create skittles and balls on the scene in drawing mode / Добавить возможность создания кеглей и мячей на сцене в режиме рисования
- [ ] Add ability to generate mazes from walls as object groups / Добавить возможность генерации лабиринтов из стен как группы объектов
- [ ] Add ability to generate fields with lines and intersections as object groups / Добавить возможности генерации полей с линиями и перекрестками как группы объектов
- [ ] Add ports to the robot and ability to install sensors on them / Добавить для робота порты и возможность устанавливать на них датчики

### Documentation / Документация
- [ ] Create comprehensive user manual / Создать подробное руководство пользователя
- [ ] Create tutorials and examples / Создать обучающие материалы и примеры

### Platform / Платформа

## Released Versions / Выпущенные версии

### v0.3.0 (Released) / (Выпущена)

#### Features / Функции
- [x] Implement scene scaling with mouse wheel / Реализовать масштабирование сцены колесиком мыши
- [x] Improve XML import/export with additional validation / Улучшить импорт/экспорт XML с дополнительной валидацией
- [x] Add keyboard shortcuts for common actions / Добавить горячие клавиши для типовых действий
- [x] Add scene constraints validation when changing object parameters in the properties window / Добавить проверку ограничений сцены при изменении параметров объекта в окне свойств
- [x] Add application menu with access to all functions / Добавить меню приложения с доступом ко всем функциям

#### Improvements / Улучшения
- [x] Enhance the properties window with more intuitive controls / Улучшить окно свойств, сделав элементы управления более интуитивными
- [x] Refactor properties window UI widgets into separate module for better maintainability / Выделить UI виджеты окна свойств в отдельный модуль для улучшения поддерживаемости
- [x] Change robot rotation to rotate around its center / Изменить поворот робота: должен вращаться вокруг своего центра
- [x] Style scrollbars with semi-transparent appearance and auto-hide functionality / Стилизовать полосы прокрутки с полупрозрачным видом и функцией автоскрытия

#### Testing / Тестирование
- [x] Add more UI interaction tests / Добавить больше тестов взаимодействия с интерфейсом
- [x] Migrate tests from pytest to unittest for better integration / Перевести тесты с pytest на unittest для лучшей интеграции
- [x] Implement performance benchmarks / Внедрить тесты производительности
- [x] Improve test coverage / Улучшить покрытие кода тестами

## Prioritization and Progress Tracking / Отслеживание приоритетов и прогресса

Progress on these goals will be tracked through GitHub issues and project boards. Items will be prioritized based on:

Прогресс по этим целям будет отслеживаться через GitHub issues и доски проектов. Приоритеты элементов будут определяться на основе:

1. User feedback / Отзывы пользователей
2. Development complexity / Сложность разработки
3. Impact on overall system / Влияние на общую систему
4. Dependencies between features / Зависимости между функциями

## Notes / Примечания

This roadmap is a living document and will be updated as the project evolves and priorities change. Team members and contributors are encouraged to suggest updates and additions to this roadmap.

Эта дорожная карта является живым документом и будет обновляться по мере развития проекта и изменения приоритетов. Членам команды и контрибьюторам рекомендуется предлагать обновления и дополнения к этой дорожной карте.

Last updated: April 2025 / Последнее обновление: Апрель 2025 