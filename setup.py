from setuptools import setup, find_packages

setup(
    name="gSceneTS",
    version="0.2.0",
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