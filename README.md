# TS Scene Generator

Генератор сцен для TRIK Studio, позволяющий создавать и редактировать сцены с помощью графического интерфейса.

## Возможности

- Создание и редактирование стен
- Создание и редактирование регионов
- Размещение и перемещение робота
- Три режима работы:
  - Режим наблюдателя (по умолчанию)
  - Режим рисования
  - Режим редактирования
- Привязка к сетке
- Настройка размеров сцены
- Масштабирование сцены колесиком мыши (с Ctrl) и через панель управления
- Поддержка горячих клавиш для основных операций
- Темный и светлый режимы интерфейса
- Экспорт сцены в XML-формат

## Горячие клавиши

- **F1** — Переключение в режим наблюдателя
- **F2** — Переключение в режим рисования
- **F3** — Переключение в режим редактирования
- **Ctrl+Plus (+)** — Увеличить масштаб
- **Ctrl+Minus (-)** — Уменьшить масштаб
- **Ctrl+0** — Сбросить масштаб до исходного (1:1)
- **Delete** — Удалить выбранный элемент
- **W** — Выбрать инструмент "Стена" (в режиме рисования)
- **R** — Выбрать инструмент "Регион" (в режиме рисования)
- **G** — Сгенерировать XML

## Требования

- Python 3.x
- PyQt6
- Дополнительные зависимости указаны в `requirements.txt`

## Установка

### Способ 1: Установка из репозитория

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ilyashir/gSceneTS
```

2. Перейдите в директорию проекта:
```bash
cd gSceneTS
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Способ 2: Установка как пакет Python

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ilyashir/gSceneTS
```

2. Перейдите в директорию проекта:
```bash
cd gSceneTS
```

3. Установите пакет и все зависимости:
```bash
pip install -e .
```

Это установит пакет в режиме разработки, позволяя вносить изменения в код без необходимости переустановки.

## Использование

### Запуск из репозитория

```bash
python main.py
```

### Запуск установленного пакета

После установки пакета с помощью `pip install -e .` вы можете запускать приложение из любой директории, используя команду:

```bash
gscene
```

### Использование интерфейса

1. Используйте панель инструментов слева для:
   - Переключения режимов работы
   - Выбора типа рисования (стена/регион)
   - Настройки размеров сцены
   - Включения/выключения привязки к сетке

2. Используйте панель свойств справа для:
   - Просмотра и редактирования свойств выбранных объектов
   - Настройки параметров сцены

3. Для сохранения сцены нажмите кнопку "Generate XML" и выберите место сохранения файла.

## Режимы работы

### Режим наблюдателя
- По умолчанию активен при запуске
- Позволяет просматривать сцену
- Кнопки рисования отключены

### Режим рисования
- Активируется кнопкой "Рисование"
- Доступны кнопки для создания стен и регионов
- Позволяет рисовать новые объекты на сцене

### Режим редактирования
- Активируется кнопкой "Редактирование"
- Позволяет перемещать робота
- Позволяет редактировать существующие объекты

## Лицензия

MIT License

Copyright (c) 2025 Ilya Shirokolobov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
