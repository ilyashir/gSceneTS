from setuptools import setup, find_packages
import re
import os

# Динамически получаем версию из __init__.py
with open(os.path.join(os.path.dirname(__file__), '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Не удалось найти версию")

setup(
    name="gSceneTS",
    version=version,
    packages=find_packages(),
    
    # Зависимости с указанием версий
    install_requires=[
        "PyQt6>=6.4.0",
        "PyQt6-Qt6>=6.4.0", 
        "PyQt6-sip>=13.4.0",
        "pytest>=7.0.0",
        "pytest-qt==4.2.0",
        "transparent-scrollbar-pyqt>=0.5.0",
    ],
    
    # Дополнительные зависимости, использующие определенный коммит
    dependency_links=[
        "git+https://github.com/ilyashir/transparent-scrollbar-pyqt.git@v0.5.0#subdirectory=transparent_scrollbar_pkg"
    ],
    
    # Если библиотека не найдена, используем локальную копию
    package_data={
        "utils": ["transparent_scrollbar/*.py"],
    },
    
    # Метаданные
    author="ilyashir",
    author_email="ilya.shirokolobov@gmail.com",
    description="Графический редактор сцены для TRIK Studio",
    keywords="graphics, robotics, editor, virtual robot, TRIK Studio",
    python_requires=">=3.8",
    
    # Запускаемый скрипт
    entry_points={
        "console_scripts": [
            "gscene=main:main",
        ],
        "gui_scripts": [
            "gscene-gui=main:main",
        ],
    },
) 