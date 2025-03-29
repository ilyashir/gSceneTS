# Changelog / История изменений

All notable changes to this project will be documented in this file.

Все значимые изменения в проекте будут документироваться в этом файле.

## [0.2.0] - 2024-06-22

### Added
- UI interaction tests for theme toggle and element dragging
- Automatic message box handling in tests for improved reliability
- Centralized fixture for tests in conftest.py
- Base functionality with scene editor, robot control, walls and regions
- XML export and import capabilities

### Changed
- Improved UI design with better styles and layout
- Added theme switching capability (light/dark)
- Enhanced adaptive elements for better responsiveness
- Fixed incorrect wall and region tests

### Fixed
- Fixed issues with duplicated ID handling in walls and regions
- Improved test robustness with message box auto-closing
- Corrected stroke width assertions in wall tests

## [0.1.0] - 2024-05-30

### Added / Добавлено
- Initial project setup and architecture
- Basic graphics scene implementation
- Robot model with rotation capabilities
- Wall creation and editing
- Region creation and editing
- Grid and background with coordinate system
- Properties window for object editing
- Testing framework implementation 