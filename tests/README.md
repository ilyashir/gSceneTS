# Тесты для проекта gSceneTS

В этой директории содержатся тесты для проверки функциональности приложения gSceneTS.

## Структура тестов

- `test_robot.py` - тесты для класса `Robot`
- `test_wall.py` - тесты для класса `Wall`
- `test_region.py` - тесты для класса `Region`
- `test_field_widget.py` - тесты для класса `FieldWidget`
- `test_mouse_events.py` - тесты для обработки событий мыши в приложении
- `conftest.py` - настройки для тестирования с PyQt

## Запуск тестов

Для запуска всех тестов используйте команду:

```bash
python run_tests.py
```

Либо можно запустить pytest напрямую:

```bash
pytest -xvs tests
```

Для запуска конкретного набора тестов:

```bash
pytest -xvs tests/test_robot.py
```

## Отладка тестов

При возникновении проблем при тестировании можно увеличить вербозность вывода:

```bash
pytest -xvs tests --log-cli-level=DEBUG
```

## Требования

Для запуска тестов необходимы следующие библиотеки:
- PyQt6
- pytest

Установка зависимостей:

```bash
pip install -r requirements.txt
``` 